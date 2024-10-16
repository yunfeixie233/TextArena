import random
from typing import Optional, Tuple
import textarena as ta


class CodenamesEnv(ta.Env):
    """Environment for playing the game Codenames."""

    environment_name = "Codenames"

    def __init__(self):
        self.game_state = ta.State(
            render={},
            logs=[],
            player_map={
                1: "Blue Spymaster",
                2: "Blue Guesser",
                3: "Red Spymaster",
                4: "Red Guesser",
            },
        )
        self.words = [
            "apple",
            "banana",
            "computer",
            "sky",
            "cat",
            "dog",
            "tree",
            "book",
            "chair",
            "moon",
        ]
        self.blue_words = random.sample(self.words, 4)
        self.red_words = random.sample(
            [w for w in self.words if w not in self.blue_words], 4
        )
        self.neutral_words = [
            w for w in self.words if w not in self.blue_words + self.red_words
        ]
        self.turn = 1  # Blue Spymaster goes first
        self.terminated = False

    def reset(
        self, seed: Optional[int] = None
    ) -> Tuple[Optional[ta.Observation], Optional[ta.Info]]:
        if seed is not None:
            random.seed(seed)

        self.game_state.logs = [
            (-1, "Game has started. Blue Spymaster, provide a clue.")
        ]
        self.turn = 1  # Blue Spymaster's turn
        self.terminated = False

        return {
            1: [(-1, "Waiting for Blue Spymaster")],
            2: [(-1, "Waiting for Blue Spymaster")],
            3: [(-1, "Waiting for Blue Spymaster")],
            4: [(-1, "Waiting for Blue Spymaster")],
        }, {}

    def step(
        self, player_id: int, action: str
    ) -> Tuple[ta.Observation, ta.Reward, bool, bool, ta.Info]:
        if self.terminated:
            return {}, {player_id: 0}, False, True, {}

        if player_id != self.turn:
            return {}, {player_id: -1}, False, False, {"message": "Not your turn"}

        # Spymaster's turn to give a clue
        if player_id in [1, 3]:  # Blue or Red Spymaster
            clue, number = action.split(":")
            number = int(number)
            self.game_state.logs.append(
                (player_id, f"Spymaster gave the clue: {clue} for {number} words")
            )
            self.turn = (
                2 if player_id == 1 else 4
            )  # Switch to Blue Guesser or Red Guesser
            observations = {
                1: [(player_id, f"Clue given: {clue} for {number} words")],
                2: [
                    (player_id, f"Clue from your Spymaster: {clue} for {number} words")
                ],
                3: [(player_id, f"Clue given: {clue} for {number} words")],
                4: [
                    (player_id, f"Clue from enemy Spymaster: {clue} for {number} words")
                ],
            }
            reward = {1: 0, 2: 0, 3: 0, 4: 0}

        # Guesser's turn to guess a word
        else:
            guess = action
            team = "blue" if player_id == 2 else "red"
            opponent_team = "red" if team == "blue" else "blue"

            if guess in self.blue_words and team == "blue":
                self.blue_words.remove(guess)
                self.game_state.logs.append(
                    (
                        player_id,
                        f"{team.capitalize()} Guesser guessed: {guess}. Correct!",
                    )
                )
                reward = {1: 1, 2: 1, 3: 0, 4: 0}
            elif guess in self.red_words and team == "red":
                self.red_words.remove(guess)
                self.game_state.logs.append(
                    (
                        player_id,
                        f"{team.capitalize()} Guesser guessed: {guess}. Correct!",
                    )
                )
                reward = {1: 0, 2: 0, 3: 1, 4: 1}
            elif guess in self.neutral_words:
                self.game_state.logs.append(
                    (player_id, f"Guesser guessed: {guess}. Neutral word.")
                )
                reward = {1: 0, 2: 0, 3: 0, 4: 0}
                # Neutral guess means it's the other team's turn
                self.turn = 3 if player_id == 2 else 1
            else:
                self.terminated = True
                reward = (
                    {1: -1, 2: -1, 3: 1, 4: 1}
                    if team == "blue"
                    else {1: 1, 2: 1, 3: -1, 4: -1}
                )
                self.game_state.logs.append(
                    (-1, f"Game over! {team.capitalize()} Guesser guessed wrong.")
                )
                observations = {
                    1: [(-1, f"Game over! {team.capitalize()} team loses.")],
                    2: [(-1, f"Game over! {team.capitalize()} team loses.")],
                    3: [(-1, f"Game over! {opponent_team.capitalize()} team wins!")],
                    4: [(-1, f"Game over! {opponent_team.capitalize()} team wins!")],
                }
                return observations, reward, False, True, {}

            if not self.blue_words or not self.red_words:
                self.terminated = True
                winner = "Blue" if not self.blue_words else "Red"
                self.game_state.logs.append((-1, f"{winner} team wins!"))
                reward = (
                    {1: 1, 2: 1, 3: 0, 4: 0}
                    if winner == "Blue"
                    else {1: 0, 2: 0, 3: 1, 4: 1}
                )
                observations = {
                    1: [(-1, f"{winner} team wins!")],
                    2: [(-1, f"{winner} team wins!")],
                    3: [(-1, f"{winner} team wins!")],
                    4: [(-1, f"{winner} team wins!")],
                }
                return observations, reward, False, True, {}

            self.turn = (
                1 if player_id == 2 else 3
            )  # Switch turns: Blue or Red Spymaster
            observations = {
                1: [(player_id, f"Guesser guessed: {guess}.")],
                2: [(player_id, f"Guesser guessed: {guess}.")],
                3: [(player_id, f"Guesser guessed: {guess}.")],
                4: [(player_id, f"Guesser guessed: {guess}.")],
            }

        truncated = False
        return observations, reward, truncated, self.terminated, {}

    def render(self):
        for i, log in self.game_state.logs:
            if i == -1:
                print(f"Game: {log}")
            else:
                print(f"Player {self.game_state.player_map[i]}: {log}")
