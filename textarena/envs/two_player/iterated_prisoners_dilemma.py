"""Environment for playing the game iterated prisoners dilemma with chat

We have two players, each of whom can choose to cooperate or defect.
The players are rewarded based on their choices and the choices of the other player.
The game is played for a random number of rounds.
The players can communicate with each other using chat messages.
"""

import re
import random
import textarena

MIN_TURNS = 1

IPD_PROMPT = """You are playing 'Iterated Prisoners Dilemma' with chat. You are Player {player_id}.
You can choose to 'cooperate' or 'defect' in each round.
Your goal is to maximize your score by choosing the best strategy.
You can also send chat messages to the other player.
The game will last for a random number of rounds.
You receive points based on the following rules:
- If both players cooperate, both get 3 points.
- If one player cooperates and the other defects, the defector gets 5 points and the cooperator gets 0 points.
- If both players defect, both get 1 point.
Good luck!"""

CHOICE_REGEX = r"Choice: (cooperate|defect)"


class IteratedPrisonersDilemma(textarena.Env):
    """Environment for playing the game iterated prisoners dilemma with chat."""

    def __init__(self, chat_turns_per_round, max_turns=30) -> None:
        """
        Initialize the environment.

        Args:
            chat_turns_per_round (int): Number of chat turns allowed per round.
            max_turns (int): Maximum number of rounds to play.
        """
        self.chat_turns_per_round = chat_turns_per_round + 1
        self.max_turns = max_turns
        self.num_rounds = max(int(random.betavariate(2, 5) * self.max_turns), MIN_TURNS)
        self.ENVIRONMENT_NAME = "Iterated Prisoners Dilemma"

        self.game_state = {
            "turn": 0,
            "sub_turn": 0,
            "max_turns": self.max_turns,
            "logs": [],
            "player_scores": {0: 0, 1: 0},
            "player_choices": {0: None, 1: None},
        }

    def reset(self, seed: int | None = None):
        """
        Reset the environment to its initial state.

        Args:
            seed (int | None): Seed for random number generator to ensure reproducibility.

        Returns:
            Tuple[Dict[int, str], Dict[int, Any]]: Initial observations for both players and info.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        self.game_state["turn"] = 0
        self.game_state["player_scores"] = {0: 0, 1: 0}
        self.game_state["sub_turn"] = 0
        self.game_state["logs"] = []
        self.game_state["player_choices"] = {0: None, 1: None}

        return (
            {
                0: self._generate_player_prompt(player_id=0),
                1: self._generate_player_prompt(player_id=1),
            },
            {
                "player_0_score": self.game_state["player_scores"][0],
                "player_1_score": self.game_state["player_scores"][1],
            },
        )

    def _generate_player_prompt(self, player_id: int) -> str:
        """Generate the prompt for each player, providing them with instructions.
        Args:
            player_id (int): ID of the player (0 or 1).
        Returns:
            str: Initial prompt for the player."""

        base_prompt = IPD_PROMPT.format(player_id=player_id)

        # append the history of chat messages and choices
        chat_history = [
            f"Player {log['player_id']}: {log['message']}"
            for log in self.game_state["logs"]
        ]

        # finally add the prompt for the current turn
        chat_turn = self.game_state["turn"] % self.chat_turns_per_round != 0
        if chat_turn:
            return (
                base_prompt
                + "\n".join(chat_history)
                + "\n\nChat with the other player."
            )
        return (
            base_prompt
            + "\n".join(chat_history)
            + "\n\nMake your choice: 'cooperate' or 'defect'. (reply with either Choice: cooperate or Choice: defect)"
        )

    def compute_scores(self) -> tuple[int, int]:
        """Compute the scores for the current round based on the players' choices.

        Returns:
            Tuple[int, int]: Scores for player 0 and player 1.
        """
        assert self.game_state["player_choices"][0] is not None
        assert self.game_state["player_choices"][1] is not None
        choices = self.game_state["player_choices"]
        if choices[0] == "cooperate" and choices[1] == "cooperate":
            return 3, 3
        if choices[0] == "cooperate" and choices[1] == "defect":
            return 0, 5
        if choices[0] == "defect" and choices[1] == "cooperate":
            return 5, 0
        if choices[0] == "defect" and choices[1] == "defect":
            return 1, 1

    def step(
        self, player_id: int, action: str
    ) -> tuple[dict[int, str], dict[int, any], bool, bool, dict[int, any]]:
        """Execute a step in the environment.

        Args:
            player_id (int): ID of the player making the action.
            action (str): Action taken by the player.

        Returns:
            Tuple[Dict[int, str], Dict[int, Any], bool, bool, Dict[int, Any]]: Observations, info, truncated, and extra info.
        """
        observations, reward, truncated, terminated, info, scores = (
            None,
            None,
            False,
            False,
            None,
            None,
        )
        ## first figure out if it's a chat turn or a choice turn
        chat_turn = self.game_state["turn"] % self.chat_turns_per_round != 0
        if chat_turn:
            self.game_state["logs"].append({"player_id": player_id, "message": action})
            self.game_state["sub_turn"] = 1 - self.game_state["sub_turn"]
        else:  # they should have made a choice
            action_match = re.match(CHOICE_REGEX, action)
            if action_match is None:
                terminated = True
                info = {
                    "reason": f"Player {player_id} made an invalid choice: {action}. It should be 'cooperate' or 'defect'."
                }
                reward = {player_id: -1, 1 - player_id: -1}
                return {}, reward, truncated, terminated, info
            action = action_match.group(1)
            self.game_state["player_choices"][player_id] = action
            self.game_state["sub_turn"] = 1 - self.game_state["sub_turn"]
            if self.game_state["sub_turn"] == 0:
                scores = self.compute_scores()
                self.game_state["player_scores"][0] += scores[0]
                self.game_state["player_scores"][1] += scores[1]
                self.game_state["logs"].append(
                    {
                        "player_id": "System",
                        "message": f"Player 0 chose {self.game_state['player_choices'][0]}, Player 1 chose {self.game_state['player_choices'][1]}.",
                    }
                )
                self.game_state["logs"].append(
                    {
                        "player_id": "System",
                        "message": f"Player 0 score: {self.game_state['player_scores'][0]}, Player 1 score: {self.game_state['player_scores'][1]}.",
                    }
                )
                self.game_state["player_choices"] = {0: None, 1: None}
        if self.game_state["sub_turn"] == 1:
            self.game_state["turn"] += 1
        observations = {
            0: self._generate_player_prompt(player_id=0),
            1: self._generate_player_prompt(player_id=1),
        }
        truncated = self.game_state["turn"] >= self.num_rounds
        terminated = False

        if truncated:
            info = {"reason": "Game over: maximum number of rounds reached."}
            reward = self.game_state["player_scores"]
        else:
            info = {}
            reward = None
        return observations, reward, truncated, terminated, info

    def render(self):
        """Render minimal game state."""
        turn_info = f"Turn: {self.game_state['turn'] + 1}/{self.num_rounds}"
        player_0_info = f"Player 0 Score: {self.game_state['player_scores'][0]}"
        player_1_info = f"Player 1 Score: {self.game_state['player_scores'][1]}"
        print(f"{turn_info}\n{player_0_info}\n{player_1_info}\n")
