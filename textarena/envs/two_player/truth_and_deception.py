"""
Truth and Deception Game

In this game, there are two players: the Deceiver and the Guesser.

- **Deceiver**: Knows which of two presented facts is correct and tries to convince the Guesser to pick the incorrect one.
- **Guesser**: Must determine which of the two facts is correct based on the conversation.

**Gameplay:**

1. Both players are presented with two facts. The Deceiver knows which one is correct.
2. Players engage in a conversation for a fixed number of turns.
3. After the conversation, the Guesser makes a guess.
4. The game ends, and rewards are assigned based on the Guesser's choice.

**Key Rules:**

- The Deceiver aims to mislead the Guesser into choosing the wrong fact.
- The Guesser aims to correctly identify the true fact.
- The conversation lasts for a predetermined number of turns.
- The Guesser must choose "Fact 1" or "Fact 2" after the conversation ends.

**Parameters:**

- `max_turns`: Maximum number of conversation turns before the Guesser must make a guess.
- `data_path`: Path to the JSON file containing the facts data.

**Game Outcomes:**

- **Guesser wins**: If they correctly identify the true fact.
- **Deceiver wins**: If the Guesser chooses the incorrect fact.
- **Game ends**: After the Guesser makes a guess.
"""

import json
import os
import random
import re
from typing import Optional, Tuple, Dict, Any

import textarena as ta

GUESSER_PROMPT = (
    "Now guess which of the two facts are correct by returning [Fact 1] or [Fact 2]."
)


class TruthAndDeceptionEnv(ta.Env):
    """Environment for Truth and Deception Game"""

    def __init__(
        self,
        max_turns: Optional[int] = 5,
    ):
        """
        Initialize the Truth and Deception game.

        Roles:
            - Player 0 is the deceiver
            - Player 1 is the guesser

        Args:
            max_turns (int): Maximum number of conversation turns.
            data_path (str): Path to the JSON file containing the facts.
        """
        self.environment_name = "Truth and Deception"

        # load facts
        self._load_facts()

        # Ensure max_turns is an even number
        assert max_turns % 2 == 0, "Please provide an even number for max_turns."

        # Initialize game state
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
            render_keys=["correct_fact", "wrong_fact"]
        )


    def _load_facts(self):
        """Load the facts as a dict from the json"""
        file_path = os.path.join(
            "textarena", "envs", "two_player", "data", "truth_and_deception_facts.json"
        )
        # Load facts from JSON file
        with open(file_path, "r", encoding="utf-8") as file:
            self.facts_data = json.load(file)


    def reset(self, seed: Optional[int] = None) -> Tuple[ta.Observation, ta.Info]:
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

        # Select a random set of facts
        selected_facts = random.choice(self.facts_data)

        # Randomize the order in which the facts are presented
        facts = [
            (selected_facts["facts"]["fact1"], selected_facts["correct_fact"]=="fact1"),
            (selected_facts["facts"]["fact2"], selected_facts["correct_fact"]=="fact2"),
        ]
        random.shuffle(facts)


        game_state = {
            "fact1": {
                "fact": facts[0][0],
                "is_correct": facts[0][1]
            },
            "fact2": {
                "fact": facts[1][0],
                "is_correct": facts[1][1]
            },
            # set the gamestate facts for rendering
            "correct_fact": facts[0][0] if facts[0][1] else facts[1][0],
            "wrong_fact": facts[0][0] if facts[1][1] else facts[1][0]
        }

        observations = {
            0: [(ta.GAME_ID, self._generate_deceiver_prompt(game_state=game_state))], # Player 0 is always the deceiver
            1: [(ta.GAME_ID, self._generate_guesser_prompt(game_state=game_state))], # Player 1 is always the guesser
        }

        info = {
            "fact1": game_state["fact1"],
            "fact2": game_state["fact2"]
        }

        self.state.reset(
            game_state=game_state,
            initial_logs=[
                (ta.GAME_ID, "Game started.")
            ]
        )

        return observations, info


    def _generate_deceiver_prompt(self, game_state: Dict[str, Any]) -> ta.Message:
        """
        Generate the initial prompt for the Deceiver.

        Returns:
            str: Initial prompt for the Deceiver.
        """
        prompt = (
            f"You are Player 0, and you are the Deceiver in the 'Truth and Deception' game.\n"
            f"You know which of the following two facts is correct:\n"
            f"Fact 1: {game_state['fact1']['fact']} ({'correct' if game_state['fact1']['is_correct'] else 'wrong'})\n"
            f"Fact 2: {game_state['fact2']['fact']} ({'correct' if game_state['fact2']['is_correct'] else 'wrong'})\n"
            "Your goal is to convince the other player to choose the incorrect fact.\n"
            f"You will have a conversation for {self.state.max_turns} turns.\n"
            "After that, the other player will make their guess.\n"
            "On your turn, simply type your message."
        )
        return prompt

    def _generate_guesser_prompt(self, game_state: Dict[str, Any]) -> ta.Message:
        """
        Generate the initial prompt for the Guesser.

        Returns:
            str: Initial prompt for the Guesser.
        """
        prompt = (
            f"You are Player 1, and you are the Guesser in the 'Truth and Deception' game.\n"
            f"You need to determine which of the following two facts is correct:\n"
            f"Fact 1: {game_state['fact1']['fact']}\n"
            f"Fact 2: {game_state['fact2']['fact']}\n"
            f"You will have a conversation with the other player for {self.state.max_turns} turns.\n"
            "After that, you will make your guess.\n"
            "On your turn, simply type your message."
        )
        return prompt

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        ta.Observation,  # observations
        ta.Reward,  # reward
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
        observations[player_id].append((player_id, action))
        observations[1-player_id].append((player_id, action))

        # Conversation phase
        if self.state.turn < self.state.max_turns-1:
            # Relay the message to the other player
            pass 
        elif self.state.turn == self.state.max_turns-1:
            # adjust the observation to let the guesser guess
            observations[1-player_id].append((ta.GAME_ID, GUESSER_PROMPT))

        # Guessing phase
        elif self.state.turn == self.state.max_turns :
            # define regex patterns
            guess_fact1_pattern = re.compile(r"\[Fact 1\]", re.IGNORECASE)
            guess_fact2_pattern = re.compile(r"\[Fact 2\]", re.IGNORECASE)

            # check if fact1 was guessed
            if guess_fact1_pattern.search(action):
                # check if guesser was correct
                if self.state.game_state["fact1"]["is_correct"]:
                    # Guesser wins
                    reward = {0: -1, 1: 1}  # Deceiver gets -1, Guesser gets +1
                    info["reason"] = "Guesser is correct."

                else:
                    # Deceiver wins
                    reward = {0: 1, 1: -1}  # Deceiver gets +1, Guesser gets -1
                    info["reason"] = "Guesser is wrong."

            # check if fact 2 was guessed
            elif guess_fact2_pattern.search(action):
                # check if guesser was correct
                if self.state.game_state["fact2"]["is_correct"]:
                    # Guesser wins
                    reward = {0: -1, 1: 1}  # Deceiver gets -1, Guesser gets +1
                    info["reason"] = "Guesser is correct."

                else:
                    # Deceiver wins
                    reward = {0: 1, 1: -1}  # Deceiver gets +1, Guesser gets -1
                    info["reason"] = "Guesser is wrong."

            else:
                # no guess was provided
                reward = {0: 0, 1: -1}  # Deceiver gets 0, Guesser gets -1
                info["reason"] = "Guesser did not provide a guess."

            terminated = True
            self.step_logs.append((ta.GAME_ID, info["reason"]))


        else:
            raise AssertionError(
                "The game has concluded. Please reset before stepping again."
            )

        self.state.step(
            logging_messages=self.step_logs
        )

        return observations, reward, truncated, terminated, info

    def render(self):
        """
        Render the current game state.
        """
        print(f"Turn: {self.state.turn}/{self.state.max_turns + 1}")
        print("Game Logs:")
        for player_id, log in self.state.logs:
            if player_id == ta.GAME_ID:
                print(f"Game: {log}")
            else:
                print(f"Player {player_id}: {log}")
        print("\n")
