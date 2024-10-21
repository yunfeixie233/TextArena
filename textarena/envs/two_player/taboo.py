"""
Taboo Game

In this game, there are two players: the Clue Giver and the Guesser.

**Gameplay:**

- The Clue Giver is provided with a secret word (the word to guess) and a list of taboo words.
- The Clue Giver must provide clues to the Guesser without using the taboo words or the word to guess.
- The Guesser tries to guess the secret word based on the clues provided.
- If the Guesser correctly guesses the word, both players win.
- The game ends if the Clue Giver uses a taboo word or the word to guess, or if the turn limit is reached without a correct guess.

**Key Rules:**

- The Clue Giver must not use any of the taboo words or the word to guess in their clues.
- The Guesser can make guesses based on the clues provided.
- The game continues until the Guesser guesses correctly, the Clue Giver violates a rule, or the turn limit is reached.

**Parameters:**

- `max_turns`: The maximum number of turns before the game ends.

**Game Outcomes:**

- **Both players win**: If the Guesser correctly guesses the word.
- **Clue Giver loses**: If they use a taboo word or the word to guess in their clue.
- **Both players lose**: If the turn limit is reached without a correct guess.
"""

import json
import os
import random
import re
from typing import Optional, Tuple, Dict, Any

import textarena as ta


class TabooEnv(ta.Env):
    """Environment for the Taboo game."""

    def __init__(
        self,
        categories: list[str],
        max_turns: Optional[int] = 10,
    ):
        """
        Initialize the Taboo game.

        Roles:
            - Player 0 is the Clue Giver
            - Player 1 is the Guesser

        Args:
            max_turns (int): Maximum number of turns before the game ends.
        """
        self.environment_name = "Taboo"
        self.categories = categories

        # Load the data
        self._load_data()

        # Initialize game state
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
            render_keys=["word_to_guess", "taboo_words"]
        )

    def _load_data(self):
        """
        Load words and their taboo words from JSON files.
        """
        file_path = os.path.join(
            "textarena", "envs", "two_player", "data", "taboo_words.json"
        )

        # Load all data from JSON files
        with open(file_path, "r", encoding="utf-8") as f:
            full_data = json.load(f)

        # subsample to the legal keys
        self.data = {}
        for category in self.categories:
            self.data.update(full_data[category])

    def reset(
        self, seed: Optional[int] = None
    ) -> Tuple[Optional[ta.Observation], ta.Info]:
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


        game_state = {}
        game_state["word_to_guess"], game_state["taboo_words"] = (
            random.choice(list(self.data.items()))
        )

        # Generate initial prompts for both players
        observations = {
            0: [(ta.GAME_ID, self._generate_clue_giver_prompt(game_state=game_state))],  # Player 0 is the Clue Giver
            1: [(ta.GAME_ID, self._generate_guesser_prompt())],  # Player 1 is the Guesser
        }

        info = {
            "word_to_guess": game_state["word_to_guess"],
            "taboo_words": game_state["taboo_words"],
        }

        self.state.reset(
            game_state=game_state,
            initial_logs=[
                (ta.GAME_ID, "Game started.")
            ]
        )

        return observations, info

    def _generate_clue_giver_prompt(self, game_state:Dict[str, Any]) -> ta.Message:
        """
        Generate the initial prompt for the Clue Giver.

        Returns:
            str: Initial prompt for the Clue Giver.
        """
        prompt = (
            f"You are Player 0, the Clue Giver in the Taboo game.\n"
            f"The word to guess is '{game_state['word_to_guess']}'.\n"
            f"Taboo words: {', '.join(game_state['taboo_words'])}.\n"
            "Your goal is to provide clues to the Guesser without using the taboo words or the word to guess.\n"
            f"You have {self.state.max_turns} turns to help the Guesser guess the word.\n"
            "On your turn, simply type your clue.\n"
        )
        return prompt

    def _generate_guesser_prompt(self) -> ta.Message:
        """
        Generate the initial prompt for the Guesser.

        Returns:
            str: Initial prompt for the Guesser.
        """
        prompt = (
            "You are Player 1, the Guesser in the Taboo game.\n"
            "Your goal is to guess the secret word based on the clues provided by the Clue Giver.\n"
            f"You have {self.state.max_turns} turns to guess the word.\n"
            "On your turn, simply type your guess.\n"
        )
        return prompt

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[ta.Observation],  # observations
        Optional[ta.Reward],  # reward
        bool,  # truncated
        bool,  # terminated
        ta.Info,  # info
    ]:
        """
        Process the player's action.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's message or action.

        Returns:
            tuple: (observations, reward, truncated, terminated, info)
        """
        assert isinstance(
            action, str
        ), f"Actions are required to be strings. Received dtype: {type(action)}"

        assert (
            player_id == self.state.current_player
        ), f"The passed player_id is not as expected. Player id received: {player_id}; Expected: {self.state.current_player}"
        
        terminated, truncated = False, False 
        self.step_logs = [] 
        observations = {0: [], 1: []}
        reward = None
        info = {}

        # update step logs
        self.step_logs.append((player_id, action))

        observations[0].append((player_id, action))
        observations[1].append((player_id, action))


        # Clue Giver's turn
        if player_id == 0:
            # Check for taboo words or the word to guess in the clue
            forbidden_words = self.state.game_state["taboo_words"] + [
                self.state.game_state["word_to_guess"]
            ]
            pattern = re.compile(
                r"\b(" + "|".join(map(re.escape, forbidden_words)) + r")\b",
                re.IGNORECASE,
            )
            if pattern.search(action):
                # Clue Giver used a taboo word or the word to guess
                terminated = True
                reward = {0: -1, 1: 0}
                info["reason"] = "Clue Giver used a taboo word or the word to guess."

        # Guesser's turn
        else:
            # Check if the guess is correct
            if self.state.game_state["word_to_guess"].lower() in action.strip().lower():
                # Guesser guessed correctly
                terminated = True
                reward = {0: 1, 1: 1}
                info["reason"] = "Guesser guessed the word correctly."


        if "reason" in info:
            self.step_logs.append(
                (ta.GAME_ID, info["reason"])
            )

        truncated = self.state.step(
            logging_messages=self.step_logs
        )

        return observations, reward, truncated, terminated, info

    def render(self):
        """
        Render the current game state.
        """
        print("Game Logs:")
        for player_id, log in self.state.logs:
            if player_id == -1:
                print(f"Game: {log}")
            elif player_id == 0:
                print(f"Clue Giver: {log}")
            else:
                print(f"Guesser: {log}")
        print("\n")
