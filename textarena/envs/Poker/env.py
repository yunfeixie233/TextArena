# import re, random 
# from collections import Counter 
# from typing import Any, Dict, List, Optional, Tuple 

# import textarena as ta 


# class PokerEnv(ta.Env):
#     def __init__(
#         self,
#         num_rounds: int = 10,
#         starting_chips: int = 1_000,
#         small_blind: int = 10,
#         big_blind: int = 20,
#     ):
#         """
#         Initialize the Texas Hold'em Poker game.

#         Args:
#             num_rounds (int): Number of rounds to play
#             starting_chips (int): Starting chips for each player
#             small_blind (int): Small blind amount
#             big_blind (int): Big blind amount
#         """
#         # Game configuration
#         self.num_rounds = num_rounds 
#         self.starting_chips = starting_chips 
#         self.small_blind = small_blind 
#         self.big_blind = big_blind 

#         # Card setup
#         self.suits = ["♠", "♥", "♦", "♣"]
#         self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
#         self.rank_values = {rank: idx for idx, rank in enumerate(self.ranks)}
        
#         # Initialize game state
#         self.state = ta.State(
#             num_players=2,
#             max_turns=num_rounds, # betting rounds per hand
#             check_truncated=False, # no turn limit
#         )

#         # Define action patterns
#         self.check_pattern = re.compile(r"\[Check\]", re.IGNORECASE)
#         self.fold_pattern = re.compile(r"\[Fold\]", re.IGNORECASE)
#         self.call_pattern = re.compile(r"\[Call.*\]", re.IGNORECASE)
#         self.bet_pattern = re.compile(r"\[bet (\d+)\]", re.IGNORECASE)
#         self.raise_pattern = re.compile(r"\[raise (\d+)\]", re.IGNORECASE)

#     @property
#     def terminal_render_keys(self):
#         return [
#             ["player_hands", 0],
#             ["player_hands", 1],
#             "player_chips", 
#             "visible_community_cards", 
#             "player_bets"
#         ]


#     def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
#         """
#         Generate the initial prompt explaining the poker game rules and format to a player.
#         This is called once at the start of the game.

#         Args:
#             player_id (int): ID of the player (0 or 1)
#             game_state (Dict[str, Any]): Initial game state

#         Returns:
#             str: The initial prompt explaining the game rules and format
#         """
#         prompt = (
#             f"You are Player {player_id} in Texas Hold'em Poker.\n"
#             f"Game Information:\n"
#             f"- This is a {self.num_rounds}-round game\n"
#             f"- Each player starts with {self.starting_chips} chips\n"
#             f"- Small blind is {self.small_blind} chips\n"
#             f"- Big blind is {self.big_blind} chips\n"
#             f"- Players must call the current bet to stay in the hand\n\n"
#             "Available Actions:\n"
#             "  [Check] - When there's no bet to call\n"
#             "  [Call] - Match the current bet\n"
#             "  [Fold] - Give up your hand\n"
#             "  [Bet <amount>] - Make a new bet, e.g. [Bet 100]\n"
#             "  [Raise <amount>] - Increase the current bet, e.g. [Raise 200]\n\n"
#             "The Player with the most chips at the end wins"
#         )
#         return prompt

#     def reset(self, num_players: int = 2, seed: Optional[int] = None):
#         """ Reset the full game to its initial state """
#         if seed is not None:
#             random.seed(seed)
#         assert num_players==2, f"The number of players has to be 2 for 2-player Poker. You provided {num_players}"

#         self.state.reset(
#             game_state={
#                 "round": 1,
#                 "betting_round": 0,  # 0: pre-flop, 1: flop, 2: turn, 3: river
#                 "player_chips": {0: self.starting_chips, 1: self.starting_chips},
#                 "player_hands": {0: [], 1: []},
#                 "community_cards": [],
#                 "visible_community_cards": [],
#                 "pot": 0,
#                 "current_bet": 0,
#                 "player_bets": {0: 0, 1: 0},
#                 "button": 0,  # Dealer button position
#                 "folded_players": set(),
#                 "all_in_players": set(),
#                 "checked_players": set(),  # Track who has checked this betting round
#                 "round_turn": 0
#             },
#             player_prompt_function=self._generate_player_prompt,
#             executable_on_reset=[self._reset_round]
#         )

#     def _create_deck(self) -> List[Dict[str, str]]:
#         """Create a standard 52-card deck."""
#         return [{"rank": rank, "suit": suit} for suit in self.suits for rank in self.ranks]

#     def _reset_round(self):
#         """ TODO """
#         # deal new hand
#         deck = self._create_deck()
#         random.shuffle(deck)

#         for player_id in [0, 1]:
#             self.state.game_state["player_hands"][player_id] = [deck.pop() for _ in range(2)]
#             card1, card2 = self.state.game_state["player_hands"][player_id]
#             self.state.add_observation(
#                 from_id=ta.GAME_ID,
#                 to_id=player_id,
#                 message=f"Your cards are: [{card1['rank']}{card1['suit']}, {card2['rank']}{card2['suit']}]",
#                 for_logging=True
#             )

#         # Deal community cards (face down initially)
#         self.state.game_state["community_cards"] = [deck.pop() for _ in range(5)]
#         self.state.game_state["visible_community_cards"] = []

#         # post the blinds
#         sb_player = (self.state.game_state["button"] + 1) % 2
#         bb_player = (self.state.game_state["button"] + 2) % 2


#         # post small blind
#         self.state.game_state["player_chips"][sb_player] -= self.small_blind 
#         self.state.game_state["player_bets"][sb_player] = self.small_blind 
#         self.state.game_state["pot"] += self.small_blind 

#         # post big blind 
#         self.state.game_state["player_chips"][bb_player] -= self.big_blind
#         self.state.game_state["player_bets"][bb_player] = self.big_blind 
#         self.state.game_state["pot"] += self.big_blind 

#         self.state.game_state["current_bet"] = self.big_blind 
#         self.state.game_state["round_turn"] = 0

#         # set current player (bb_player + 1)
#         next_player_id = (bb_player + 1) % 2
#         self.state.manually_updated_current_player(new_player_id=next_player_id)
#         # self.state.current_player_id = (bb_player + 1) % 2

#         self._observe_current_pot()


#     def _observe_current_pot(self):
#         """ TODO """
#         community_card_str = ", ".join([f"{card['rank']}{card['suit']}" for card in self.state.game_state["visible_community_cards"]])
#         current_pot_message = (
#             f"Visible Community Cards: [{community_card_str}]\n"
#             f"Current Pot: {self.state.game_state['pot']}\n"
#             f"Player 0 chips: {self.state.game_state['player_chips'][0]}; current bet: {self.state.game_state['player_bets'][0]}\n"
#             f"Player 1 chips: {self.state.game_state['player_chips'][1]}; current bet: {self.state.game_state['player_bets'][1]}\n"
#         )

#         self.state.add_observation(
#             from_id=ta.GAME_ID,
#             to_id=-1, # Broadcast to all
#             message=current_pot_message
#         )

#     def step(self,action: str) -> Tuple[bool, ta.Info]:
#         """Process a player's action."""
#         # add to observations
#         self.state.add_observation(
#             from_id=self.state.current_player_id,
#             to_id=-1, # Broadcast to all
#             message=action
#         )

#         # process the current betting round
#         self._process_betting_action(action=action, player_id=self.state.current_player_id)


#         # If betting round is complete, move to next phase
#         if self._is_betting_round_complete():
#             self._advance_game_phase()

#         self._observe_current_pot()
#         return self.state.step(rotate_player=False)

#     def _parse_action(self, action: str) -> Tuple[str, Optional[int]]:
#         """
#         Parse the player's action string into action type and bet amount.
        
#         Returns:
#             Tuple[str, Optional[int]]: Action type and bet amount (if applicable)
#         """
#         action = action#.strip()

#         # try to match the patterns
#         check_match = self.check_pattern.search(action)
#         fold_match = self.fold_pattern.search(action)
#         call_match = self.call_pattern.search(action)
#         bet_match = self.bet_pattern.search(action)
#         raise_match = self.raise_pattern.search(action)

#         self.state.game_state["round_turn"] += 1

#         # check patterns in order 
#         if check_match:
#             return "check", None 
#         elif fold_match:
#             return "fold", None 
#         elif call_match:
#             return "call", None 
#         elif bet_match:
#             amount = int(bet_match.group(1))
#             return "bet", amount 
#         elif raise_match:
#             amount = int(raise_match.group(1))
#             return "raise", amount 
        
#         return "invalid", None 

#     def _process_betting_action(self, player_id: int, action: str):
#         """ TODO """
#         # parse and validate the action 
#         action_type, bet_amount = self._parse_action(action)

#         # check if valid
#         if action_type == "invalid":
#             self.state.set_invalid_move(
#                 player_id=player_id,
#                 reason=(
#                     f"Player {player_id} did not provide a valid poker action.",
#                     f"You need to either [check], [fold], [call], [bet <amount>] or [raise <amount]."
#                 )
#             )
#             return

#         # apply the action to update chips, pot, etc.
#         self._apply_action(player_id, action_type, bet_amount)

#         # Check if hand is over (everyone folded or all-in)
#         if self._is_hand_over():
#             self._handle_hand_completion()

#         # move to next player if betting continues
#         else:
#             next_player = self._get_next_active_player(player_id)
#             # self.state.current_player_id = next_player 

#             # try setting the next player 
#             self.state.manually_updated_current_player(new_player_id=next_player)


#     def _is_hand_over(self) -> bool:
#         """
#         Check if the current hand is over due to folds or all-in situations.
        
#         Returns:
#             bool: True if hand is over, False otherwise
#         """
#         active_players = set(range(2)) - self.state.game_state["folded_players"] - self.state.game_state["all_in_players"]
        
#         # Hand is over if only one player remains
#         if len(active_players) == 1:
#             return True
            
#         # Hand is over if all remaining players are all-in
#         if all(player in self.state.game_state["all_in_players"] 
#                for player in active_players):
#             return True

#         # pot hasn't increased 
            
#         return False

#     def _handle_hand_completion(self):
#         """Handle the completion of a hand, either through showdown or single player remaining."""
#         # Reveal all community cards
#         self.state.game_state["visible_community_cards"] = self.state.game_state["community_cards"]
        
#         # Handle showdown or give pot to last player
#         self._handle_showdown()
        
#         # Check if game should continue
#         if self.state.game_state["round"] < self.num_rounds and all(
#             chips > 0 for chips in self.state.game_state["player_chips"].values()
#         ):
#             # Start new hand
#             self.state.game_state["round"] += 1
#             self.state.game_state["betting_round"] = 0
#             self.state.game_state["button"] = (self.state.game_state["button"] + 1) % 2
#             self.state.game_state["folded_players"] = set()
#             self.state.game_state["all_in_players"] = set()
#             self.state.game_state["checked_players"] = set()
#             self._reset_round()
#         else:
#             # Game is complete, determine winner
#             self.determine_winner()
#             self.state.game_state["game_complete"] = True
            
            

#     def _evaluate_hands(self, active_players: set[int]) -> int:
#         """
#         Evaluate the poker hands of active players and determine the winner.
        
#         Args:
#             active_players (set[int]): Set of players still in the hand
        
#         Returns:
#             int: Player ID of the winner
#         """
#         # show the cards of all active players
#         cards = '\n\t'.join([
#             f"Player {p}: " + self.state.game_state["player_hands"][p][0]["rank"]+self.state.game_state["player_hands"][p][0]["suit"]+", "+\
#             self.state.game_state["player_hands"][p][1]["rank"]+self.state.game_state["player_hands"][p][1]["suit"]
#             for p in active_players
#         ])

#         self.state.add_observation(
#             from_id=ta.GAME_ID,
#             to_id=-1, # Broadcast to all
#             message=f"Showdown. Player cards:\n\t{cards}\n"
#         )

#         community_cards = self.state.game_state["community_cards"]
#         hand_rankings = {}
        
#         for player in active_players:
#             hole_cards = self.state.game_state["player_hands"][player]
#             hand_rankings[player] = self._evaluate_single_hand(hole_cards + community_cards)
        
#         # Return player with the best hand
#         self.state.add_observation(
#             from_id=ta.GAME_ID,
#             to_id=-1,
#             message=f"Player {max(hand_rankings.items(), key=lambda x: x[1])[0]} wins the round."
#         )
#         return max(hand_rankings.items(), key=lambda x: x[1])[0]


#     def _evaluate_single_hand(self, cards: List[Dict[str, str]]) -> Tuple[int, List[int]]:
#         """
#         Evaluate a single poker hand (7 cards) and return its ranking.
        
#         Returns:
#             Tuple[int, List[int]]: (hand_type_rank, [value1, value2, ...])
#             where hand_type_rank is:
#             9: Straight Flush
#             8: Four of a Kind
#             7: Full House
#             6: Flush
#             5: Straight
#             4: Three of a Kind
#             3: Two Pair
#             2: One Pair
#             1: High Card
#         """
#         # Convert cards to ranks and suits
#         ranks = [self.rank_values[card["rank"]] for card in cards]
#         suits = [card["suit"] for card in cards]
        
#         # Check for flush
#         suit_counts = Counter(suits)
#         flush_suit = next((suit for suit, count in suit_counts.items() if count >= 5), None)
        
#         # Get rank counts for pairs, trips, etc
#         rank_counts = Counter(ranks)
        
#         # Check for straight
#         distinct_ranks = sorted(set(ranks))
#         straight = False
#         straight_high = None
        
#         # Handle Ace-low straight specially
#         if set([14, 2, 3, 4, 5]).issubset(set(ranks)):  # Changed from [0,1,2,3,12] to standard values
#             straight = True
#             straight_high = 5  # Changed from 3 to 5 for proper high card
        
#         # Check normal straights
#         for i in range(len(distinct_ranks) - 4):
#             if distinct_ranks[i+4] - distinct_ranks[i] == 4:
#                 straight = True
#                 straight_high = distinct_ranks[i+4]
        
#         # Evaluate hand type from highest to lowest
#         # Straight Flush
#         if flush_suit and straight:
#             flush_cards = [c for c in cards if c["suit"] == flush_suit]
#             flush_ranks = sorted([self.rank_values[c["rank"]] for c in flush_cards])
#             # Check if flush cards form a straight
#             for i in range(len(flush_ranks) - 4):
#                 if flush_ranks[i+4] - flush_ranks[i] == 4:
#                     return (9, [flush_ranks[i+4]])  # Return highest card of straight flush
#             # Check Ace-low straight flush
#             if set([14, 2, 3, 4, 5]).issubset(set(flush_ranks)):
#                 return (9, [5])
        
#         # Four of a Kind
#         if 4 in rank_counts.values():
#             quads = max(r for r, count in rank_counts.items() if count == 4)
#             kicker = max(r for r in ranks if r != quads)  # Changed to ensure we get highest kicker
#             return (8, [quads, kicker])
        
#         # Full House
#         if 3 in rank_counts.values():
#             trips = max(r for r, count in rank_counts.items() if count == 3)
#             pairs = [r for r, count in rank_counts.items() if count >= 2 and r != trips]
#             if pairs:  # If we have at least one pair
#                 return (7, [trips, max(pairs)])
        
#         # Flush
#         if flush_suit:
#             flush_ranks = sorted([self.rank_values[c["rank"]] for c in cards if c["suit"] == flush_suit], reverse=True)
#             return (6, flush_ranks[:5])
        
#         # Straight
#         if straight:
#             return (5, [straight_high])
        
#         # Three of a Kind
#         if 3 in rank_counts.values():
#             trips = max(r for r, count in rank_counts.items() if count == 3)
#             kickers = sorted([r for r in ranks if r != trips], reverse=True)  # Changed to exclude trips value
#             return (4, [trips] + kickers[:2])
        
#         # Two Pair
#         pairs = [r for r, count in rank_counts.items() if count == 2]
#         if len(pairs) >= 2:
#             pairs.sort(reverse=True)
#             kickers = [r for r in ranks if rank_counts[r] == 1]
#             kicker = max(kickers) if kickers else min(pairs)  # Handle case where we might have three pairs
#             return (3, pairs[:2] + [kicker])
        
#         # One Pair
#         if 2 in rank_counts.values():
#             pair = max(r for r, count in rank_counts.items() if count == 2)
#             kickers = sorted([r for r in ranks if r != pair], reverse=True)  # Changed to exclude pair value
#             return (2, [pair] + kickers[:3])
        
#         # High Card
#         high_cards = sorted(ranks, reverse=True)
#         return (1, high_cards[:5])


#     def _is_betting_round_complete(self) -> bool:
#         """
#         Check if the current betting round is complete.
#         A betting round is complete when either:
#         1. All active players have matched the highest bet
#         2. All active players have checked (when there's no bet)
#         """
#         active_players = set(range(2)) - self.state.game_state["folded_players"]
#         current_bet = self.state.game_state["current_bet"]
        
#         if current_bet == 0:
#             # If no bets, everyone needs to check
#             return self.state.game_state["checked_players"] == active_players
#         else:
#             # If there are bets, everyone needs to match, and if this is the 
#             # first round, if the amount is equal to the blind
#             # the big-blind needs to have checked
#             if all(
#                 self.state.game_state["player_bets"][pid] == current_bet
#                 for pid in active_players 
#                 if pid not in self.state.game_state["all_in_players"]
#             ):
#                 # make sure every player had a turn
#                 if self.state.game_state["round_turn"] >= 2:
#                     return True 
#                 return False 


#     def _advance_game_phase(self):
#         """ TODO """
#         if self.state.game_state["betting_round"] < 3: # Still in current hand
#             # Move to next betting round
#             self.state.game_state["betting_round"] += 1

#             # Reset betting state
#             self.state.game_state["current_bet"] = 0
#             self.state.game_state["player_bets"] = {0: 0, 1: 0}
#             self.state.game_state["checked_players"] = set()

#             # Reveal community cards for the new phase 
#             visible_cards = {
#                 1: 3,  # Flop
#                 2: 4,  # Turn
#                 3: 5,  # River
#             }.get(self.state.game_state["betting_round"], 0)

#             self.state.game_state["visible_community_cards"] = self.state.game_state["community_cards"][:visible_cards]
        
#         else: # Hand is complete
#             self._handle_showdown()

#             # Check if game should continue 
#             if self.state.game_state["round"] < self.num_rounds and all(
#                 chips > 0 for chips in self.state.game_state["player_chips"].values()
#             ):
#                 # Start new hand 
#                 self.state.game_state["round"] += 1
#                 self.state.game_state["betting_round"] = 0
#                 self.state.game_state["button"] = (self.state.game_state["button"] + 1) % 2
#                 self.state.game_state["folded_players"] = set()
#                 self.state.game_state["all_in_players"] = set()
#                 self.state.game_state["checked_players"] = set()
#                 self.state.game_state["visible_community_cards"] = []
#                 self._reset_round()
#             else:
#                 # Game is complete
#                 self.determine_winner()
#                 self.state.game_state["game_complete"] = True

#     def _handle_showdown(self):
#         """ TODO """
#         active_players = set(range(2)) - self.state.game_state["folded_players"]

#         if len(active_players) > 1:
#             # evaluate hands and determine winner
#             winner = self._evaluate_hands(active_players)
#         else:
#             # Last player remaining gets pot 
#             winner = active_players.pop()

#         self.state.game_state["player_chips"][winner] += self.state.game_state["pot"]
#         self.state.game_state["pot"] = 0


#     def _get_next_active_player(self, current_player_id: int) -> int:
#         """ TODO """
#         next_player = (current_player_id + 1) % 2

#         # Skip players who have folded or are all-in
#         while (
#             next_player in self.state.game_state["folded_players"] or 
#             next_player in self.state.game_state["all_in_players"]
#         ):
#             next_player = (next_player + 1) % 2

#         return next_player 


#     def determine_winner(self) -> Tuple[int, int]:
#         """
#         Determine the overall winner of the game and their final chip count.
        
#         Returns:
#             Tuple[int, int]: (winner_id, final_chips)
#         """

#         # Get final chip counts
#         final_chips = self.state.game_state["player_chips"]

#         chips_player_0 = final_chips[0]
#         chips_player_1 = final_chips[1]

#         if chips_player_0 == chips_player_1:
#             self.state.set_draw(
#                 reason=f"Both players finished the game with the same number of chips."
#             )

#         else:
#             winner_id = 0 if chips_player_0 > chips_player_1 else 1
#             winner_chips = final_chips[winner_id]

#             self.state.game_state["game_complete"] = True
#             self.state.game_state["winner"] = winner_id
#             self.state.game_state["winning_chips"] = winner_chips

#             self.state.set_winners(
#                 player_ids=[winner_id],
#                 reason=f"Player {winner_id} won by gaining the most chips"
#             )
        


#     def _apply_action(self, player_id: int, action_type: str, bet_amount: Optional[int]):
#         """
#         Apply the parsed action to the game state.
#         """
#         if action_type == "fold":
#             self.state.game_state["folded_players"].add(player_id)
#             self.state.add_observation(
#                 from_id=ta.GAME_ID,
#                 to_id=-1, # Broadcast to all
#                 message=f"Player {player_id} has folded."
#             )
            
#         elif action_type == "check":
#             if self.state.game_state["current_bet"] > self.state.game_state["player_bets"][player_id]:
#                 self.state.set_invalid_move(
#                     player_id=player_id,
#                     reason=f"Player {player_id}. Cannot check when there's a bet to call"
#                 )
#             else:
#                 self.state.game_state["checked_players"].add(player_id)
#                 self.state.add_observation(
#                     from_id=ta.GAME_ID,
#                     to_id=-1,
#                     message=f"Player {player_id} has checked."
#                 )
            
                
#         elif action_type == "call":
#             call_amount = self.state.game_state["current_bet"] - self.state.game_state["player_bets"][player_id]

#             if call_amount == 0:
#                 # treat as check
#                 self.state.game_state["checked_players"].add(player_id)
#                 self.state.add_observation(
#                     from_id=ta.GAME_ID,
#                     to_id=-1,
#                     message=f"Player {player_id} has checked."
#                 )

#             elif call_amount > self.state.game_state["player_chips"][player_id]:
#                 # Player goes all-in
#                 call_amount = self.state.game_state["player_chips"][player_id]
#                 self.state.game_state["all_in_players"].add(player_id)

#                 self.state.add_observation(
#                     from_id=ta.GAME_ID,
#                     to_id=-1, # Broadcast to all
#                     message=f"Player {player_id} is going all in."
#                 )
#             else:
#                 self.state.add_observation(
#                     from_id=ta.GAME_ID,
#                     to_id=-1, # Broadcast to all
#                     message=f"Player {player_id} has called ({call_amount})."
#                 )
            
                

                
#             self.state.game_state["player_chips"][player_id] -= call_amount
#             self.state.game_state["player_bets"][player_id] += call_amount
#             self.state.game_state["pot"] += call_amount
            
#         elif action_type in ["bet", "raise"]:    
#             # Calculate total amount player needs to put in
#             total_amount = bet_amount
#             if action_type == "raise":
#                 total_amount += self.state.game_state["current_bet"]


#             if total_amount > self.state.game_state["player_chips"][player_id]:
#                 self.state.set_invalid_move(
#                     player_id=player_id,
#                     reason=f"Player {player_id}. Bet amount exceeds available chips."
#                 )
            
                
#             # Handle the bet
#             current_bet = self.state.game_state["player_bets"][player_id]
#             amount_to_add = total_amount - current_bet

#             self.state.add_observation(
#                 from_id=ta.GAME_ID,
#                 to_id=-1, # Broadcast to all
#                 message=f"Player {player_id} has raised/bet ({amount_to_add})."
#             )
            
#             self.state.game_state["player_chips"][player_id] -= amount_to_add
#             self.state.game_state["player_bets"][player_id] = total_amount
#             self.state.game_state["pot"] += amount_to_add
#             self.state.game_state["current_bet"] = total_amount
            
#             # Check for all-in
#             if self.state.game_state["player_chips"][player_id] == 0:
#                 self.state.game_state["all_in_players"].add(player_id)


import re, random
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import textarena as ta


class PokerEnv(ta.Env):
    # Define action patterns
    check_pattern = re.compile(r"\[Check\]", re.IGNORECASE)
    fold_pattern = re.compile(r"\[Fold\]", re.IGNORECASE)
    call_pattern = re.compile(r"\[Call.*\]", re.IGNORECASE)
    bet_pattern = re.compile(r"\[bet (\d+)\]", re.IGNORECASE)
    raise_pattern = re.compile(r"\[raise (\d+)\]", re.IGNORECASE)

    def __init__(
        self,
        num_rounds: int = 10,
        starting_chips: int = 1_000,
        small_blind: int = 10,
        big_blind: int = 20,
    ):
        """
        A simplified multi-player Texas Hold'em Poker environment (no side pots).
        Handles between 2 and 15 players.

        Args:
            num_rounds (int): Number of rounds to play.
            starting_chips (int): Starting chip stack for each player.
            small_blind (int): Small blind amount.
            big_blind (int): Big blind amount.
        """
        self.num_rounds = num_rounds
        self.starting_chips = starting_chips
        self.small_blind = small_blind
        self.big_blind = big_blind

        # Card setup
        self.suits = ["♠", "♥", "♦", "♣"]
        self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.rank_values = {rank: idx+2 for idx, rank in enumerate(self.ranks)}
        #  (Mapping e.g. "2" -> 2, ..., "10"->10, "J"->11, "Q"->12, "K"->13, "A"->14)

    @property
    def terminal_render_keys(self):
        """
        Keys that your environment's renderer (or logs) might use to display state in a summary.
        Include anything you want to show in a terminal or offline environment.
        """
        return [
            "player_chips",
            "visible_community_cards",
            "player_bets",
            "button",
            "pot"
        ]

    # def reset(self, num_players: int, seed: Optional[int] = None):
    #     """ Reset the full game to its initial state """
    #     # Create the underlying state for N players
    #     self.state = ta.State(num_players=num_players, min_players=2, max_players=15)
        
    #     # Store the basic structure of the game
    #     game_state = {
    #             "round": 1,
    #             "betting_round": 0,  # 0: pre-flop, 1: flop, 2: turn, 3: river
    #             "player_chips": {pid: self.starting_chips for pid in range(num_players)},
    #             "player_hands": {pid: [] for pid in range(num_players)},
    #             "community_cards": [],
    #             "visible_community_cards": [],
    #             "pot": 0,
    #             "current_bet": 0,
    #             "player_bets": {pid: 0 for pid in range(num_players)},
    #             "button": 0,  # Dealer button position
    #             "folded_players": set(),
    #             "all_in_players": set(),
    #             "checked_players": set(),
    #             "round_turn": 0,  # how many actions have taken place in this betting round
    #             "game_complete": False
    #         }
    #     self.state.reset(seed=seed, game_state=game_state, player_prompt_function=self._generate_player_prompt, executable_on_reset=[self._reset_round])
    def reset(self, num_players: int, seed: Optional[int] = None):
        """ Reset the full game to its initial state """
        # Create the underlying state for N players
        self.state = ta.State(num_players=num_players, min_players=2, max_players=15)
        
        # Store the basic structure of the game
        game_state = {
                "round": 1,  # Start at round 1
                "betting_round": 0,  # 0: pre-flop, 1: flop, 2: turn, 3: river
                "player_chips": {pid: self.starting_chips for pid in range(num_players)},
                "player_hands": {pid: [] for pid in range(num_players)},
                "community_cards": [],
                "visible_community_cards": [],
                "pot": 0,
                "current_bet": 0,
                "player_bets": {pid: 0 for pid in range(num_players)},
                "button": 0,  # Dealer button position
                "folded_players": set(),
                "all_in_players": set(),
                "checked_players": set(),
                "round_turn": 0,  # how many actions have taken place in this betting round
                "game_complete": False,
                "last_valid_round": 1,  # Track the last valid round number for error recovery
                "last_valid_betting_round": 0  # Track the last valid betting round for error recovery
            }
        self.state.reset(seed=seed, game_state=game_state, player_prompt_function=self._generate_player_prompt, executable_on_reset=[self._reset_round])
        
        # Announce new game starting
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,
            message=f"Starting a new {self.num_rounds}-round Texas Hold'em game with {num_players} players."
        )

    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """
        Generate the initial prompt explaining the poker game rules and format to a player.
        This is called once at the start of the game.
        """
        prompt = (
            f"You are Player {player_id} in a {self.state.num_players}-player Texas Hold'em Poker game.\n"
            f"Game Information:\n"
            f"- This is a {self.num_rounds}-round game\n"
            f"- Each player starts with {self.starting_chips} chips\n"
            f"- Small blind is {self.small_blind} chips\n"
            f"- Big blind is {self.big_blind} chips\n"
            f"- Players must call the current bet to stay in the hand\n\n"
            "Available Actions:\n"
            "  '[Check]' - When there's no bet to call\n"
            "  '[Call]' - Match the current bet\n"
            "  '[Fold]' - Give up your hand\n"
            "  '[Bet <amount>]' - Make a new bet, e.g. '[Bet 100]'\n"
            "  '[Raise <amount>]' - Increase the current bet, e.g. '[Raise 200]'\n\n"
            "The Player with the most chips at the end wins"
        )
        return prompt

    def _create_deck(self) -> List[Dict[str, str]]:
        """Create a standard 52-card deck."""
        return [{"rank": rank, "suit": suit} for suit in self.suits for rank in self.ranks]

    def _reset_round(self):
        """
        Initialize a new round (hand):
          - Shuffle and deal hole cards
          - Reset pot, bets, etc.
          - Post small blind and big blind
          - Set next player to act
        """
        gs = self.state.game_state
        num_players = self.state.num_players

        deck = self._create_deck()
        random.shuffle(deck)

        # Deal each player 2 cards
        for pid in range(num_players):
            gs["player_hands"][pid] = [deck.pop(), deck.pop()]
            c1, c2 = gs["player_hands"][pid]
            # Private observation for each player's hole cards
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=pid,
                message=f"Your hole cards: [{c1['rank']}{c1['suit']}, {c2['rank']}{c2['suit']}]",
                for_logging=True
            )

        # Reset community cards
        gs["community_cards"] = [deck.pop() for _ in range(5)]
        gs["visible_community_cards"] = []

        # Reset pot, bets, etc.
        gs["pot"] = 0
        gs["current_bet"] = 0
        gs["player_bets"] = {pid: 0 for pid in range(num_players)}
        gs["folded_players"] = set()
        gs["all_in_players"] = set()
        gs["checked_players"] = set()
        gs["round_turn"] = 0

        # Post blinds
        button = gs["button"]
        sb_player = (button + 1) % num_players
        bb_player = (button + 2) % num_players

        # Subtract small blind
        sb = min(self.small_blind, gs["player_chips"][sb_player])
        gs["player_chips"][sb_player] -= sb
        gs["player_bets"][sb_player] = sb
        gs["pot"] += sb

        # Subtract big blind
        bb = min(self.big_blind, gs["player_chips"][bb_player])
        gs["player_chips"][bb_player] -= bb
        gs["player_bets"][bb_player] = bb
        gs["pot"] += bb

        gs["current_bet"] = max(sb, bb)

        # Next player to act is the one after the big blind
        next_player_id = (bb_player + 1) % num_players
        self.state.manually_updated_current_player(new_player_id=next_player_id)

        self._observe_current_pot()


    # def _observe_current_pot(self):
    #     """
    #     Send a formatted observation to the next player showing:
    #     - Round number (out of total rounds) and the current turn (pre-flop, flop, turn, river)
    #     - The visible community cards and the pot
    #     - A table listing each player's chip count, bet, and status (active, folded, or all-in)
    #         with their role (Dealer, Small Blind, Big Blind) next to their name.
    #     - Privately remind the current player of their hole cards.
    #     """
    #     gs = self.state.game_state
    #     num_players = self.state.num_players

    #     # Header: show round and turn info.
    #     round_text = f"Round {gs['round']} of {self.num_rounds}"
    #     turn_names = {0: "Pre-flop", 1: "Flop", 2: "Turn", 3: "River"}
    #     turn_text = turn_names.get(gs["betting_round"], "Unknown Turn")
    def _observe_current_pot(self):
        """
        Send a formatted observation to the next player showing the game state.
        """
        gs = self.state.game_state
        num_players = self.state.num_players

        # Validate that round number is within bounds
        round_num = max(1, min(gs["round"], self.num_rounds))
        betting_round = max(0, min(gs["betting_round"], 3))
        
        # Header: show round and turn info.
        round_text = f"Round {round_num} of {self.num_rounds}"
        turn_names = {0: "Pre-flop", 1: "Flop", 2: "Turn", 3: "River"}
        turn_text = turn_names.get(betting_round, "Unknown Turn")

        # Ensure visible cards match the betting round
        if betting_round == 0:
            expected_visible = []
        elif betting_round == 1:
            expected_visible = gs["community_cards"][:3]
        elif betting_round == 2:
            expected_visible = gs["community_cards"][:4]
        elif betting_round == 3:
            expected_visible = gs["community_cards"][:5]
        
        # Fix visible cards if they don't match expected
        if gs["visible_community_cards"] != expected_visible and not gs["game_complete"]:
            gs["visible_community_cards"] = expected_visible


        # Determine roles based on the dealer button:
        dealer = gs["button"]
        small_blind = (dealer + 1) % num_players
        big_blind = (dealer + 2) % num_players

        # Build the community cards string.
        community_str = ", ".join(
            f"{card['rank']}{card['suit']}" for card in gs["visible_community_cards"]
        )

        # Build player status lines with roles included.
        player_lines = []
        for pid in range(num_players):
            role_labels = []
            if pid == dealer:
                role_labels.append("Dealer")
            if pid == small_blind:
                role_labels.append("Small Blind")
            if pid == big_blind:
                role_labels.append("Big Blind")
            role_str = f" ({'/'.join(role_labels)})" if role_labels else ""

            if pid in gs["folded_players"]:
                status = "folded"
            elif pid in gs["all_in_players"]:
                status = "all-in"
            else:
                status = "active"

            player_lines.append(
                f"Player {pid}{role_str}: {gs['player_chips'][pid]} chips, bet={gs['player_bets'][pid]}, status={status}"
            )

        # Compose the full observation message.
        current_pid = self.state.current_player_id
        hole = gs["player_hands"][current_pid]
        obs_message = (
            f"----- {round_text} - Turn: {turn_text} -----\n"
            f"Visible Community Cards: [{community_str}]\n"
            f"Pot: {gs['pot']}\n"
            + "\n".join(player_lines) +
            f"\nYour hole cards: {hole[0]['rank']}{hole[0]['suit']}, "
            f"{hole[1]['rank']}{hole[1]['suit']}"
            "\n-----------------------------------------"
        )

        # Send the observation only to the current (next) player.
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=current_pid,
            message=obs_message
        )

    # def step(self, action: str) -> Tuple[bool, ta.Info]:
    #     current_pid = self.state.current_player_id
        
    #     # Broadcast action
    #     self.state.add_observation(from_id=current_pid, to_id=-1, message=action)
        
    #     # Process the action
    #     self._process_betting_action(action=action, player_id=current_pid)
        
    #     # Check if round is complete ONLY if game isn't already over
    #     if not self.state.game_state["game_complete"]:
    #         complete = self._is_betting_round_complete()
    #         if complete and not self._is_hand_over():
    #             self._advance_game_phase()
        
    #     # Update observations after any changes
    #     self._observe_current_pot()
        
    #     return self.state.step(rotate_player=False)

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """Process the current player's action and advance the game state accordingly"""
        # Check if game is already complete
        if self.state.game_state["game_complete"]:
            reason = "The game is already complete. No further actions can be taken."
            self.state.set_invalid_move(player_id=self.state.current_player_id, reason=reason)
            return False, {"reason": reason}
            
        current_pid = self.state.current_player_id

        # Broadcast the action
        self.state.add_observation(from_id=current_pid, to_id=-1, message=action)

        # Parse and apply the action
        self._process_betting_action(action=action, player_id=current_pid)

        # Safeguard: validate round/betting round consistency
        gs = self.state.game_state
        if gs["round"] < 1 or gs["round"] > self.num_rounds or gs["betting_round"] < 0 or gs["betting_round"] > 3:
            # Log error and fix corrupted state
            err_msg = f"ERROR: Detected invalid game state. Round: {gs['round']}, Betting Round: {gs['betting_round']}"
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=err_msg)
            # Attempt to repair the state - use most recent valid values
            gs["round"] = max(1, min(gs["round"], self.num_rounds))
            gs["betting_round"] = max(0, min(gs["betting_round"], 3))

        # If the betting round is complete, advance game phase
        if not self.state.game_state["game_complete"]:
            if self._is_betting_round_complete() and not self._is_hand_over():
                self._advance_game_phase()

        # After all that, observe pot again
        self._observe_current_pot()

        return self.state.step(rotate_player=False)

    def _process_betting_action(self, action: str, player_id: int):
        """Parse action, validate, apply, and check if hand ends."""
        action_type, bet_amount = self._parse_action(action)
        gs = self.state.game_state

        if action_type == "invalid":
            reason=(
                    f"Player {player_id} did not provide a valid poker action.\n"
                    "Valid actions: '[Check]', '[Fold]', '[Call]', '[Bet <amount>]', '[Raise <amount>]'."
                )
            self.state.set_invalid_move(player_id=player_id, reason=reason)
            return

        # Apply the action
        self._apply_action(player_id, action_type, bet_amount)

        # Check if the hand ends immediately (folds or everyone all-in)
        if self._is_hand_over() and not gs["game_complete"]:
            self._handle_hand_completion()
        else:
            # Move action to next active player (if not already going to next round, etc.)
            next_player = self._get_next_active_player(player_id)
            self.state.manually_updated_current_player(new_player_id=next_player)

    def _parse_action(self, action: str) -> Tuple[str, Optional[int]]:
        """Parse the player's action string into (action_type, bet_amount)."""
        gs = self.state.game_state
        gs["round_turn"] += 1

        # Attempt pattern matches
        if self.check_pattern.search(action):
            return ("check", None)
        if self.fold_pattern.search(action):
            return ("fold", None)
        if self.call_pattern.search(action):
            return ("call", None)
        if self.bet_pattern.search(action):
            match = self.bet_pattern.search(action)
            amount = int(match.group(1))
            return ("bet", amount)
        if self.raise_pattern.search(action):
            match = self.raise_pattern.search(action)
            amount = int(match.group(1))
            return ("raise", amount)

        return ("invalid", None)

    def _apply_action(self, player_id: int, action_type: str, bet_amount: Optional[int]):
        """
        Update the game state according to the player's action choice.
        Note: This version does not implement side pots.
        """
        gs = self.state.game_state
        if action_type == "fold":
            gs["folded_players"].add(player_id)
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=f"Player {player_id} folds.")

        elif action_type == "check":
            if gs["current_bet"] > gs["player_bets"][player_id]:
                self.state.set_invalid_move(player_id=player_id, reason="Cannot check when there's a live bet to call.")
            else:
                gs["checked_players"].add(player_id)
                self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=f"Player {player_id} checks.")

        elif action_type == "call":
            call_needed = gs["current_bet"] - gs["player_bets"][player_id]
            if call_needed < 0:
                # Player is trying to "call" when they've already matched or exceeded. Treat as check.
                gs["checked_players"].add(player_id)
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,
                    message=f"Player {player_id} checks (already matched)."
                )
                return

            # If they do not have enough chips, they go all in.
            if call_needed >= gs["player_chips"][player_id]:
                all_in_amount = gs["player_chips"][player_id]
                gs["player_bets"][player_id] += all_in_amount
                gs["player_chips"][player_id] = 0
                gs["pot"] += all_in_amount
                gs["all_in_players"].add(player_id)
                message=f"Player {player_id} calls all-in for {all_in_amount}."
                self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)
                # Also update current bet if needed
                if gs["player_bets"][player_id] > gs["current_bet"]:
                    gs["current_bet"] = gs["player_bets"][player_id]
            else:
                # Normal call
                gs["player_bets"][player_id] += call_needed
                gs["player_chips"][player_id] -= call_needed
                gs["pot"] += call_needed
                message=f"Player {player_id} calls {call_needed}."
                self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)

        elif action_type in ("bet", "raise"):
            # Raise or Bet means the player is putting in an amount above current bet.
            # If "raise", total_amount = current_bet + raise_amount
            # If "bet" (when current bet is 0?), total_amount = bet_amount
            current_player_contribution = gs["player_bets"][player_id]
            if action_type == "bet":
                # This implies no prior bet or we allow bet as a new bet. Usually bet is if current_bet==0.
                total_amount = bet_amount
            else:
                # raise
                total_amount = gs["current_bet"] + bet_amount

            if total_amount <= gs["current_bet"] and action_type == "raise":
                reason=f"A raise must exceed the current bet of {gs['current_bet']}."
                self.state.set_invalid_move(player_id=player_id, reason=reason)
                return

            # How much do they need to add
            needed = total_amount - current_player_contribution
            if needed < 0:
                reason="Bet/Raise amount is too small or negative."
                self.state.set_invalid_move(player_id=player_id, reason=reason)
                return

            if needed > gs["player_chips"][player_id]:
                # All-in
                needed = gs["player_chips"][player_id]
                gs["all_in_players"].add(player_id)

            gs["player_bets"][player_id] += needed
            gs["player_chips"][player_id] -= needed
            gs["pot"] += needed

            if gs["player_bets"][player_id] > gs["current_bet"]:
                gs["current_bet"] = gs["player_bets"][player_id]

            message=f"Player {player_id} {action_type}s {needed} (total={gs['player_bets'][player_id]})."
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)

    def _is_hand_over(self) -> bool:
        """
        Check if the current hand is over because:
          - only one player remains (others folded)
          - or all active players are all in
        """
        gs = self.state.game_state
        num_players = self.state.num_players

        # active = not folded and not out of chips
        active_players = [
            pid for pid in range(num_players)
            if pid not in gs["folded_players"] and gs["player_chips"][pid] > 0
        ]
        # If at any point a player is at 0 chips but hasn't folded, we consider them "all in"
        # so they remain "active" in a sense until showdown, but can't bet further.
        # We'll track that in gs["all_in_players"], but let's be consistent:
        for pid in range(num_players):
            if gs["player_chips"][pid] == 0 and pid not in gs["folded_players"]:
                gs["all_in_players"].add(pid)

        # If only one player is truly active or has not folded, the hand ends
        if len(active_players) <= 1:
            return True

        # If all active players are all_in, the hand ends immediately (skip further betting)
        if all(pid in gs["all_in_players"] for pid in active_players):
            return True

        return False

    # def _handle_hand_completion(self):
    #     """When the hand ends early (folds) or due to all-ins, go directly to showdown, then next round or game end."""
    #     gs = self.state.game_state

    #     # Reveal all community cards
    #     gs["visible_community_cards"] = gs["community_cards"]

    #     self._handle_showdown()

    #     # Check if we can start a new hand
    #     if gs["round"] < self.num_rounds:
    #         # Check if at least two players still have chips
    #         # If only one remains with chips, game is effectively over
    #         players_with_chips = [pid for pid, chips in gs["player_chips"].items() if chips > 0]
    #         if len(players_with_chips) > 1:
    #             # new round
    #             gs["round"] += 1
    #             gs["betting_round"] = 0
    #             gs["button"] = (gs["button"] + 1) % self.state.num_players
    #             self._reset_round()
    #             return
    #     # Otherwise, finalize game
    #     self.determine_winner()
    #     gs["game_complete"] = True
    def _handle_hand_completion(self):
        """When the hand ends early (folds) or due to all-ins, go directly to showdown, then next round or game end."""
        gs = self.state.game_state

        # Reveal all community cards
        gs["visible_community_cards"] = gs["community_cards"]

        self._handle_showdown()

        # Check if we can start a new hand
        if gs["round"] < self.num_rounds:
            # Check if at least two players still have chips
            players_with_chips = [pid for pid, chips in gs["player_chips"].items() if chips > 0]
            if len(players_with_chips) > 1:
                # New round
                gs["round"] += 1
                gs["betting_round"] = 0
                gs["button"] = (gs["button"] + 1) % self.state.num_players
                
                # Add a clear round transition message
                self.state.add_observation(
                    from_id=ta.GAME_ID,
                    to_id=-1,
                    message=f"Starting Round {gs['round']} of {self.num_rounds}"
                )
                
                self._reset_round()
                return
        
        # Game is over - ensure we properly finalize it
        self.determine_winner()
        gs["game_complete"] = True

    def _handle_showdown(self):
        """
        Show all hole cards for the players who haven't folded,
        evaluate their best hands, and award pot to the winner(s).
        This version splits the pot evenly among ties, ignoring side pots.
        """
        gs = self.state.game_state
        num_players = self.state.num_players

        # Which players are still in?
        active_players = [
            pid for pid in range(num_players)
            if pid not in gs["folded_players"]
        ]
        if not active_players:
            # Corner case: everyone folded. Typically the last folder is the last to fold,
            # but in practice you might handle this differently. For simplicity, pot remains
            # unclaimed or we treat the last to fold as winner. We'll pick the last folder’s
            # prior player:
            # But let's handle it simply: no one wins? (unusual corner case)
            message="All players folded simultaneously. No pot awarded (corner case)."
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)
            gs["pot"] = 0
            return

        if len(active_players) == 1:
            # Only one player didn't fold, so they get the pot
            winner = active_players[0]
            gs["player_chips"][winner] += gs["pot"]
            message=f"Player {winner} wins the pot by default (everyone else folded)."
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)
            gs["pot"] = 0
            return

        # Multiple players -> showdown
        # Show each player's hole cards
        details = []
        for pid in active_players:
            hole = gs["player_hands"][pid]
            detail_str = (
                f"Player {pid} hole cards: "
                f"{hole[0]['rank']}{hole[0]['suit']} {hole[1]['rank']}{hole[1]['suit']}"
            )
            details.append(detail_str)
        self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message="Showdown:\n" + "\n".join(details))

        # Evaluate each player's best 5-card hand
        ranks_dict = {}
        for pid in active_players:
            hole_cards = gs["player_hands"][pid]
            community = gs["community_cards"]
            ranks_dict[pid] = self._evaluate_hand(hole_cards + community)

        # Find the best hand rank
        # hand rank is a tuple (hand_category, tie_breaker_list)
        # We do a max() by comparing these tuples
        best_rank = max(ranks_dict.values())
        # find all players that match that rank
        winners = [pid for pid in active_players if ranks_dict[pid] == best_rank]

        # Award the pot
        if len(winners) == 1:
            w = winners[0]
            gs["player_chips"][w] += gs["pot"]
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,
                message=f"Player {w} wins the pot of {gs['pot']}."
            )
            gs["pot"] = 0
        else:
            # tie - split pot evenly
            split_amt = gs["pot"] // len(winners)
            for w in winners:
                gs["player_chips"][w] += split_amt
            remainder = gs["pot"] % len(winners)  # leftover if not divisible
            gs["pot"] = 0
            message=f"Tie among players {winners}. Each gets {split_amt} chips."
            self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)
            if remainder > 0:
                # If you'd like a random leftover awarding, or skip it
                # We'll just discard it or give it to the first winner:
                gs["player_chips"][winners[0]] += remainder

    def _evaluate_hand(self, cards: List[Dict[str, str]]) -> Tuple[int, List[int]]:
        """
        Evaluate the best 5-card hand from 7 cards (2 hole + 5 community).
        Returns a tuple: (hand_ranking_category, tie_breaker_list),
        where hand_ranking_category (int) is:
           9 = Straight Flush
           8 = Four of a Kind
           7 = Full House
           6 = Flush
           5 = Straight
           4 = Three of a Kind
           3 = Two Pair
           2 = One Pair
           1 = High Card
        The tie_breaker_list is used to compare hands in the same category.
        """
        # Convert to numerical ranks & suits
        ranks = [self.rank_values[c["rank"]] for c in cards]
        suits = [c["suit"] for c in cards]

        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)

        # Check for flush
        flush_suit = None
        for s, count in suit_counts.items():
            if count >= 5:
                flush_suit = s
                break

        distinct_ranks = sorted(set(ranks))
        # Check for straight (including ace-low case)
        straight, straight_high = self._check_straight(distinct_ranks)

        # 1) Check Straight Flush
        if flush_suit and straight:
            # collect flush cards
            flush_cards = [r for r, s in zip(ranks, suits) if s == flush_suit]
            flush_cards = sorted(set(flush_cards))
            sf, sf_high = self._check_straight(flush_cards)
            if sf:
                # hand rank 9, tie-break on the top card
                return (9, [sf_high])

        # 2) Four of a Kind
        if 4 in rank_counts.values():
            quad = max(r for r, cnt in rank_counts.items() if cnt == 4)
            kicker = max(r for r in rank_counts if r != quad)
            return (8, [quad, kicker])

        # 3) Full House (3 of a kind + a pair)
        if 3 in rank_counts.values():
            triple = max(r for r, cnt in rank_counts.items() if cnt == 3)
            # see if there's a pair among the others
            pairs = [r for r, cnt in rank_counts.items() if cnt >= 2 and r != triple]
            if pairs:
                pair = max(pairs)
                return (7, [triple, pair])

        # 4) Flush
        if flush_suit:
            flush_cards = [r for r, s in zip(ranks, suits) if s == flush_suit]
            flush_cards.sort(reverse=True)
            return (6, flush_cards[:5])

        # 5) Straight
        if straight:
            return (5, [straight_high])

        # 6) Three of a kind
        if 3 in rank_counts.values():
            triple = max(r for r, cnt in rank_counts.items() if cnt == 3)
            kickers = sorted((r for r in ranks if r != triple), reverse=True)
            return (4, [triple] + kickers[:2])

        # 7) Two Pair
        pairs = [r for r, cnt in rank_counts.items() if cnt == 2]
        if len(pairs) >= 2:
            pairs.sort(reverse=True)
            top_two = pairs[:2]
            kicker_candidates = [r for r in ranks if r not in top_two]
            kicker = max(kicker_candidates) if kicker_candidates else 0
            return (3, top_two + [kicker])

        # 8) One Pair
        if len(pairs) == 1:
            p = pairs[0]
            kickers = sorted((r for r in ranks if r != p), reverse=True)
            return (2, [p] + kickers[:3])

        # 9) High card
        sorted_ranks = sorted(ranks, reverse=True)
        return (1, sorted_ranks[:5])

    def _check_straight(self, sorted_ranks: List[int]) -> Tuple[bool, int]:
        """
        Given a sorted list of distinct ranks, determine if there's a straight.
        Returns (is_straight, high_card_of_straight).
        Also checks Ace-low case (A,2,3,4,5).
        """
        if len(sorted_ranks) < 5:
            return False, -1

        # Check Ace-low: ranks might include 14 for Ace
        # if we have [14, 2, 3, 4, 5], treat that as a straight (5-high)
        if {14, 2, 3, 4, 5}.issubset(set(sorted_ranks)):
            return True, 5  # 5 is the high card in A2345

        for i in range(len(sorted_ranks) - 4):
            seq = sorted_ranks[i : i + 5]
            if seq[-1] - seq[0] == 4:
                return True, seq[-1]
        return False, -1

    def _is_betting_round_complete(self):
        gs = self.state.game_state
        num_players = self.state.num_players

        # Get truly active players (not folded, not all-in)
        active_players = [
            pid for pid in range(num_players)
            if pid not in gs["folded_players"] and pid not in gs["all_in_players"]
        ]
        
        # If 0-1 active players, round is complete
        if len(active_players) <= 1:
            return True

        current_bet = gs["current_bet"]
        
        if current_bet == 0:
            # If no bet, all active players must have checked
            # Make sure checked_players contains ALL active players
            return all(pid in gs["checked_players"] for pid in active_players)
        else:
            # All players must match the current bet
            all_matched = all(gs["player_bets"][pid] == current_bet for pid in active_players)
            # Also ensure minimum number of actions have occurred
            return all_matched and gs["round_turn"] >= len(active_players)

    def _advance_game_phase(self):
        gs = self.state.game_state
        num_players = self.state.num_players

        if gs["betting_round"] < 3:
            # Advance to the next betting round
            gs["betting_round"] += 1

            # Reset betting-specific state
            gs["current_bet"] = 0
            gs["player_bets"] = {pid: 0 for pid in range(num_players)}
            gs["checked_players"] = set()  # Make sure this is cleared
            gs["round_turn"] = 0  # Reset turn counter

            # Reveal appropriate community cards
            if gs["betting_round"] == 1:
                # Flop: show first 3 cards
                gs["visible_community_cards"] = gs["community_cards"][:3]
            elif gs["betting_round"] == 2:
                # Turn: show 4 cards 
                gs["visible_community_cards"] = gs["community_cards"][:4]
            elif gs["betting_round"] == 3:
                # River: show all 5 cards
                gs["visible_community_cards"] = gs["community_cards"][:5]

            # Always restart with player after button
            next_player = self._get_next_active_player((gs["button"] + 1) % num_players)
            self.state.manually_updated_current_player(new_player_id=next_player)
        else:
            # End of all betting rounds
            self._handle_showdown()
            
            # Check if we should start new hand
            if gs["round"] < self.num_rounds:
                remaining_players = [pid for pid, chips in gs["player_chips"].items() if chips > 0]
                if len(remaining_players) > 1:
                    gs["round"] += 1  # Increment the hand number
                    gs["betting_round"] = 0  # Reset betting round
                    gs["button"] = (gs["button"] + 1) % num_players  # Move button
                    self._reset_round()
                else:
                    self.determine_winner()
                    gs["game_complete"] = True
            else:
                self.determine_winner()
                gs["game_complete"] = True


    def _get_next_active_player(self, current_player: int) -> int:
        """
        Return the next player ID that is neither folded nor all-in.
        If all but one are folded/all-in, we can just return that one or
        the same player. (The logic calling this will handle if the hand ends.)
        """
        gs = self.state.game_state
        num_players = self.state.num_players
        candidate = (current_player + 1) % num_players

        while candidate != current_player:
            if (candidate not in gs["folded_players"]
                and candidate not in gs["all_in_players"]):
                return candidate
            candidate = (candidate + 1) % num_players

        # If we circle back, it means all others are folded/all-in,
        # so we return the original player (which might also be folded/all-in).
        return current_player

    # def determine_winner(self) -> Tuple[List[int], int]:
    #     """
    #     Determine the overall game winner(s) based on who has the most chips.
    #     If there's a tie, mark them all as winners. 
    #     Returns (list_of_winner_ids, chips_of_winner).
    #     """
    #     gs = self.state.game_state
    #     final_chips = gs["player_chips"]
    #     max_chips = max(final_chips.values())

    #     # Might be multiple
    #     winners = [pid for pid, amt in final_chips.items() if amt == max_chips]
    #     if len(winners) == 1:
    #         w = winners[0]
    #         gs["winner"] = w
    #         gs["winning_chips"] = max_chips
    #         reason=f"Player {w} has the most chips ({max_chips})."
    #         self.state.set_winners(player_ids=[w], reason=reason)
    #     else:
    #         # tie
    #         self.state.set_draw(reason=f"Players {winners} tie with {max_chips} chips each.")
    #     return (winners, max_chips)

    def determine_winner(self) -> Tuple[List[int], int]:
        """
        Determine the overall game winner(s) based on who has the most chips.
        If there's a tie, mark them all as winners. 
        Returns (list_of_winner_ids, chips_of_winner).
        """
        gs = self.state.game_state
        final_chips = gs["player_chips"]
        max_chips = max(final_chips.values())

        # Might be multiple
        winners = [pid for pid, amt in final_chips.items() if amt == max_chips]
        if len(winners) == 1:
            w = winners[0]
            gs["winner"] = w
            gs["winning_chips"] = max_chips
            reason = f"Player {w} wins the tournament with {max_chips} chips."
            self.state.set_winners(player_ids=[w], reason=reason)
            # Important: Mark game as complete!
            gs["game_complete"] = True
            
            # Announce final standings
            standings_msg = ", ".join([f"Player {pid} finished with {chips} chips" for pid, chips in final_chips.items()])
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,
                message=f"Tournament complete! {standings_msg}"
            )
        else:
            # tie
            tie_msg = f"Players {winners} tie with {max_chips} chips each."
            self.state.set_draw(reason=tie_msg)
            gs["game_complete"] = True
            
        return (winners, max_chips)
