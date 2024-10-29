""" Taboo Environment """

import os
import re 
import json
import random 
from typing import Optional, Tuple, Dict, List, Any


import textarena as ta 


class TabooEnv(ta.Env):
    """ Environment for Taboo Game. """
    def __init__(
        self, 
        categories: List[str],
        max_turns: Optional[int],
        data_path: Optional[str]=None
    ):
        """
        Initialize the Taboo game environment.

        Roles:
            - Player 0 is the Clue Giver
            - Player 1 is the Guesser

        Args:
            categories (List[str]): List of categories to include in the game.
            max_turns (int): Maximum number of conversation turns.
            data_path (str): Path to the JSON file containing the facts.
        """

        # Enforce even number of turns
        assert max_turns % 2 == 0, \
            f"Please use an even number of max turns. Current max_turns: {max_turns}"



        self.categories = categories
        self.data_path = data_path 


        # Load the data 
        self._load_data()

        # Initialize game state 
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
            check_truncated=False,
            render_keys=["word_to_guess", "taboo_words"],
            role_mapping={0: "Clue Giver", 1: "Guesser"}
        )


    def _load_data(self):
        """
        Load the word list based on the specified categories from the JSON file.
        The JSON structure is expected to be:
        {
            "category1": {
                "word1": ["taboo1", "taboo2", ...],
                "word2": ["taboo1", "taboo2", ...],
                ...
            },
            "category2": {
                ...
            },
            ...
        }
        """
        if self.data_path is None:
            self.data_path = os.path.join(
                "textarena", "envs", "two_player", "Taboo", "words.json"
            )

        # Load all data from JSON file 
        with open(self.data_path, "r", encoding="utf-8") as f:
            full_data = json.load(f)

        # Subsample to the legal keys 
        self.data = {}
        for category in self.categories:
            self.data.update(full_data[category])

    def reset(
        self, seed: Optional[int] = None
    ) -> Optional[ta.Observations]:
        """
        Reset the Taboo game to its initial state.

        Args:
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Optional[ta.Observations]: Initial observations for both players as a dictionary.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        word_to_guess, taboo_words = (
            random.choice(list(self.data.items()))
        )

        return self.state.reset(
            game_state={
                "word_to_guess": word_to_guess,
                "taboo_words": taboo_words
            },
            player_prompt_function=self._generate_player_prompt
        )


    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """
        Generate the initial prompt for a player based on their role.

        Args:
            player_id (int): The player's ID (0 or 1).

        Returns:
            str: The initial prompt for the player.
        """
        if self.state.role_mapping[player_id] == "Clue Giver":
            prompt = (
                f"You are Player {player_id}, the Clue Giver in the Taboo game.\n"
                f"The word to guess is '{game_state['word_to_guess']}'.\n"
                f"Taboo words: {', '.join(game_state['taboo_words'])}.\n"
                "Your goal is to provide clues to help the Guesser guess the word without using the taboo words or the word to guess.\n"
                f"You have {self.state.max_turns} turns to assist the Guesser.\n"
                "On your turn, simply type your clue.\n"
            )

        elif self.state.role_mapping[player_id] == "Guesser":
            prompt = (
                f"You are Player {player_id}, the Guesser in the Taboo game.\n"
                "Your goal is to guess the secret word based on the clues provided by the Clue Giver.\n"
                f"You have {self.state.max_turns} turns to guess the word.\n"
                "On your turn, simply type your guess in squared brackets. For example: '[elephant'].\n"
            )

        else:
            # unexpected
            raise ValueError(f"Unexpected role mapping: {self.state.role_mapping[player_id]}. Expected 'Clue Giver' or 'Guesser'.")

        return prompt 

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[ta.Observations], # Observations: Dict[int, Tuple[int, str]]
        Optional[ta.Rewards], # Rewards: Dict[int, int]
        bool, # Truncated
        bool, # Terminated
        ta.Info, # Info: Optional[Dict[str, Any]]
    ]:
        """
        Process the player's action.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's message or action.

        Returns:
            tuple: (observations, rewards, truncated, terminated, info)
        """
        # check the player_id and action fromat
        self.state.check_action_format(
            action=action,
            player_id=player_id
        )

        # update the observations and log the action
        self.state.add_observation(
            from_id=player_id,
            to_id=-1, # Broadcast to all
            message=action,
            for_logging=True
        )


        # Clue Giver's turn
        if self.state.role_mapping[player_id] == "Clue Giver":
            # Check for taboo words or the word to guess in the clue 
            forbidden_words = self.state.game_state["taboo_words"] + [
                self.state.game_state["word_to_guess"]
            ]
            pattern = re.compile(
                r"\b(" + "|".join(map(re.escape, forbidden_words)) + r")\b",
                re.IGNORECASE,
            )
            if pattern.search(action):
                # Clue Giver used a forbidden word.
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"The Clue Giver (Player {player_id}) mentioned a taboo word, or the target word."]
                )
            
        # Guesser's turn
        elif self.state.role_mapping[player_id] == "Guesser":
            # Guesser must provide a guess within squared brackets
            guess_pattern = re.compile(r"\[(.*?)\]")
            match = guess_pattern.search(action)
            if not match:
                # Invalid guess format
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=["Invalid guess format. Please provide your guess within squared brackets, e.g., '[apple]'."]
                )
                return self.state.step()

            guess = match.group(1).strip().lower()
            correct_word = self.state.game_state["word_to_guess"].lower()

            if guess == correct_word:
                # Guesser guessed correctly
                self.state.set_winners(
                    player_ids=[0, 1],
                    reason=f"Player {player_id} (Guesser) correctly guessed the word. Both players win!"
                )
                return self.state.step()


        else:
            # unexpected
            raise ValueError(f"Unexpected role mapping: {self.state.role_mapping[player_id]}. Expected 'Clue Giver' or 'Guesser'.")


        return self.state.step()


    def render(self):
        """
        Render the current game state to the console.
        """
        print(f"Turn: {self.state.turn}/{self.state.max_turns if self.state.max_turns else '∞'}")
        print("\nRecent Game Logs:")
        recent_logs = self.state.logs[-5:]  # Display the last 5 logs
        for sender_id, log in recent_logs:
            if sender_id == ta.GAME_ID:
                print(f"[GAME] {log}")
            elif self.state.role_mapping[sender_id] == "Clue Giver":
                print(f"[Clue Giver (Player {sender_id})]: {log}")
            elif self.state.role_mapping[sender_id] == "Guesser":
                print(f"[Guesser (Player {sender_id})]: {log}")
        print("\n")
