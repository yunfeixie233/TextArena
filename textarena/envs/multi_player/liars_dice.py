"""
Liar's Dice Game

In this game, $k$ players each roll a set number of dice (usually five), keeping their dice hidden from the other players.

**Gameplay:**

- Every player rolls their dice and keeps them hidden.
- Players take turns making bids on the total quantity of a face value (from 1 to 6) among all dice.
  - A bid consists of a quantity and a face value, e.g., "I bid three 4s", meaning there are at least three dice showing a face value of 4.
  - 1s are wild and can be used as any face value.
  - If every die a player has is different, their dice do not count towards the bid.
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

import random

import textarena as ta

BASE_PROMPT = """You are player {player_id}, you are playing the game liar's dice.
In liar's dice, players take turns making bids on the total quantity of a face value among all dice.
1s are wild and can be used as any face value.
On your turn, you can:
- Make a bid: Increase the quantity or the face value.
- Call the bluff: Challenge the previous bid.
The game ends when a bluff is called and resolved.

The minimum bid is 3 1s. To make a bid, use the format '[Bid] <quantity> <face_value>'.
To call a bluff, use the format '[Call]'.

Your dice: {dice}"""


class LiarsDice(ta.Env):
    """Liar's Dice game environment."""

    def __init__(self, num_dice: int = 5, num_players: int = 5):
        self.num_dice = num_dice
        self.num_players = num_players
        self.reset()

    def reset(self, seed: int = None) -> tuple[ta.Observation, ta.Info]:
        """Reset the environment to its initial state."""
        random.seed(seed)
        dice = [
            {i: [random.randint(1, 6) for _ in range(self.num_dice)]}
            for i in range(self.num_players)
        ]
        self.game_state = ta.State(
            render={"dice": dice},
            logs=[(ta.GAME_ID, "New game started.")],
            player_map={i: f"Player {i}" for i in range(self.num_players)},
            bid=None,
            dice=dice,
        )
        return (
            {i: [self.get_initial_prompt(dice[i], i)] for i in range(self.num_players)},
            {},
        )

    def get_initial_prompt(self, dice, player_id) -> ta.Message:
        """Returns a prompt for the player."""
        if player_id != 0:
            return ta.GAME_ID, BASE_PROMPT.format(player_id=player_id, dice=dice)
        return (
            ta.GAME_ID,
            f"{BASE_PROMPT.format(player_id=player_id, dice=dice)}\n\n It's your turn make the initial bid.",
        )

    def step(
        self, player_id: int, action: str
    ) -> tuple[ta.Observation, ta.Reward, bool, bool, ta.Info]:
        """Take a step in the environment."""
        message = (player_id, action)
        next_player = (player_id + 1) % self.num_players
        next_player_message = {
            _id: [(ta.GAME_ID, "It's your turn.")] if _id == next_player else []
            for _id in range(self.num_players)
        }
        base_rewards = {i: 0 for i in range(self.num_players)}
        if "[Call]" in action:
            if self.game_state["bid"] is None:
                base_rewards[player_id] = -1
                return (
                    {player_id: [message, (ta.GAME_ID, "No bids have been made yet.")]},
                    base_rewards,
                    True,
                    False,
                    {"reason": "No bids have been made yet."},
                )
            return self._resolve_bluff(message)
        elif "[Bid]" in action:
            action = action.split("[Bid]")[1].strip()
            if not self._update_bid(action):
                base_rewards[player_id] = -1
                return (
                    {player_id: [message, (ta.GAME_ID, "Invalid bid format.")]},
                    base_rewards,
                    True,
                    False,
                    {"reason": "Invalid bid format."},
                )
            return (
                {
                    _id: [message] + next_player_message[_id]
                    for _id in range(self.num_players)
                },
                base_rewards,
                False,
                False,
                {},
            )
        else:
            base_rewards[player_id] = -1
            return (
                {player_id: [message, (ta.GAME_ID, "Invalid action format.")]},
                base_rewards,
                True,
                False,
                {"reason": "Invalid action format."},
            )

    def _update_bid(self, action) -> bool:
        """Updates the bid, returning false if the bid is invalid"""
        quantity, face_value = action.split()
        quantity = int(quantity)
        face_value = int(face_value)
        if self.game_state["bid"] is None:
            self.game_state["bid"] = (quantity, face_value)
            return True
        prev_quantity, prev_face_value = self.game_state["bid"]
        prev_quantity = int(prev_quantity)
        prev_face_value = int(prev_face_value)
        if quantity < prev_quantity:
            return False, None, None
        if quantity == prev_quantity and face_value <= prev_face_value:
            return False
        self.game_state["bid"] = (quantity, face_value)
        return True

    def _resolve_bluff(self, call_message):
        """Resolve the bluff."""
        player_id = call_message[0]
        actual_counts = {i: 0 for i in range(1, 7)}
        for player in self.game_state["dice"]:
            if set(player.values()) == 5:
                continue  # Skip players with all different dice
            for die in player.values():
                if die == 1:
                    for i in range(1, 7):
                        actual_counts[i] += 1
                else:
                    actual_counts[die] += 1

        if actual_counts[self.game_state["bid"][1]] >= self.game_state["bid"][0]:
            loser = player_id  # the bluff caller
            message = (ta.GAME_ID, f"Player {loser} loses! The bid succeeded.")
        else:
            loser = player_id - 1 % self.num_players  # the player who made the bid
            message = (ta.GAME_ID, f"Player {loser} loses! The bid failed.")
        self.game_state.logs.append(message)
        message_obs = ({i: [call_message, message] for i in range(self.num_players)},)
        rewards = {
            i: 1 for i in range(self.num_players)
        }  # reward players who didn't die...
        rewards[loser] = -1

        return (
            message_obs,
            rewards,
            True,
            False,
            {},
        )

    def render(self):
        """Render the environment."""
        if self.game_state["bid"] is None:
            print("No bids have been made yet.")
        else:
            print(f"Current bid: {self.game_state['bid']}")
        print("Dice:")
        for i, player in enumerate(self.game_state["dice"]):
            print(f"Player {i}: {player}")
        print("\n")
