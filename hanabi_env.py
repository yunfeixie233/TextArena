import random
import re
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import textarena as ta


class Suit(Enum):
    WHITE = "W"
    YELLOW = "Y" 
    GREEN = "G"
    BLUE = "B"
    RED = "R"


class Card:
    def __init__(self, suit: Suit, rank: int):
        self.suit = suit
        self.rank = rank
        
    def __str__(self):
        return f"{self.suit.value}{self.rank}"
    
    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank


class HanabiEnv(ta.Env):
    def __init__(self, life_tokens: int = 3, info_tokens: int = 8):
        self.life_tokens_max = life_tokens
        self.info_tokens_max = info_tokens
        self.suits = list(Suit)
        self.max_rank = 5
        
        # Action patterns
        self.reveal_pattern = re.compile(
            r"\[reveal\]\s+player\s+\+?(\d+)\s+(color|rank)\s+([WYGBR1-5])",
            re.IGNORECASE
        )
        self.play_pattern = re.compile(r"\[play\]\s+(\d+)", re.IGNORECASE)
        self.discard_pattern = re.compile(r"\[discard\]\s+(\d+)", re.IGNORECASE)
    
    def reset(self, num_players: int, seed: Optional[int] = None):
        """Reset the game state for a new game."""
        assert 2 <= num_players <= 5, f"Hanabi supports 2-5 players, got {num_players}"
        
        self.state = ta.TeamMultiPlayerState(
            num_players=num_players,
            seed=seed,
            error_allowance=1
        )
        
        # Determine hand size based on player count
        self.hand_size = 5 if num_players <= 3 else 4
        
        # Generate deck
        self.deck = self._generate_deck()
        random.shuffle(self.deck)
        
        # Initialize game state
        game_state = {
            "life_tokens": self.life_tokens_max,
            "info_tokens": self.info_tokens_max,
            "fireworks": {suit: 0 for suit in self.suits},
            "player_hands": {},
            "hand_hints": {},  # Stores hints each player has about their hand
            "discard_pile": [],
            "deck": self.deck.copy(),
            "last_round_countdown": -1,  # -1 means not in last round
            "score": 0
        }
        
        # Deal initial hands
        for pid in range(num_players):
            game_state["player_hands"][pid] = []
            game_state["hand_hints"][pid] = []
            for _ in range(self.hand_size):
                if game_state["deck"]:
                    card = game_state["deck"].pop()
                    game_state["player_hands"][pid].append(card)
                    game_state["hand_hints"][pid].append({"colors": [], "ranks": []})
        
        self.state.reset(
            game_state=game_state,
            player_prompt_function=self._initial_prompt
        )
        
        # Set first player
        self.state.current_player_id = 0
        
        # Add initial game state observation
        self.state.add_observation(
            to_id=self.state.current_player_id,
            message=self._generate_state_description(self.state.current_player_id),
            observation_type=ta.ObservationType.GAME_MESSAGE
        )
    
    def _generate_deck(self) -> List[Card]:
        """Generate a standard Hanabi deck."""
        deck = []
        rank_counts = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}
        for suit in self.suits:
            for rank, count in rank_counts.items():
                for _ in range(count):
                    deck.append(Card(suit, rank))
        return deck
    
    def _initial_prompt(self, player_id: int, game_state: Dict) -> str:
        """Generate the initial prompt for a player."""
        return f"""You are Player {player_id} in a game of Hanabi.

Hanabi is a cooperative card game where players work together to build fireworks by playing cards in sequence (1-5) for each color.

CRITICAL RULE: You CANNOT see your own cards, only other players' cards.

There are 5 colors: White (W), Yellow (Y), Green (G), Blue (B), Red (R)
Each color has cards: three 1s, two 2s, two 3s, two 4s, and one 5

Resources:
- Life Tokens: {game_state['life_tokens']} (lose one when playing wrong card)
- Info Tokens: {game_state['info_tokens']} (spend to give hints)

Actions (use exact format):
- '[Reveal] player +N color C' - Tell player N positions with color C
- '[Reveal] player +N rank R' - Tell player N positions with rank R  
- '[Play] X' - Play card at position X (0-indexed)
- '[Discard] X' - Discard card at position X to gain an info token

Goal: Cooperatively build all 5 fireworks to score 25 points!"""
    
    def _generate_state_description(self, player_id: int) -> str:
        """Generate current game state description for a player."""
        gs = self.state.game_state
        
        # Build fireworks display
        fireworks = " ".join([f"{s.value}:{gs['fireworks'][s]}" for s in self.suits])
        
        # Build hand descriptions
        hands_desc = []
        
        # Current player's hand (hidden but with hints)
        hands_desc.append(f"Your hand (positions 0-{len(gs['player_hands'][player_id])-1}):")
        for i, card in enumerate(gs['player_hands'][player_id]):
            hints = gs['hand_hints'][player_id][i]
            hint_str = []
            if hints['colors']:
                hint_str.append(f"colors: {','.join(hints['colors'])}")
            if hints['ranks']:
                hint_str.append(f"ranks: {','.join(map(str, hints['ranks']))}")
            hint_info = f" (hints: {'; '.join(hint_str)})" if hint_str else " (no hints)"
            hands_desc.append(f"  Position {i}: ???{hint_info}")
        
        # Other players' hands (visible)
        for pid in range(self.state.num_players):
            if pid != player_id:
                relative_pos = (pid - player_id) % self.state.num_players
                hands_desc.append(f"\nPlayer +{relative_pos}'s hand:")
                for i, card in enumerate(gs['player_hands'][pid]):
                    hands_desc.append(f"  Position {i}: {card}")
        
        # Discard pile summary
        if gs['discard_pile']:
            discards = ", ".join([str(c) for c in gs['discard_pile'][-5:]])  # Show last 5
            discard_info = f"Recent discards: {discards}"
        else:
            discard_info = "Discard pile: empty"
        
        return f"""Game State:
Life tokens: {gs['life_tokens']}/{self.life_tokens_max}
Info tokens: {gs['info_tokens']}/{self.info_tokens_max}
Fireworks: {fireworks}
Cards in deck: {len(gs['deck'])}
{discard_info}

{chr(10).join(hands_desc)}"""
    
    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """Process a player's action."""
        self.state.add_observation(
            from_id=self.state.current_player_id,
            message=action,
            observation_type=ta.ObservationType.PLAYER_ACTION
        )
        
        # Parse and execute action
        action_executed = False
        
        # Check for reveal action
        reveal_match = self.reveal_pattern.search(action)
        if reveal_match:
            self._handle_reveal(reveal_match)
            action_executed = True
        
        # Check for play action
        play_match = self.play_pattern.search(action)
        if play_match and not action_executed:
            self._handle_play(play_match)
            action_executed = True
        
        # Check for discard action
        discard_match = self.discard_pattern.search(action)
        if discard_match and not action_executed:
            self._handle_discard(discard_match)
            action_executed = True
        
        # Invalid action
        if not action_executed:
            self.state.set_invalid_move(
                reason="Invalid action format. Use [Reveal], [Play], or [Discard]"
            )
        
        # Check game end conditions
        self._check_game_end()
        
        # Rotate to next player if no invalid move
        if not self.state.made_invalid_move and not self.state.done:
            self.state.current_player_id = (self.state.current_player_id + 1) % self.state.num_players
            
            # Send state to next player
            self.state.add_observation(
                to_id=self.state.current_player_id,
                message=self._generate_state_description(self.state.current_player_id),
                observation_type=ta.ObservationType.GAME_MESSAGE
            )
        
        return self.state.step(rotate_player=False)
    
    def _handle_reveal(self, match):
        """Handle a reveal (hint) action."""
        gs = self.state.game_state
        
        # Check if we have info tokens
        if gs['info_tokens'] <= 0:
            self.state.set_invalid_move(reason="No info tokens available")
            return
        
        # Parse the action
        relative_player = int(match.group(1))
        hint_type = match.group(2).lower()
        hint_value = match.group(3).upper()
        
        # Calculate target player
        target_player = (self.state.current_player_id + relative_player) % self.state.num_players
        
        if target_player == self.state.current_player_id:
            self.state.set_invalid_move(reason="Cannot give hints to yourself")
            return
        
        # Find matching cards
        target_hand = gs['player_hands'][target_player]
        matching_positions = []
        
        if hint_type == "color":
            if hint_value not in [s.value for s in self.suits]:
                self.state.set_invalid_move(reason=f"Invalid color: {hint_value}")
                return
            
            for i, card in enumerate(target_hand):
                if card.suit.value == hint_value:
                    matching_positions.append(i)
                    if hint_value not in gs['hand_hints'][target_player][i]['colors']:
                        gs['hand_hints'][target_player][i]['colors'].append(hint_value)
        
        elif hint_type == "rank":
            try:
                rank = int(hint_value)
                if rank < 1 or rank > 5:
                    self.state.set_invalid_move(reason=f"Invalid rank: {rank}")
                    return
            except:
                self.state.set_invalid_move(reason=f"Invalid rank: {hint_value}")
                return
            
            for i, card in enumerate(target_hand):
                if card.rank == rank:
                    matching_positions.append(i)
                    if rank not in gs['hand_hints'][target_player][i]['ranks']:
                        gs['hand_hints'][target_player][i]['ranks'].append(rank)
        
        if not matching_positions:
            self.state.set_invalid_move(
                reason=f"No cards match that hint in target player's hand"
            )
            return
        
        # Consume info token
        gs['info_tokens'] -= 1
        
        # Announce the hint
        positions_str = ", ".join(map(str, matching_positions))
        hint_desc = f"{hint_type} {hint_value}"
        self.state.add_observation(
            message=f"Player {self.state.current_player_id} reveals to Player {target_player}: "
                   f"Cards at positions [{positions_str}] are {hint_desc}",
            observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
        )
    
    def _handle_play(self, match):
        """Handle a play card action."""
        gs = self.state.game_state
        position = int(match.group(1))
        
        # Validate position
        if position < 0 or position >= len(gs['player_hands'][self.state.current_player_id]):
            self.state.set_invalid_move(reason=f"Invalid card position: {position}")
            return
        
        # Get the card
        card = gs['player_hands'][self.state.current_player_id][position]
        
        # Check if it can be played
        current_rank = gs['fireworks'][card.suit]
        can_play = (card.rank == current_rank + 1)
        
        if can_play:
            # Successfully play the card
            gs['fireworks'][card.suit] = card.rank
            gs['score'] += 1
            
            self.state.add_observation(
                message=f"Player {self.state.current_player_id} successfully played {card}!",
                observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
            )
            
            # Bonus: completing a firework (playing a 5) gives back an info token
            if card.rank == 5 and gs['info_tokens'] < self.info_tokens_max:
                gs['info_tokens'] += 1
                self.state.add_observation(
                    message=f"Firework {card.suit.value} completed! Gained 1 info token.",
                    observation_type=ta.ObservationType.GAME_MESSAGE
                )
        else:
            # Failed play - lose life token
            gs['life_tokens'] -= 1
            gs['discard_pile'].append(card)
            
            self.state.add_observation(
                message=f"Player {self.state.current_player_id} incorrectly played {card}. "
                       f"Lost 1 life token!",
                observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
            )
        
        # Remove card and hints
        gs['player_hands'][self.state.current_player_id].pop(position)
        gs['hand_hints'][self.state.current_player_id].pop(position)
        
        # Draw new card if available
        if gs['deck']:
            new_card = gs['deck'].pop()
            gs['player_hands'][self.state.current_player_id].append(new_card)
            gs['hand_hints'][self.state.current_player_id].append({"colors": [], "ranks": []})
        elif gs['last_round_countdown'] == -1:
            # Deck empty - start last round countdown
            gs['last_round_countdown'] = self.state.num_players
    
    def _handle_discard(self, match):
        """Handle a discard action."""
        gs = self.state.game_state
        position = int(match.group(1))
        
        # Validate position
        if position < 0 or position >= len(gs['player_hands'][self.state.current_player_id]):
            self.state.set_invalid_move(reason=f"Invalid card position: {position}")
            return
        
        # Can't discard if info tokens are full
        if gs['info_tokens'] >= self.info_tokens_max:
            self.state.set_invalid_move(reason="Cannot discard when info tokens are full")
            return
        
        # Discard the card
        card = gs['player_hands'][self.state.current_player_id][position]
        gs['discard_pile'].append(card)
        gs['info_tokens'] += 1
        
        self.state.add_observation(
            message=f"Player {self.state.current_player_id} discarded {card}. "
                   f"Gained 1 info token.",
            observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
        )
        
        # Remove card and hints
        gs['player_hands'][self.state.current_player_id].pop(position)
        gs['hand_hints'][self.state.current_player_id].pop(position)
        
        # Draw new card if available
        if gs['deck']:
            new_card = gs['deck'].pop()
            gs['player_hands'][self.state.current_player_id].append(new_card)
            gs['hand_hints'][self.state.current_player_id].append({"colors": [], "ranks": []})
        elif gs['last_round_countdown'] == -1:
            # Deck empty - start last round countdown
            gs['last_round_countdown'] = self.state.num_players
    
    def _check_game_end(self):
        """Check if the game should end."""
        gs = self.state.game_state
        
        # Game ends if life tokens reach 0
        if gs['life_tokens'] <= 0:
            self.state.add_observation(
                message=f"Game Over! No life tokens remaining. Final score: {gs['score']}/25",
                observation_type=ta.ObservationType.GAME_MESSAGE
            )
            # In cooperative game, all players get same reward (normalized score)
            reward = gs['score'] / 25.0
            reward_dict = {pid: reward for pid in range(self.state.num_players)}
            self.state.set_game_outcome(
                reward_dict=reward_dict,
                reason=f"No life tokens. Score: {gs['score']}/25"
            )
            return
        
        # Game ends if all fireworks complete (perfect game)
        if all(gs['fireworks'][suit] == 5 for suit in self.suits):
            self.state.add_observation(
                message="Perfect Game! All fireworks completed! Score: 25/25",
                observation_type=ta.ObservationType.GAME_MESSAGE
            )
            reward_dict = {pid: 1.0 for pid in range(self.state.num_players)}
            self.state.set_game_outcome(
                reward_dict=reward_dict,
                reason="Perfect game! Score: 25/25"
            )
            return
        
        # Game ends after last round
        if gs['last_round_countdown'] > 0:
            gs['last_round_countdown'] -= 1
            if gs['last_round_countdown'] == 0:
                self.state.add_observation(
                    message=f"Game Over! Deck exhausted. Final score: {gs['score']}/25",
                    observation_type=ta.ObservationType.GAME_MESSAGE
                )
                reward = gs['score'] / 25.0
                reward_dict = {pid: reward for pid in range(self.state.num_players)}
                self.state.set_game_outcome(
                    reward_dict=reward_dict,
                    reason=f"Deck exhausted. Score: {gs['score']}/25"
                )
    
    def get_board_str(self) -> str:
        """Get a string representation of the game board."""
        gs = self.state.game_state
        
        lines = []
        lines.append("=" * 50)
        lines.append("HANABI GAME STATE")
        lines.append("=" * 50)
        
        # Resources
        lines.append(f"Life Tokens: {'♥' * gs['life_tokens']}{'♡' * (self.life_tokens_max - gs['life_tokens'])}")
        lines.append(f"Info Tokens: {'●' * gs['info_tokens']}{'○' * (self.info_tokens_max - gs['info_tokens'])}")
        lines.append(f"Deck: {len(gs['deck'])} cards remaining")
        lines.append("")
        
        # Fireworks
        lines.append("Fireworks:")
        for suit in self.suits:
            rank = gs['fireworks'][suit]
            display = " ".join([str(i) if i <= rank else "_" for i in range(1, 6)])
            lines.append(f"  {suit.value}: {display}")
        lines.append(f"Score: {gs['score']}/25")
        lines.append("")
        
        # Hands
        lines.append("Player Hands:")
        for pid in range(self.state.num_players):
            hand_str = " ".join([str(card) for card in gs['player_hands'][pid]])
            lines.append(f"  Player {pid}: {hand_str}")
        
        if gs['discard_pile']:
            lines.append("")
            lines.append(f"Discard Pile ({len(gs['discard_pile'])} cards)")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
