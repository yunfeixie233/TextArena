from enum import Enum
import re, random
from typing import Optional, Dict, Any, List, Tuple

import textarena as ta

class CoupAction(Enum):
    """
    Each of the actions below is annotated with whether it is blockable or not.

    And what card a player claims to have when they make the action.
    """

    Income = "income"
    ForeignAid = "foreign aid"  # -- Blockable, doesn't claim anything
    Coup = "coup"
    Tax = "tax" # -- Blockable, claims Duke
    Assassinate = "assassinate" # -- Blockable, claims Assassin
    Exchange = "exchange" # -- Blockable, claims Ambassador
    Steal = "steal" # -- Blockable, claims Captain

    # Special action for when a player plays an Ambassador on themselves. 
    # This is a bit of a hack to make the game work, but it's not a real action in the game.
    # Tells us which two cards they want to keep after the exchange
    Keep = "keep"


    # Counteractions.
    PASS = "pass"
    BULLSHIT = "bullshit"

    BlockForeignAid = "block foreign aid"

    # Two cards can block a steal
    BlockStealAmbassador = "block steal ambassador"
    BlockStealCaptain = "block steal captain"
    
    BlockAssassinate = "block assassinate"



class CoupEnv(ta.Env):
    """
    A minimal text-based implementation of the Coup card game using textarena.

    Example actions a player might enter:
      - [<action> <target_player_id> ]
      - [PASS]                 -> The player makes an action.
      - [BULLSHIT]             -> The player challenges the last play.
      - [block foreign aid]    -> The player counteracts the last play.
    """


    def __init__(self):
        super().__init__()

    def reset(self, num_players: int, seed: Optional[int] = None) -> None:
        """ Reset the environment for a new Coup game """
        self.state = ta.State(num_players=num_players, min_players=2, max_players=6)

        # Create deck with three of each card
        deck = ["Duke", "Assassin", "Ambassador", "Captain", "Contessa"] * 3
        random.shuffle(deck)

        # Initialize game state
        game_state = {
            "phase": "play",

            "hands": {},  # The cards each player has in their hand
            "pile": [],  # The cards in the pile in the middle
            
            "influences_remaining": {pid: 2 for pid in range(num_players)},  # Each player starts with 2 influence cards
            "coins": {pid: 2 for pid in range(num_players)},  # Each player starts with 2 coins
            "treasury_coins": 50 - 2*num_players, # Max 50 coins in the pot, minus the coins each player starts with

            # CHALLENGE phase specific information
            "last_action": None,  # The last action that was taken
            "last_action_source_player_id": None,  # The player who made the last action
            "last_action_target_player_id": None,  # The target of the last action
            "challenge_phase_next_players": [],  # The players who are next to play IN THIS GAME PHASE
        }

        # Deal two cards to each player
        for player_id in range(num_players):
            game_state["hands"].setdefault(player_id, [])
            game_state["hands"][player_id].append(deck.pop())
            game_state["hands"][player_id].append(deck.pop())

        # Pile has whatever is left in the deck
        game_state["pile"] = deck

        # Initialize textarena state
        self.state.reset(seed=seed, game_state=game_state, player_prompt_function=self._generate_player_prompt)

        # Show each player their initial hand
        self._observer_current_state(broadcast=True)

        # Start with player 0
        self.state.manually_update_current_player(new_player_id=0)
    

    def step(self, action_str: str) -> Tuple[bool, ta.Info]:
        """ Process a single step/action from the current player """
        # Log the player's raw input by sending the action_str to player with id -1
        self.state.add_observation(from_id=self.state.current_player_id, to_id=-1, message=action_str)
        
        # TODO: Do a check that forces a coup if the player has 10 or more coins?

        # Game phase is either in play (a player is doing an initial action like income, foreign aid, etc)
        # or challenge (we are querying one or more players about a potential counteraction)
        if self.state.game_state["phase"] == "play":
            action, action_target_player_id = self._parse_action(action_str)
            self._do_play_phase_step(action, action_target_player_id)
        
        elif self.state.game_state["phase"] == "challenge":
            # counteractions don't have a target player id, when we parse the challenge action we get keep_cards instead
            action, keep_cards = self._parse_action(action_str)
            self._do_challenge_phase_step(action, keep_cards)
        else:
            raise Exception(f"Unexpected game phase: {self.state.game_state['phase']}")

        return self._advance_turn()


        

    def _do_play_phase_step(self, action: CoupAction, action_target_player_id: Optional[int] = None, blockable: bool = True):
        """
        Update the coins and the phase state based on the action.

        @param blockable: if an action is blockable, then we have to go to each player to prompt if they want to block/challenge it
                          if it's not blockable, then that means that no other players have challenged, or a challenge has already been made and failed
        """
        if action == CoupAction.Income:
            self.state.game_state["coins"][self.state.current_player_id] += 1
            self.state.game_state["treasury_coins"] -= 1
        
        elif action == CoupAction.Coup:
            self.state.game_state["coins"][self.state.current_player_id] -= 7
            self.state.game_state["treasury_coins"] += 7
            
            # pop a random card
            if len(self.state.game_state["hands"][action_target_player_id]) > 0:
                self._make_player_lose_a_card(action_target_player_id)
            else:
                reason=f"Invalid move. Can't coup player {action_target_player_id} because have already lost all their cards."
                self.state.set_invalid_move(player_id=self.state.current_player_id, reason=reason)

        elif action in [CoupAction.ForeignAid, CoupAction.Tax, CoupAction.Assassinate, CoupAction.Steal] and blockable:
            # change state to call phase
            self.state.game_state["phase"] = "call"
            self.state.game_state["last_action"] = action
            self.state.game_state["last_action_source_player_id"] = self.state.current_player_id
            self.state.game_state["last_action_target_player_id"] = action_target_player_id
            self.state.game_state["challenge_phase_next_players"] = [action_target_player_id] +\
                [pid for pid in range(self.state.num_players) if pid != self.state.current_player_id and pid != action_target_player_id] + \
                [self.state.current_player_id]
            
        elif action == CoupAction.ForeignAid: # and not blockable (implied from above)
            self.state.game_state["phase"] = "play"
            self.state.game_state["coins"][self.state.current_player_id] += 2
            self.state.game_state["treasury_coins"] -= 2
        
        elif action == CoupAction.Tax: # and not blockable (implied from above)
            self.state.game_state["phase"] = "play"
            self.state.game_state["coins"][self.state.current_player_id] += 3
            self.state.game_state["treasury_coins"] -= 3
        
        elif action == CoupAction.Assassinate: # and not blockable (implied from above)
            self.state.game_state["phase"] = "play"
            self.state.game_state["coins"][self.state.current_player_id] -= 3
            self.state.game_state["treasury_coins"] += 3

            # The player that was assassinated loses a card
            self._make_player_lose_a_card(action_target_player_id)
        
        elif action == CoupAction.Steal: # and not blockable (implied from above)
            self.state.game_state["phase"] = "play"
            self.state.game_state["coins"][self.state.current_player_id] += 2
            self.state.game_state["treasury_coins"] -= 2
        
        elif action == CoupAction.Exchange:
            # change state to challenge phase
            self.state.game_state["phase"] = "challenge"
            self.state.game_state["last_action"] = action
            self.state.game_state["last_action_source_player_id"] = self.state.current_player_id
            self.state.game_state["last_action_target_player_id"] = self.state.target_player_id
            self.state.game_state["challenge_phase_next_players"] = [pid for pid in range(self.state.num_players) if pid != self.state.current_player_id] + [self.state.target_player_id]



    def _do_challenge_phase_step(self, action: CoupAction, keep_cards: Optional[List[str]] = None):
        # If the player passes (they don't want to challenge), then we don't need to do anything, just advance (this is handled in step())
        if action == CoupAction.PASS:
            return
        

        if action == CoupAction.BULLSHIT:
            # the "challenged" player is the player who initially played the challenged card
            challenged_card = self._action_to_card(self.state.game_state["last_action"])
            challenged_player_id = self.state.game_state["last_action_source_player_id"]
            is_honest = self.state.game_state["hands"][challenged_player_id].count(challenged_card) > 0
            
            # This needs to be set before the _do_play_phase_step call below because it uses the current player id
            self.state.current_player_id = challenged_player_id
            
            if is_honest:
                # If player was honest, then he gets a new card from the pile
                self.state.game_state["hands"][challenged_player_id].append(self.state.game_state["pile"].pop())

                # Put back the newly revealed card
                self.state.game_state["pile"].append(challenged_card)
                random.shuffle(self.state.game_state["pile"])

                # Player who called bullshit loses a card
                self._make_player_lose_a_card(self.state.current_player_id)
                
                # Actually do the action that was challenged, now that the challenge is over
                # We do this by skipping the action to the challenged player, the person who initially played the challenged card                
                self._do_play_phase_step(self.state.game_state["last_action"], self.state.game_state["last_action_target_player_id"], blockable=False)
            else:
                # Player who got challenged loses a card, nothing else changes
                self._make_player_lose_a_card(challenged_player_id)

        elif action == CoupAction.Keep:

            pass
        else:
            # TODO: add ability for players' blocks to be challenged. Right now we just assume the block is instantly challenged and revealed.
            #       I think the way to do this would be to maintain the action that was blocked, and then when the challenged player answers,
            #       we check if they have the card that was blocked.
            #       We also need to make sure that the challenged player is not the player who made the block.
            if action in {CoupAction.BlockForeignAid, CoupAction.BlockStealAmbassador, CoupAction.BlockStealCaptain, CoupAction.BlockAssassinate}:
                blocking_card = self._action_to_card(action)
                is_honest = self.state.game_state["hands"][self.state.current_player_id].count(blocking_card) > 0
                if not is_honest:
                    # If the player claiming to block the foreign aid (current_player_id) is dishonest, then they lose a card, and the foreign aid action is done
                    self._make_player_lose_a_card(self.state.current_player_id)

                    self.state.current_player_id = self.state.game_state["last_action_source_player_id"]
                    self._do_play_phase_step(CoupAction.ForeignAid, self.state.game_state["last_action_target_player_id"], blockable=False)



    # ---------------------------------------------------------------------
    # PROMPT GENERATION METHODS -- CONVERTS GAME STATE TO PROMPT
    # ---------------------------------------------------------------------
    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
            """ Provide a quick summary / instructions for each player at game start """

            with open("./base_coup_prompt.txt", "r") as f:
                prompt = f.read()
            
            ############################################################
            # Fill in turn-specific information
            ############################################################

            # Fill in the player's id
            prompt = prompt.replace("<PLAYER_ID>", str(player_id))

            # Player observations:
            prompt = prompt.replace("<PLAYER_OBSERVATIONS>", self._make_player_observations_prompt(player_id, game_state))

            # Call to action or challenge:
            prompt = prompt.replace("<CALL_TO_ACTION_OR_CHALLENGE>", self._make_call_to_action_or_challenge_prompt(player_id, game_state))


            return prompt
    

    def _make_player_observations_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """
        Make a prompt for a given player_id who's turn it is. This tells them their hand and the state of the game.
        """
        # TODO: I don't know how observations are supposed to work. I'd guess it's something like this:
        #       Whatever comes out of this goes into the <PLAYER_OBSERVATIONS> section of the base prompt.
        #
        # Player X has 1 influence card remaining, and is showing a Duke card.
        # Player Y has 2 coins, and is showing a Captain card.
        # Player Z has 3 coins, and is showing an Ambassador card.
        # The pot has 10 coins remaining.

        # Player X's hand is [Duke, Duke]
        # Player Y's hand is [Captain, Captain]
        # Player Z's hand is [Ambassador, Ambassador]

        # There are X cards remaining in the pile

        # You have Y influence cards remaining, a Duke and a Captain
        
        pass


    def _make_call_to_action_or_challenge_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """ 
        Make a prompt for the player that asks them to make an action or challenge 
        
        If the game is in the play phase, the player is asked to make an action.
        If the game is in the challenge phase, the player is asked to make a counteraction (block, bullshit, or pass).
        """

        if game_state["phase"] == "play":
            return "It is your turn. What action do you want to take?"
        
        elif game_state["phase"] == "challenge":
            # Special case for Exchange where a player plays an Ambassador "on themselves"
            if game_state["last_action"] == CoupAction.Exchange and game_state["last_action_target_player_id"] == player_id:
                return f"It is your turn. You just played an Ambassador. You now have these four cards in your hand: {', '.join(game_state['hands'][player_id])}." +\
                       f"Which two cards do you want to keep?"
            elif game_state["last_action_target_player_id"] == player_id:
                # Only two blockable actions are Steal and Assassinate
                block_options_str = "[block steal captain], [block steal ambassador]" if game_state['last_action'] == CoupAction.Steal else "[block assassinate]"
                return f"It is Player #{game_state['last_action_source_player_id']}'s turn and they played {game_state['last_action'].value()} on you" +\
                        f"{self._action_to_card_str(game_state['last_action'])} Do you want to {block_options_str}, challenge [BULLSHIT] or [PASS]?"
            else:
                return f"It is Player #{game_state['last_action_source_player_id']}'s turn and they played {game_state['last_action'].value()}," +\
                       f"{self._action_to_card(game_state['last_action'])} Do you want to challenge [BULLSHIT] or [PASS]?"
        else:
            raise Exception(f"Unexpected game phase: {game_state['phase']}")

    def _action_to_card_str(self, action: CoupAction) -> str:
        """ Convert a CoupAction to a card """
        if action == CoupAction.Income or action == CoupAction.ForeignAid:
            return "." # These don't require a claim, end sentence
        elif action == CoupAction.Tax:
            return ", claiming to have a Duke card."
        elif action == CoupAction.Assassinate:
            return ", claiming to have an Assassin card."
        elif action == CoupAction.Steal:
            return ", claiming to have a Captain card."
        elif action == CoupAction.Exchange:
            return ", claiming to have an Ambassador card."
        else:
            raise Exception(f"Unexpected action: {action}")
    
    def _action_to_card(self, action: CoupAction) -> str:
        """ Convert a CoupAction to a card """
        
        if action == CoupAction.Tax:
            return "Duke"
        elif action == CoupAction.Assassinate:
            return "Assassin"
        elif action == CoupAction.Steal:
            return "Captain"
        elif action == CoupAction.Exchange:
            return "Ambassador"
        
        elif action == CoupAction.BlockAssassinate:
            return "Contessa"
        elif action == CoupAction.BlockStealCaptain:
            return "Captain"
        elif action == CoupAction.BlockStealAmbassador:
            return "Ambassador"
        elif action == CoupAction.BlockForeignAid:
            return "Duke"
        
        else:
            return "."

    # ---------------------------------------------------------------------
    # GAME STATE ADJUSTMENT METHODS -- SYNTACTIC SUGAR FOR THE GAME LOGIC
    # ---------------------------------------------------------------------

    def _make_player_lose_a_card(self, player_id: int):
        """
        In a perfect world, the player would pick which card they want to lose.
        But for now, we'll just pop the last card in their hand.
        """
        self.state.game_state["hands"][player_id].pop()

    def _advance_turn(self):
        """
        Advance the state to the next direct player.
        """
        if self.state.game_state["phase"] == "play":
            # Always reset the challenge phase info if we're doing a play phase just in case
            self._reset_challenge_phase_info()

            # Move on to next player
            current_pid = self.state.current_player_id
            next_pid = (current_pid + 1) % self.state.num_players
            
        elif self.state.game_state["phase"] == "challenge":
            if len(self.state.game_state["challenge_phase_next_players"]) > 0:
                next_pid = self.state.game_state["challenge_phase_next_players"].pop(0)
            else:
                # If there are no more players to challenge, set the last action source player's next player as the next, reset the challenge phase info
                original_pid = self.state.game_state["last_action_source_player_id"]
                next_pid = (original_pid + 1) % self.state.num_players
                self._reset_challenge_phase_info()

        else:
            raise Exception(f"Unexpected game phase: {self.state.game_state['phase']}")
        
        self.state.manually_update_current_player(new_player_id=next_pid)
        winner = self._get_winner()
        if winner is not None:
            return True, ta.Info(message=f"Player {winner} has won the game!")
        else:
            return False, ta.Info(message="") # TODO: Add info?

    def _reset_challenge_phase_info(self):
        # Resets the `challenge` phase specific information at each play phase
        self.state.game_state["last_action"] = None
        self.state.game_state["last_action_source_player_id"] = None
        self.state.game_state["last_action_target_player_id"] = None
        self.state.game_state["challenge_phase_next_players"] = []

    def _get_winner(self) -> Optional[int]:
        """
        Check if the game is over. Return winning player id if so, otherwise return None.
        """
        remaining_players = [pid for pid in range(self.state.num_players) if len(self.state.game_state["hands"][pid]) > 0]
        if len(remaining_players) == 1:
            return remaining_players[0]
        else:
            return None


    # ---------------------------------------------------------------------
    # PARSE ACTIONS -- JUST BOILERPLATE CODE NOTHING INTERESTING BELOW HERE
    # ---------------------------------------------------------------------

    def _parse_action(self, action_str: str) -> Tuple[CoupAction, Optional[int]]:
        """
        Convert an action string (e.g. 'income','foreign aid','coup','assassinate','steal','exchange') to CoupAction enum.
        Return None if invalid.
        """
        ## TODO: some fancy regex here to parse the action and target player id
        action_str = action_str.lower()
        
        if action_str == "income":
            return CoupAction.Income, None
        elif action_str == "foreign aid":
            return CoupAction.ForeignAid, None
        elif action_str == "coup":
            return CoupAction.Coup, # TODO: add target player id
        elif action_str == "assassinate":
            return CoupAction.Assassinate, # TODO: add target player id
        elif action_str == "steal":
            return CoupAction.Steal, # TODO: add target player id
        elif action_str == "exchange":
            return CoupAction.Exchange, None
        

        elif action_str == "keep":
            return CoupAction.Keep, [] # TODO: parse keep cards
        
        elif action_str == "block steal captain":
            return CoupAction.BlockStealCaptain, None
        elif action_str == "block assassinate ambassador":
            return CoupAction.BlockAssassinateAmbassador, None
        elif action_str == "block foreign aid":
            return CoupAction.BlockForeignAid, None
        elif action_str == "block assassinate":
            return CoupAction.BlockAssassinate, None
        
        elif action_str == "bullshit":
            return CoupAction.BULLSHIT, None
        elif action_str == "pass":
            return CoupAction.PASS, None
        else:
            print(f"Unrecognized action: {action_str}")
            self.state.error_count += 1
            return None