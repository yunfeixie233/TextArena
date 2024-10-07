"""
Liar's Dice Game

In this game, two players each roll a set number of dice (usually five), keeping their dice hidden from the other player.

**Gameplay:**

- Each player rolls their dice and keeps them hidden.
- Players take turns making bids on the total quantity of a face value (from 1 to 6) among all dice.
  - A bid consists of a quantity and a face value, e.g., "I bid three 4s", meaning there are at least three dice showing a face value of 4.
- On their turn, a player can:
  - **Make a higher bid**: Increase the quantity or the face value (if increasing the face value, the quantity must be at least the same).
  - **Call the bluff**: If a player believes the previous bid is false, they can challenge it by saying "Call".
- If a bluff is called:
  - All dice are revealed.
  - The actual counts are tallied.
  - If the bid is valid (there are at least as many of the face value as claimed), the bidder wins.
  - If the bid is invalid, the challenger wins.
- The game ends when a bluff is called and resolved.

**Key Rules:**

- Bids must increase in quantity or face value.
  - You can increase the quantity while keeping the face value the same or higher.
  - If you increase the face value, the quantity must be equal to or higher than the previous quantity.
- Players must use the correct action formats:
  - To make a bid: "[Bid] <quantity> <face_value>"
  - To call a bluff: "[Call]"
- Face values range from 1 to 6.

**Parameters:**

- `num_dice`: Number of dice each player rolls at the beginning (default is 5).

**Game Outcomes:**

- A player wins by successfully calling a bluff or by making a bid that the opponent believes and cannot challenge.
- A player loses if their bluff is called and the actual counts do not support their bid.
"""

from typing import Any, Dict, Optional, Tuple
import random
import re
import textarena as ta

class LiarsDiceEnv(ta.Env):
    def __init__(
        self,
        num_dice: Optional[int] = 5,
    ):
        """
        Initialize the Liar's Dice game environment.

        Args:
            num_dice (int): Number of dice each player rolls.
        """
        self.ENVIRONMENT_NAME = "Liar's Dice"
        self.num_dice = num_dice

        # Initialize game state variables
        self.game_state = {
            "turn": 0,
            "current_bid": {"quantity": 0, "face_value": 0},
            "dice_rolls": {0: [], 1: []},
            "logs": [],
            "render": [
                "turn", 
                ["current_bid","quantity"], 
                ["current_bid","face_value"], 
                ["dice_rolls", 0],
                ["dice_rolls", 1],
            ],
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

        self.game_state["turn"] = 0
        self.game_state["current_bid"] = {"quantity": 0, "face_value": 0}
        self.game_state["dice_rolls"] = {
            0: [random.randint(1, 6) for _ in range(self.num_dice)],
            1: [random.randint(1, 6) for _ in range(self.num_dice)],
        }
        self.game_state["logs"] = []

        # Generate initial prompts for both players
        observations = {
            0: self._generate_player_prompt(player_id=0),
            1: self._generate_player_prompt(player_id=1),
        }

        info = {
            "dice_rolls": self.game_state["dice_rolls"],
            "current_bid": self.game_state["current_bid"],
        }

        self.game_state["logs"].append("[GAME] New game started.")
        self.game_state["logs"].append(f"[GAME] Player 0 and Player 1 have rolled their dice.")

        return observations, info

    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for a player.

        Args:
            player_id (int): The player's ID.

        Returns:
            str: The initial prompt for the player.
        """
        dice = self.game_state["dice_rolls"][player_id]
        prompt = (
            f"You are Player {player_id} in Liar's Dice.\n"
            f"You have rolled {self.num_dice} dice: {', '.join(map(str, dice))}.\n"
            "Players take turns making bids on the total quantity of a face value among all dice.\n"
            "On your turn, you can either make a higher bid or call the opponent's bluff.\n"
            "Actions:\n"
            "- To make a bid: '[Bid] <quantity> <face_value>', e.g., '[Bid] 3 4'\n"
            "- To call a bluff: '[Call]'\n"
            "If you call a bluff, all dice are revealed:\n"
            "- If the actual quantity of the face value is less than the bid, you win.\n"
            "- If the actual quantity meets or exceeds the bid, you lose.\n"
            f"The current bid is: Quantity = {self.game_state['current_bid']['quantity']}, Face Value = {self.game_state['current_bid']['face_value']}\n"
            "It's your turn. What is your action?"
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
            action (str): The player's action.

        Returns:
            tuple: (observations, reward, truncated, terminated, info)
        """
        other_player_id = 1 - player_id
        terminated = False
        truncated = False
        reward = None
        info = {}

        self.game_state["turn"] += 1

        # Log the player's action
        self.game_state["logs"].append(f"[Player {player_id}] {action}")

        action_lower = action.strip().lower()

        # Check if the player is calling a bluff
        if "[call]" in action_lower:
            total_quantity = sum(
                dice.count(self.game_state["current_bid"]["face_value"])
                for dice in self.game_state["dice_rolls"].values()
            )
            bid_quantity = self.game_state["current_bid"]["quantity"]
            if total_quantity < bid_quantity:
                # Challenger wins
                terminated = True
                reward = {player_id: 1, other_player_id: -1}
                info["reason"] = (
                    f"Actual quantity of face value {self.game_state['current_bid']['face_value']} "
                    f"is {total_quantity}, less than the bid ({bid_quantity}). "
                    f"Player {player_id} wins."
                )
                self.game_state["logs"].append(f"[GAME] {info['reason']}")
            else:
                # Challenger loses
                terminated = True
                reward = {player_id: -1, other_player_id: 1}
                info["reason"] = (
                    f"Actual quantity of face value {self.game_state['current_bid']['face_value']} "
                    f"is {total_quantity}, meets or exceeds the bid ({bid_quantity}). "
                    f"Player {player_id} loses."
                )
                self.game_state["logs"].append(f"[GAME] {info['reason']}")

            # Reveal dice rolls
            self.game_state["logs"].append(f"[GAME] Dice are revealed:")
            self.game_state["logs"].append(f"  - Player 0's dice: {self.game_state['dice_rolls'][0]}")
            self.game_state["logs"].append(f"  - Player 1's dice: {self.game_state['dice_rolls'][1]}")
            observations = {player_id: action, other_player_id: action}
            return observations, reward, truncated, terminated, info

        # Check if the player is making a bid
        elif "[bid]" in action_lower:
            # Parse the new bid
            match = re.search(r'\[bid\]\s*(\d+)\s+(\d+)', action_lower)
            if not match:
                # Invalid bid format
                terminated = True
                reward = {player_id: -1, other_player_id: 0}
                info["reason"] = f"Invalid bid format. Player {player_id} did not provide quantity and face value."
                self.game_state["logs"].append(f"[GAME] {info['reason']}")
                observations = {player_id: action, other_player_id: action}
                return observations, reward, truncated, terminated, info

            new_quantity = int(match.group(1))
            new_face_value = int(match.group(2))

            # Validate face value
            if not (1 <= new_face_value <= 6):
                terminated = True
                reward = {player_id: -1, other_player_id: 0}
                info["reason"] = f"Invalid face value. Player {player_id} provided face value {new_face_value}, which is not between 1 and 6."
                self.game_state["logs"].append(f"[GAME] {info['reason']}")
                observations = {player_id: action, other_player_id: action}
                return observations, reward, truncated, terminated, info

            # Validate bid increase
            current_quantity = self.game_state["current_bid"]["quantity"]
            current_face_value = self.game_state["current_bid"]["face_value"]
            if (new_quantity < current_quantity) or (new_quantity == current_quantity and new_face_value <= current_face_value):
                terminated = True
                reward = {player_id: -1, other_player_id: 0}
                info["reason"] = "Invalid bid. New bid must have a higher quantity or higher face value."
                self.game_state["logs"].append(f"[GAME] {info['reason']}")
                observations = {player_id: action, other_player_id: action}
                return observations, reward, truncated, terminated, info

            # Update the current bid
            prev_bid = self.game_state["current_bid"].copy()
            self.game_state["current_bid"]["quantity"] = new_quantity
            self.game_state["current_bid"]["face_value"] = new_face_value
            info["info"] = (
                f"Player {player_id} increases the bid to Quantity = {new_quantity}, Face Value = {new_face_value} "
                f"(previous bid was Quantity = {prev_bid['quantity']}, Face Value = {prev_bid['face_value']})."
            )
            self.game_state["logs"].append(f"[GAME] {info['info']}")
            observations = {player_id: action, other_player_id: action}
            return observations, reward, truncated, terminated, info

        else:
            # Invalid action
            terminated = True
            reward = {player_id: -1, other_player_id: 0}
            info["reason"] = f"Invalid action. Player {player_id} must use '[Bid] <quantity> <face_value>' or '[Call]'."
            self.game_state["logs"].append(f"[GAME] {info['reason']}")
            observations = {player_id: action, other_player_id: action}
            return observations, reward, truncated, terminated, info

    def render(self):
        """
        Render the current game state.
        """
        print(f"Turn: {self.game_state['turn']}")
        current_bid = self.game_state["current_bid"]
        print(f"Current Bid: Quantity = {current_bid['quantity']}, Face Value = {current_bid['face_value']}")
        print("\nGame Logs:")
        for log in self.game_state["logs"]:
            print(log)
        print("\n")
