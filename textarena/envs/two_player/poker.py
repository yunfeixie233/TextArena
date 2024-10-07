"""
Simplified Texas Hold'em Poker Game

In this simplified version of Texas Hold'em Poker, two players compete over a fixed number of rounds.

**Gameplay:**

- **Starting Chips**: Both players start with an equal number of chips.
- **Rounds**: The game is played over a fixed number of rounds.
- **Betting**:
  - Each round begins with both players placing an **ante** into the pot.
  - Players are dealt two private cards (hole cards).
  - A set of five community cards is dealt face-up.
  - Players can choose to **bet**, **call**, **raise**, **fold** or **check** during betting phases.
  - Betting continues until one player folds, or both **check**
- **Hand Ranking**: Standard Poker hand rankings are used to determine the winner.
- **Showdown**:
  - If both players bet or call, a showdown occurs where the best hand wins the pot.
  - If a player folds, the other player wins the pot without a showdown.

**Key Rules:**

- **Betting Actions**:
  - **[Bet] <amount>**: Place a bet of the specified amount.
  - **[Call]**: Match the opponent's bet.
  - **[Raise] <amount>**: Increase the bet by the specified amount.
  - **[Check]**: Check
  - **[Fold]**: Surrender the hand and forfeit any bets placed.
- **Hand Evaluation**:
  - Hands are evaluated using standard Poker hand rankings.
  - Each player's best possible hand is determined from their hole cards and the community cards.

**Parameters:**

- `starting_chips`: The number of chips each player starts with.
- `fixed_bet`: The fixed amount for bets and raises.
- `num_rounds`: The number of rounds to play.

**Game Outcomes:**

- The player with the most chips at the end of all rounds wins the game.
- A player can also win if the opponent runs out of chips before the rounds are completed.
"""
from typing import Any, Dict, Optional, Tuple
import random
import re
import textarena as ta


class SimplifiedPokerEnv(ta.Env):
    def __init__(
        self,
        starting_chips: int = 100,
        fixed_bet: int = 10,
        num_rounds: int = 5,
    ):
        """
        Initialize the Simplified Texas Hold'em Poker environment.
        Args:
            starting_chips (int): The number of chips each player starts with.
            fixed_bet (int): The fixed amount for bets and raises.
            num_rounds (int): The number of rounds to play.
        """
        self.ENVIRONMENT_NAME = "SimplifiedTexasHoldemPoker"
        
        self.starting_chips = starting_chips
        self.fixed_bet = fixed_bet
        self.num_rounds = num_rounds
        
        self.suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        
        self.game_state = {
            "round": 0,
            "max_rounds": self.num_rounds,
            "player_chips": {0: self.starting_chips, 1: self.starting_chips},
            "current_pot": 0,
            "community_cards": [],
            "player_hands": {0: [], 1: []},
            "current_bet": 0,
            "player_bets": {0: 0, 1: 0},
            "current_player": 0,  # Whose turn it is
            "last_action": {0: None, 1: None},
            "logs": [],
            "render": [
                "round", "max_rounds",
                ["player_chips", 0], ["player_chips", 1],
                "current_pot", "community_cards",
                ["player_hands", 0], ["player_hands", 1],
                "current_bet"
            ]
        }
        
    def reset(
        self,
        seed: Optional[int] = None
    ) -> Tuple[Optional[Dict[int, str]], Dict[int, Any]]:
        """
        Reset the game to its initial state.
        Args:
            seed (Optional[int]): Seed for random number generator to ensure reproducibility.
        Returns:
            Tuple[Dict[int, str], Dict[int, Any]]: Initial prompts for both players and additional info.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        self.game_state["round"] = 0
        self.game_state["player_chips"] = {0: self.starting_chips, 1: self.starting_chips}
        self.game_state["current_pot"] = 0
        self.game_state["current_bet"] = 0
        self.game_state["player_bets"] = {0: 0, 1: 0}
        self.game_state["current_player"] = 0
        self.game_state["last_action"] = {0: None, 1: None}

        # Start the first round
        self._start_new_round()
        
        # Generate initial prompts for both players
        observations = {
            0: self._generate_player_prompt(0),
            1: self._generate_player_prompt(1)
        }
        
        info = {}
        
        self.game_state["logs"].append("[GAME] Game has been reset.")
        
        return observations, info
    
    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for a player.
        Args:
            player_id (int): ID of the player (0 or 1).
        Returns:
            str: The initial prompt for the player.
        """
        hole_cards = self.game_state["player_hands"][player_id]
        community_cards = self.game_state["community_cards"]
        chips = self.game_state["player_chips"][player_id]
        pot = self.game_state["current_pot"]
        prompt = (
            f"You are Player {player_id} in the Simplified Texas Hold'em Poker Game.\n"
            f"You have {chips} chips.\n"
            f"The current pot is {pot} chips.\n"
            f"Your hole cards are: {self._format_cards(hole_cards)}\n"
            f"The community cards are: {self._format_cards(community_cards)}\n"
            "At each turn, you can take one of the following actions:\n"
            "  - [Bet] <amount>: Place a bet of the specified amount.\n"
            "  - [Call]: Match the opponent's bet.\n"
            "  - [Raise] <amount>: Increase the bet by the specified amount.\n"
            "  - [Check]: Check.\n"
            "  - [Fold]: Surrender the hand and forfeit any bets placed.\n"
            "Use these actions to play the game.\n"
        )
        return prompt
    
    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[Dict[int, str]],  # observations
        Optional[Dict[int, int]],  # reward
        bool,  # truncated
        bool,  # terminated
        Dict[str, Any],  # info
    ]:
        """
        Process the player's action.
        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's message or action.
        Returns:
            tuple: (observations, reward, truncated, terminated, info)
        """
        other_player_id = 1 - player_id
        action_stripped = action.strip()
        terminated = False
        truncated = False
        reward = None
        info = {}
        observations = {}

        print(action)
        
        # Check if it's the player's turn
        if self.game_state["current_player"] != player_id:
            # Not player's turn
            observations[player_id] = "It's not your turn."
            return observations, reward, truncated, terminated, info
        
        # Parse the action
        action_type, amount = self._parse_action(action)
        if action_type is None:
            # Invalid action
            observations[player_id] = "Invalid action. Please choose a valid action."
            return observations, reward, truncated, terminated, info
        
        self.game_state["logs"].append(f"Player {player_id} action: {action}")
        
        # Process the action
        if action_type == "fold":
            # Player folds, opponent wins the pot
            self.game_state["player_chips"][other_player_id] += self.game_state["current_pot"]
            self.game_state["current_pot"] = 0
            self.game_state["logs"].append(f"Player {player_id} folds. Player {other_player_id} wins the pot.")
            # Check if game over
            terminated = self._check_game_over()
            if not terminated:
                # Start new round
                self._start_new_round()
                # Generate observations
                observations = {
                    0: self._generate_player_prompt(0),
                    1: self._generate_player_prompt(1)
                }
            else:
                # Game over, determine winner
                winner_id = self._determine_winner()
                reward = {winner_id: 1, 1 - winner_id: -1}
                observations[0] = f"Game over. Player {winner_id} wins."
                observations[1] = f"Game over. Player {winner_id} wins."
        elif action_type == "check":
            # Player checks
            self.game_state["last_action"][player_id] = "check"
            self.game_state["logs"].append(f"Player {player_id} checks.")
            # If both players have checked and bets are equal, proceed to showdown
            if self.game_state["last_action"][other_player_id] == "check" and self.game_state["player_bets"][0] == self.game_state["player_bets"][1]:
                self.game_state["logs"].append("Both players have checked. Proceeding to showdown.")
                self._proceed_to_showdown()
                # Check if game over
                terminated = self._check_game_over()
                if not terminated:
                    # Start new round
                    self._start_new_round()
                    # Generate observations
                    observations = {
                        0: self._generate_player_prompt(0),
                        1: self._generate_player_prompt(1)
                    }
                else:
                    # Game over, determine winner
                    winner_id = self._determine_winner()
                    reward = {winner_id: 1, 1 - winner_id: -1}
                    observations[0] = f"Game over. Player {winner_id} wins."
                    observations[1] = f"Game over. Player {winner_id} wins."
            else:
                # Switch turn to other player
                self.game_state["current_player"] = other_player_id
                observations[other_player_id] = f"Player {player_id} checks."
        elif action_type == "bet":
            bet_amount = amount
            # Check if player has enough chips
            if self.game_state["player_chips"][player_id] < bet_amount:
                observations[player_id] = "You don't have enough chips to bet that amount."
                return observations, reward, truncated, terminated, info
            # Update game state
            self.game_state["player_chips"][player_id] -= bet_amount
            self.game_state["player_bets"][player_id] += bet_amount
            self.game_state["current_pot"] += bet_amount
            self.game_state["current_bet"] = self.game_state["player_bets"][player_id]
            self.game_state["last_action"][player_id] = "bet"
            self.game_state["logs"].append(f"Player {player_id} bets {bet_amount} chips.")
            # Switch turn to other player
            self.game_state["current_player"] = other_player_id
            observations[other_player_id] = f"Player {player_id} bets {bet_amount} chips."
        elif action_type == "call":
            # Check if there's a current bet to call
            amount_to_call = self.game_state["player_bets"][other_player_id] - self.game_state["player_bets"][player_id]
            if amount_to_call <= 0:
                observations[player_id] = "There's no bet to call. You can check or bet."
                return observations, reward, truncated, terminated, info
            # Check if player has enough chips
            if self.game_state["player_chips"][player_id] < amount_to_call:
                observations[player_id] = "You don't have enough chips to call."
                return observations, reward, truncated, terminated, info
            # Update game state
            self.game_state["player_chips"][player_id] -= amount_to_call
            self.game_state["player_bets"][player_id] += amount_to_call
            self.game_state["current_pot"] += amount_to_call
            self.game_state["last_action"][player_id] = "call"
            self.game_state["logs"].append(f"Player {player_id} calls.")
            # If bets are equal and both players have acted, proceed to showdown
            if self.game_state["player_bets"][player_id] == self.game_state["player_bets"][other_player_id]:
                self.game_state["logs"].append("Both players have matched bets. Proceeding to showdown.")
                self._proceed_to_showdown()
                # Check if game over
                terminated = self._check_game_over()
                if not terminated:
                    # Start new round
                    self._start_new_round()
                    # Generate observations
                    observations = {
                        0: self._generate_player_prompt(0),
                        1: self._generate_player_prompt(1)
                    }
                else:
                    # Game over, determine winner
                    winner_id = self._determine_winner()
                    reward = {winner_id: 1, 1 - winner_id: -1}
                    observations[0] = f"Game over. Player {winner_id} wins."
                    observations[1] = f"Game over. Player {winner_id} wins."
            else:
                # Switch turn to other player
                self.game_state["current_player"] = other_player_id
                observations[other_player_id] = f"Player {player_id} calls."
        elif action_type == "raise":
            raise_amount = amount
            amount_to_call = self.game_state["player_bets"][other_player_id] - self.game_state["player_bets"][player_id]
            total_amount = amount_to_call + raise_amount
            # Check if player has enough chips
            if self.game_state["player_chips"][player_id] < total_amount:
                observations[player_id] = "You don't have enough chips to raise that amount."
                return observations, reward, truncated, terminated, info
            # Update game state
            self.game_state["player_chips"][player_id] -= total_amount
            self.game_state["player_bets"][player_id] += total_amount
            self.game_state["current_pot"] += total_amount
            self.game_state["current_bet"] = self.game_state["player_bets"][player_id]
            self.game_state["last_action"][player_id] = "raise"
            self.game_state["logs"].append(f"Player {player_id} raises by {raise_amount} chips.")
            # Switch turn to other player
            self.game_state["current_player"] = other_player_id
            observations[other_player_id] = f"Player {player_id} raises by {raise_amount} chips."
        else:
            observations[player_id] = "Invalid action."
            return observations, reward, truncated, terminated, info
        
        return observations, reward, truncated, terminated, info
    
    def _parse_action(self, action_str: str) -> Tuple[Optional[str], Optional[int]]:
        """
        Parse the player's action string.
        Returns a tuple of (action_type, amount).
        """
        action_str = action_str.strip()
        # Patterns
        fold_pattern = re.compile(r'\[Fold\]', re.IGNORECASE)
        check_pattern = re.compile(r'\[Check\]', re.IGNORECASE)
        call_pattern = re.compile(r'\[Call\]', re.IGNORECASE)
        bet_pattern = re.compile(r'\[Bet\]\s*(\d+)', re.IGNORECASE)
        raise_pattern = re.compile(r'\[Raise\]\s*(\d+)', re.IGNORECASE)
        
        if fold_pattern.search(action_str):
            return "fold", None
        elif check_pattern.search(action_str):
            return "check", None
        elif call_pattern.search(action_str):
            return "call", None
        elif bet_pattern.search(action_str):
            amount = int(bet_pattern.search(action_str).group(1))
            return "bet", amount
        elif raise_pattern.search(action_str):
            amount = int(raise_pattern.search(action_str).group(1))
            return "raise", amount
        else:
            return None, None
    
    def _start_new_round(self):
        """
        Starts a new round in the game.
        """
        self.deck = self._create_deck()
        random.shuffle(self.deck)
        
        self.game_state["round"] += 1
        self.game_state["phase"] = "betting"
        self.game_state["current_pot"] = 0
        self.game_state["current_bet"] = 0
        self.game_state["player_bets"] = {0: 0, 1: 0}
        self.game_state["last_action"] = {0: None, 1: None}
        self.game_state["community_cards"] = []
        self.game_state["player_hands"] = {0: [], 1: []}
        self.game_state["logs"].append(f"[GAME] Starting Round {self.game_state['round']}")
        
        # Players ante up
        ante = self.fixed_bet
        for player_id in [0, 1]:
            self.game_state["player_chips"][player_id] -= ante
            self.game_state["current_pot"] += ante
            self.game_state["logs"].append(f"Player {player_id} antes up {ante} chips.")
            self.game_state["player_bets"][player_id] = ante
            
        # Deal hole cards to players
        for player_id in [0, 1]:
            self.game_state["player_hands"][player_id] = [self.deck.pop(), self.deck.pop()]
            self.game_state["logs"].append(f"Player {player_id} receives two hole cards.")
            
        # Deal community cards
        self.game_state["community_cards"] = [self.deck.pop() for _ in range(5)]
        self.game_state["logs"].append(f"Community cards are dealt.")
        
        # Set current player (alternating)
        self.game_state["current_player"] = self.game_state["round"] % 2  # Alternate who starts
    
    def _proceed_to_showdown(self):
        """
        Determine the winner of the round and award the pot.
        """
        # Evaluate hands
        player0_hand = self.game_state["player_hands"][0] + self.game_state["community_cards"]
        player1_hand = self.game_state["player_hands"][1] + self.game_state["community_cards"]
        
        player0_rank = self._evaluate_hand(player0_hand)
        player1_rank = self._evaluate_hand(player1_hand)
        
        if player0_rank > player1_rank:
            winner_id = 0
            self.game_state["logs"].append(f"Player {winner_id} wins the round with a better hand.")
        elif player1_rank > player0_rank:
            winner_id = 1
            self.game_state["logs"].append(f"Player {winner_id} wins the round with a better hand.")
        else:
            # Tie, split pot
            self.game_state["player_chips"][0] += self.game_state["current_pot"] // 2
            self.game_state["player_chips"][1] += self.game_state["current_pot"] // 2
            self.game_state["logs"].append("It's a tie. Pot is split.")
            self.game_state["current_pot"] = 0
            return
        
        self.game_state["player_chips"][winner_id] += self.game_state["current_pot"]
        self.game_state["current_pot"] = 0
    
    def _evaluate_hand(self, hand):
        """
        Evaluate the poker hand and return a numeric value representing the hand strength.
        Higher value means better hand.
        """
        rank_values = {rank: index for index, rank in enumerate(self.ranks, 2)}
        # Count occurrences of each rank
        ranks_in_hand = [card['rank'] for card in hand]
        rank_counts = {}
        for rank in ranks_in_hand:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        # Check for pairs, three of a kind, four of a kind, etc.
        counts = list(rank_counts.values())
        counts.sort(reverse=True)
        
        # Check for flush
        suits_in_hand = [card['suit'] for card in hand]
        suit_counts = {}
        for suit in suits_in_hand:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
        flush = any(count >= 5 for count in suit_counts.values())
        
        # Check for straight
        rank_indices = sorted(set(rank_values[rank] for rank in ranks_in_hand))
        straight = False
        for i in range(len(rank_indices) - 4):
            if rank_indices[i] + 4 == rank_indices[i + 4]:
                straight = True
                break
        # Special case for Ace-low straight
        if set([2, 3, 4, 5, 14]).issubset(set(rank_values[rank] for rank in ranks_in_hand)):
            straight = True
        
        # Determine hand rank
        if flush and straight:
            hand_strength = 8  # Straight Flush
        elif counts[0] == 4:
            hand_strength = 7  # Four of a Kind
        elif counts[0] == 3 and counts[1] == 2:
            hand_strength = 6  # Full House
        elif flush:
            hand_strength = 5  # Flush
        elif straight:
            hand_strength = 4  # Straight
        elif counts[0] == 3:
            hand_strength = 3  # Three of a Kind
        elif counts[0] == 2 and counts[1] == 2:
            hand_strength = 2  # Two Pair
        elif counts[0] == 2:
            hand_strength = 1  # One Pair
        else:
            hand_strength = 0  # High Card
        
        return hand_strength
    
    def _check_game_over(self):
        """
        Check if the game is over.
        """
        # Game is over if a player runs out of chips or max rounds reached
        if self.game_state["player_chips"][0] <= 0:
            self.game_state["logs"].append("Player 0 has run out of chips. Player 1 wins the game.")
            return True
        if self.game_state["player_chips"][1] <= 0:
            self.game_state["logs"].append("Player 1 has run out of chips. Player 0 wins the game.")
            return True
        if self.game_state["round"] >= self.game_state["max_rounds"]:
            self.game_state["logs"].append("Maximum number of rounds reached.")
            return True
        return False
    
    def _determine_winner(self):
        """
        Determine the winner of the game.
        """
        if self.game_state["player_chips"][0] > self.game_state["player_chips"][1]:
            return 0
        elif self.game_state["player_chips"][1] > self.game_state["player_chips"][0]:
            return 1
        else:
            # It's a tie
            return -1  # Indicates tie
    
    def _format_cards(self, cards):
        """
        Format a list of card dictionaries into a string.
        """
        return ', '.join([f"{card['rank']} of {card['suit']}" for card in cards])
    
    def _create_deck(self) -> list:
        """
        Create a standard 52-card deck.
        """
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                card = {'rank': rank, 'suit': suit}
                deck.append(card)
        return deck
    
    def render(self):
        """
        Render the current game state.
        This method should be called externally to display the game state.
        """
        print(f"Round {self.game_state['round']}/{self.game_state['max_rounds']}")
        print(f"Pot: {self.game_state['current_pot']} chips")
        print("Player Chips:")
        for player_id in [0, 1]:
            print(f"  Player {player_id}: {self.game_state['player_chips'][player_id]} chips")
        print("\nCommunity Cards:")
        print(f"  {self._format_cards(self.game_state['community_cards'])}")
        print("\nPlayer Hands:")
        for player_id in [0, 1]:
            print(f"  Player {player_id}: {self._format_cards(self.game_state['player_hands'][player_id])}")
        print("\nAction Logs:")
        for log in self.game_state["logs"]:
            print(f"  - {log}")
        print("\n")
