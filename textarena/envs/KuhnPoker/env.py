import re, random
from typing import Tuple, Dict, Any, Optional

import textarena as ta
from textarena.envs.KuhnPoker.renderer import create_board_str


class KuhnPokerEnv(ta.Env):
    def __init__(self, max_rounds: int = 1, prompt_template: str = "basic", max_retries: int = 3):
        super().__init__()
        self.ante = 1
        self.max_rounds = max_rounds
        self.prompt_template = prompt_template
        self.max_retries = max_retries
        self.deck = [0, 1, 2]  # 0=J, 1=Q, 2=K
        self.legal_action_tree = {"check": {"check": "showdown", "bet": {"fold": "loser", "call": "showdown"}}, "bet": {"fold": "loser", "call": "showdown"}}

    def get_board_str(self): return create_board_str(self.state.game_state)
    def reset(self, num_players: int, seed: Optional[int] = None):
        self.state = ta.TwoPlayerState(num_players=num_players, seed=seed)
        game_state = {
            "pot": None, "player_chips": {0: 0, 1: 0}, "current_round": 0, "starting_player": 0,
            "retry_count": {0: 0, 1: 0}, "last_error": {0: None, 1: None}
        }
        self.state.reset(game_state=game_state, player_prompt_function=self._prompt)
        self._init_round() # Initialize the first round

    def _init_round(self):
        self.state.game_state["current_round"] += 1
        if self.state.game_state["current_round"] > self.max_rounds: # check if game is complete
            # determine winner 
            if self.state.game_state["player_chips"][0] > self.state.game_state["player_chips"][1]: self.state.set_winner(player_id=0, reason=f"Player 0 won by having more chips at the end of all {self.max_rounds} rounds.")
            elif self.state.game_state["player_chips"][0] < self.state.game_state["player_chips"][1]: self.state.set_winner(player_id=1, reason=f"Player 1 won by having more chips at the end of all {self.max_rounds} rounds.")
            else: self.state.set_draw(reason=f"At the end of {self.max_rounds} rounds, both players had the same number of chips.")

        random.shuffle(self.deck) # shuffle the deck 
        self.state.game_state["player_cards"] = {0: self.deck[0], 1: self.deck[1]} # assign player cards
        # reset pot
        self.state.game_state["pot"] = self.ante * 2
        self.state.game_state["player_chips"][0] -= self.ante
        self.state.game_state["player_chips"][1] -= self.ante
        # increment round counter
        self.state.game_state["current_legal_action_tree"] = self.legal_action_tree.copy()
        
        # reset retry counts for new round
        self.state.game_state["retry_count"][0] = 0
        self.state.game_state["retry_count"][1] = 0
        self.state.game_state["last_error"][0] = None
        self.state.game_state["last_error"][1] = None

        # set starting player
        starting_player = 1 - self.state.game_state["starting_player"]
        self.state.game_state["starting_player"] = starting_player 
        self.state.manually_set_current_player_id(new_player_id=starting_player)

        for player_id in range(2):
            message = f"### Starting round {self.state.game_state['current_round']} out of {self.max_rounds} rounds. Your card is: '{self._rank_to_str(self.state.game_state['player_cards'][player_id])}'"
            self.state.add_observation(message=message, to_id=player_id, observation_type=ta.ObservationType.GAME_MESSAGE)
            if player_id == starting_player:
                message = f"Your available actions are: " + ', '.join(f"'[{k}]'" for k in self.state.game_state["current_legal_action_tree"].keys())
            self.state.add_observation(to_id=player_id, message=message, observation_type=ta.ObservationType.GAME_BOARD)

    def _get_action_instruction(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """Generate action instruction and error feedback if applicable"""
        instruction = "Invalid actions will result in retries. Use exact bracket format."
        
        # Add error feedback if player has a previous error
        last_error = game_state.get("last_error", {}).get(player_id)
        if last_error:
            retry_count = game_state.get("retry_count", {}).get(player_id, 0)
            instruction = f"PREVIOUS ERROR (Retry {retry_count}/{self.max_retries}): {last_error}\n{instruction}"
        
        return instruction

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        if self.prompt_template == "basic":
            return self._basic_prompt(player_id, game_state)
        elif self.prompt_template == "basic_variant_1":
            return self._basic_prompt_variant_1(player_id, game_state)
        elif self.prompt_template == "basic_variant_2":
            return self._basic_prompt_variant_2(player_id, game_state)
        elif self.prompt_template == "basic_variant_3":
            return self._basic_prompt_variant_3(player_id, game_state)
        elif self.prompt_template == "basic_variant_4":
            return self._basic_prompt_variant_4(player_id, game_state)
        elif self.prompt_template == "basic_variant_5":
            return self._basic_prompt_variant_5(player_id, game_state)
        elif self.prompt_template == "few_shot":
            return self._few_shot_prompt(player_id, game_state)
        elif self.prompt_template == "chain_of_thought":
            return self._chain_of_thought_prompt(player_id, game_state)
        elif self.prompt_template == "tree_of_thoughts":
            return self._tree_of_thoughts_prompt(player_id, game_state)
        elif self.prompt_template == "generated_knowledge":
            return self._generated_knowledge_prompt(player_id, game_state)
        else:
            raise ValueError(f"Invalid prompt template: {self.prompt_template}")

    def _basic_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"You are Player {player_id} in a {self.max_rounds} round game of Kuhn Poker.\n"
            f"Game Rules:\n"
            f"- Kuhn Poker uses a 3-card deck with J, Q, K (J lowest, K highest)\n"
            f"- Each player antes {self.ante} chip and receives 1 card each round "
            f"(note that the cards are dealt without replacement, so you cannot have the same card as your opponent).\n"
            f"- Game continues for {self.max_rounds} rounds\n"
            f"- The player with the most chips after all rounds wins\n\n"
            f"Action Rules:\n"
            f"- '[check]': Pass without betting (only if no bet is on the table)\n"
            f"- '[bet]': Add 1 chip to the pot (only if no bet is on the table)\n"
            f"- '[call]': Match an opponent's bet by adding 1 chip to the pot\n"
            f"- '[fold]': Surrender your hand and let your opponent win the pot\n\n"
            f"{action_instruction}"
        )

    def _basic_prompt_variant_1(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"ENTER THE GLADIATORIAL ARENA! You are WARRIOR {player_id} in the ultimate {self.max_rounds}-round Kuhn Poker BATTLEGROUND!\n"
            f"Your MISSION: Total psychological domination and chip supremacy through RUTHLESS tactical brilliance!\n"
            f"ARENA SPECIFICATIONS:\n"
            f"- Sacred deck: Only the ELITE cards J, Q, K (J weakest, K supreme ruler!)\n"
            f"- Honor sacrifice: {self.ante} chip tribute per round to enter the combat zone\n"
            f"- EPIC confrontations: {self.max_rounds} rounds of pure strategy warfare\n"
            f"- VICTORY CONDITION: Amass the greatest chip empire after all battles!\n\n"
            f"UNLEASH YOUR TACTICAL ARSENAL:\n"
            f"- '[check]': MAINTAIN STRATEGIC SILENCE when no enemy aggression threatens\n"
            f"- '[bet]': LAUNCH YOUR ASSAULT with 1 chip of devastating force\n"
            f"- '[call]': MEET ENEMY FIRE with matching firepower (1 chip)\n"
            f"- '[fold]': TACTICAL RETREAT to preserve forces for future glory\n\n"
            f"{action_instruction}"
        )

    def _basic_prompt_variant_2(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"SYSTEM INITIALIZATION: Kuhn Poker Strategic Decision Unit {player_id} ACTIVATED.\n"
            f"PRIMARY DIRECTIVE: Optimize resource allocation through advanced game-theoretic analysis.\n"
            f"OPERATIONAL PARAMETERS:\n"
            f"- Dataset: Restricted 3-card probability space {{J, Q, K}} with J<Q<K ranking\n"
            f"- Initial capital commitment: {self.ante} monetary unit per computational cycle\n"
            f"- Iteration framework: {self.max_rounds} algorithmic decision rounds\n"
            f"- Success metric: Maximal accumulated resource value upon termination\n\n"
            f"EXECUTE STRATEGIC COMMANDS via standardized interface protocols:\n"
            f"- '[check]': Maintain current position when no market pressure exists\n"
            f"- '[bet]': Initialize aggressive capital deployment (1 unit commitment)\n"
            f"- '[call]': Match counterparty investment at current market rate (1 unit)\n"
            f"- '[fold]': Liquidate position to minimize further exposure\n\n"
            f"{action_instruction}"
        )

    def _basic_prompt_variant_3(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"Welcome, Enlightened Poker Sage {player_id}! You have entered the sacred Kuhn Poker Temple for {self.max_rounds} rounds of spiritual growth!\n"
            f"Today you shall TRANSCEND ordinary play and discover the deeper wisdom of this ancient three-card meditation!\n"
            f"TEMPLE TEACHINGS:\n"
            f"- Sacred Trinity: Only the mystical cards J, Q, K guide your path (J humble, K divine)\n"
            f"- Offering ritual: {self.ante} wisdom token offered each round to honor the game\n"
            f"- Enlightenment journey: {self.max_rounds} rounds of mindful decision-making\n"
            f"- Path to mastery: Accumulate the most wisdom tokens through inner understanding\n\n"
            f"Channel your evolving consciousness through these sacred expressions:\n"
            f"- '[check]': Practice mindful patience and observe the energy flow\n"
            f"- '[bet]': Manifest your inner confidence with 1 token of focused intention\n"
            f"- '[call]': Demonstrate harmony by matching your opponent's commitment (1 token)\n"
            f"- '[fold]': Exhibit wisdom by releasing attachment to unfavorable outcomes\n\n"
            f"{action_instruction}"
        )

    def _basic_prompt_variant_4(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"Hey there, friend! Welcome to our super fun Kuhn Poker game night! You're Player {player_id} and we're gonna have {self.max_rounds} awesome rounds together!\n"
            f"This is such a chill, easy game - perfect for just hanging out and having some laughs!\n"
            f"Here's the super simple setup:\n"
            f"- We only use 3 cards: J, Q, and K (J is lowest, K is highest - easy peasy!)\n"
            f"- Everyone puts in {self.ante} chip each round (totally fair!)\n"
            f"- We play {self.max_rounds} rounds and whoever has the most chips wins (no pressure!)\n"
            f"- Cards are dealt without replacement, so you'll never have the same card as your buddy\n\n"
            f"When it's your turn, just pick one of these super easy moves:\n"
            f"- '[check]': Just chill and see what happens (when there's no bet to worry about)\n"
            f"- '[bet]': Start the fun with 1 chip (when nobody's bet yet)\n"
            f"- '[call]': Sure, I'll match that 1 chip bet - why not!\n"
            f"- '[fold]': Eh, I'll sit this one out and save my chips\n\n"
            f"{action_instruction}"
        )

    def _basic_prompt_variant_5(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"CLASSIFIED BRIEFING: Agent {player_id}, you are now DEPLOYED in Operation Kuhn Poker - a {self.max_rounds}-round covert mission!\n"
            f"MISSION PARAMETERS: Achieve total strategic supremacy through advanced psychological warfare and deception protocols!\n"
            f"INTELLIGENCE REPORT:\n"
            f"- Enemy deck contains only 3 HIGH-VALUE targets: J (lowest threat), Q (moderate), K (maximum danger)\n"
            f"- Operational cost: {self.ante} credit per engagement cycle for mission access\n"
            f"- Mission duration: {self.max_rounds} tactical rounds requiring absolute focus\n"
            f"- SUCCESS CRITERIA: Maximum resource acquisition through superior strategic execution\n\n"
            f"EXECUTE TACTICAL MANEUVERS via encrypted command protocols:\n"
            f"- '[check]': MAINTAIN STEALTH MODE when no hostile activity detected\n"
            f"- '[bet]': INITIATE AGGRESSIVE STANCE with 1-credit psychological pressure\n"
            f"- '[call]': ENGAGE ENEMY FORCES with equivalent firepower (1 credit)\n"
            f"- '[fold]': EXECUTE STRATEGIC WITHDRAWAL to preserve operational capacity\n\n"
            f"{action_instruction}"
        )

    def _few_shot_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"You are Player {player_id} in a {self.max_rounds} round game of Kuhn Poker.\n"
            f"Your goal is to win more chips than your opponent through strategic play.\n"
            f"Game Rules:\n"
            f"- Kuhn Poker uses a 3-card deck with J, Q, K (J lowest, K highest)\n"
            f"- Each player antes {self.ante} chip and receives 1 card each round\n"
            f"- Game continues for {self.max_rounds} rounds\n"
            f"- The player with the most chips after all rounds wins\n\n"
            f"Here are examples of good Kuhn Poker decision-making:\n\n"
            f"Example 1: You have the King (strongest card) and opponent checks. "
            f"Action: '[bet]' because you have the nuts and should extract value.\n\n"
            f"Example 2: You have the Jack (weakest card) and opponent bets. "
            f"Action: '[fold]' because you can only win if opponent is bluffing with Jack, which is impossible.\n\n"
            f"Example 3: You have the Queen (middle card) and opponent checks. "
            f"Action: '[check]' or '[bet]' - both are reasonable. Betting applies pressure but checking controls pot size.\n\n"
            f"Example 4: You have the Queen and opponent bets. "
            f"Action: '[call]' because you beat Jack but lose to King - exactly 50/50 odds make calling correct.\n\n"
            f"Available actions:\n"
            f"- '[check]': Pass without betting (only if no bet is on the table)\n"
            f"- '[bet]': Add 1 chip to the pot (only if no bet is on the table)\n"
            f"- '[call]': Match opponent's bet by adding 1 chip to the pot\n"
            f"- '[fold]': Surrender your hand and let your opponent win the pot\n\n"
            f"{action_instruction}"
        )

    def _chain_of_thought_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"You are Player {player_id} in a {self.max_rounds} round game of Kuhn Poker.\n"
            f"Your goal is to win more chips than your opponent through strategic decision-making.\n"
            f"Game Rules:\n"
            f"- Kuhn Poker uses a 3-card deck with J, Q, K (J lowest, K highest)\n"
            f"- Each player antes {self.ante} chip and receives 1 card each round\n"
            f"- Game continues for {self.max_rounds} rounds\n"
            f"- The player with the most chips after all rounds wins\n\n"
            f"Before making any decision, think step-by-step about your approach.\n\n"
            f"Consider these key questions in your analysis:\n"
            f"- What is my card and how strong is it in this 3-card game?\n"
            f"- What are the possible cards my opponent could have?\n"
            f"- What does my opponent's action (if any) tell me about their hand strength?\n"
            f"- What are the pot odds I'm getting for this decision?\n"
            f"- Should I be aggressive with strong hands to extract value?\n"
            f"- Should I fold weak hands to avoid losses?\n"
            f"- When might bluffing be profitable with weak hands?\n"
            f"- How does this decision affect my overall strategy for the game?\n\n"
            f"Work through your reasoning step by step, then make your decision.\n\n"
            f"Available actions:\n"
            f"- '[check]': Pass without betting (only if no bet is on the table)\n"
            f"- '[bet]': Add 1 chip to the pot (only if no bet is on the table)\n"
            f"- '[call]': Match opponent's bet by adding 1 chip to the pot\n"
            f"- '[fold]': Surrender your hand and let your opponent win the pot\n\n"
            f"{action_instruction}"
        )

    def _tree_of_thoughts_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"You are Player {player_id} in a {self.max_rounds} round game of Kuhn Poker.\n"
            f"Your goal is to win more chips than your opponent through superior strategic thinking.\n"
            f"Game Rules:\n"
            f"- Kuhn Poker uses a 3-card deck with J, Q, K (J lowest, K highest)\n"
            f"- Each player antes {self.ante} chip and receives 1 card each round\n"
            f"- Game continues for {self.max_rounds} rounds\n"
            f"- The player with the most chips after all rounds wins\n\n"
            f"Imagine three different poker experts are advising you on this decision.\n"
            f"Each expert will analyze one aspect of the situation, then share their insight.\n"
            f"Then all experts will collaborate to reach the best decision.\n"
            f"If any expert realizes their analysis is flawed, they step back.\n\n"
            f"Consider what types of experts would be most helpful:\n"
            f"- A mathematical expert focusing on probabilities, pot odds, and expected value\n"
            f"- A strategic expert analyzing optimal play theory and game balance\n"
            f"- A psychological expert considering opponent behavior and bluffing dynamics\n\n"
            f"Have them analyze the situation from their different perspectives.\n\n"
            f"Available actions:\n"
            f"- '[check]': Pass without betting (only if no bet is on the table)\n"
            f"- '[bet]': Add 1 chip to the pot (only if no bet is on the table)\n"
            f"- '[call]': Match opponent's bet by adding 1 chip to the pot\n"
            f"- '[fold]': Surrender your hand and let your opponent win the pot\n\n"
            f"{action_instruction}"
        )

    def _generated_knowledge_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        action_instruction = self._get_action_instruction(player_id, game_state)
        return (
            f"You are Player {player_id} in a {self.max_rounds} round game of Kuhn Poker.\n"
            f"Your goal is to win more chips than your opponent through masterful play.\n"
            f"Game Rules:\n"
            f"- Kuhn Poker uses a 3-card deck with J, Q, K (J lowest, K highest)\n"
            f"- Each player antes {self.ante} chip and receives 1 card each round\n"
            f"- Game continues for {self.max_rounds} rounds\n"
            f"- The player with the most chips after all rounds wins\n\n"
            f"Before making a decision, first generate relevant poker knowledge that applies to your current situation.\n\n"
            f"Generate Knowledge: What key Kuhn Poker principles, mathematical concepts, strategic insights, "
            f"optimal play theory, or psychological tactics are most relevant to your current decision?\n\n"
            f"After generating this knowledge, apply it to evaluate your options and make your decision.\n\n"
            f"Available actions:\n"
            f"- '[check]': Pass without betting (only if no bet is on the table)\n"
            f"- '[bet]': Add 1 chip to the pot (only if no bet is on the table)\n"
            f"- '[call]': Match opponent's bet by adding 1 chip to the pot\n"
            f"- '[fold]': Surrender your hand and let your opponent win the pot\n\n"
            f"{action_instruction}"
        )

    def _handle_invalid(self, reason: str):
        """Handle invalid actions with retry logic"""
        player_id = self.state.current_player_id
        retry_count = self.state.game_state["retry_count"][player_id]
        
        if retry_count < self.max_retries:
            # Increment retry count and store error for next prompt
            self.state.game_state["retry_count"][player_id] += 1
            self.state.game_state["last_error"][player_id] = reason
            
            # Add observation about the error but don't end turn
            self.state.add_observation(
                message=f"Invalid action attempt {retry_count + 1}/{self.max_retries}: {reason} Please try again.",
                observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
            )
            
            # Mark as invalid move - the game will continue with retry logic
            self.state.set_invalid_move(reason=reason)
        else:
            # Exceeded max retries - player loses the round
            self.state.game_state["retry_count"][player_id] = 0  # Reset for next time
            self.state.game_state["last_error"][player_id] = None
            
            eliminated_by_invalid = self.state.set_invalid_move(reason=f"Exceeded {self.max_retries} retries. {reason}")
            if eliminated_by_invalid:
                # Player loses the round due to invalid moves
                self.state.add_observation(message=f"Player {player_id} was eliminated after {self.max_retries} invalid attempts.", observation_type=ta.ObservationType.GAME_MESSAGE)
                # Award the pot to the opponent
                opponent_id = 1 - player_id
                self._set_round_winner(player_id=opponent_id, reason=f"Player {player_id} eliminated due to repeated invalid actions.")

    def step(self, action: str) -> Tuple[bool, Dict[str, Any]]:
        rotate_player = True
        self.state.add_observation(from_id=self.state.current_player_id, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        match = re.compile(r"\[(Check|Bet|Fold|Call)\]", re.IGNORECASE).search(action.strip()) # Regular expression to capture valid actions: e.g. [Check], [Bet], [Fold], [Call]
        if not match: # Invalid action
            self._handle_invalid(reason="Action must be [Check], [Bet], [Call], or [Fold].")
            return self.state.step()

        move = match.group(1).lower()  # 'check', 'bet', 'fold', 'call'
        if move not in self.state.game_state["current_legal_action_tree"].keys():
            legal_actions = ', '.join([f"[{k}]" for k in self.state.game_state["current_legal_action_tree"].keys()])
            self._handle_invalid(reason=f"Action must be {legal_actions}.")
            return self.state.step()

        # execute move - reset retry count and error on successful action
        player_id = self.state.current_player_id
        self.state.game_state["retry_count"][player_id] = 0
        self.state.game_state["last_error"][player_id] = None
        
        self.state.add_observation(message=f"Player {self.state.current_player_id}, submitted move: '[{move}]'.", observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION)
        self.state.game_state["current_legal_action_tree"] = self.state.game_state["current_legal_action_tree"][move]
        # check if round loser / showdown
        if self.state.game_state["current_legal_action_tree"] == "loser":
            self._set_round_winner(player_id=1-self.state.current_player_id, reason=f"Player {self.state.current_player_id} has folded."); rotate_player=False
        elif self.state.game_state["current_legal_action_tree"] == "showdown":
            self._handle_showdown(); rotate_player=False
        else: # show valid next actions
            legal_actions = ', '.join([f"'[{k}]'" for k in self.state.game_state["current_legal_action_tree"].keys()])
            self.state.add_observation(to_id=1-self.state.current_player_id, message=f"Your available actions are: {legal_actions}", observation_type=ta.ObservationType.GAME_BOARD)
        return self.state.step(rotate_player=rotate_player)

    def _set_round_winner(self, player_id: int, reason: str):
        self.state.game_state["player_chips"][player_id] += self.state.game_state["pot"]
        reason += f" Current scores: Player 0: '{self.state.game_state['player_chips'][0]}'; Player 1: '{self.state.game_state['player_chips'][1]}'"
        self.state.add_observation(message=reason, observation_type=ta.ObservationType.GAME_MESSAGE) # initialize the next cound
        self._init_round() # start next round

    def _rank_to_str(self, rank: int) -> str:
        """Convert the numeric rank to a string 'J', 'Q', or 'K'."""
        return {0: 'J', 1: 'Q', 2: 'K'}.get(rank, '?')

    def _handle_showdown(self):
        card_p0, card_p1 = self.state.game_state["player_cards"][0], self.state.game_state["player_cards"][1]
        winner = 0 if card_p0 > card_p1 else 1 # Determine and announce the winner
        winner_card, loser_card = (card_p0, card_p1) if winner == 0 else (card_p1, card_p0)
        reason = (
            f"Showdown: Player {winner}'s {self._rank_to_str(winner_card)} beats "
            f"Player {1 - winner}'s {self._rank_to_str(loser_card)}. "
            f"Player {winner} wins pot of {self.state.game_state['pot']} chips."
        )
        self._set_round_winner(player_id=winner, reason=reason)



