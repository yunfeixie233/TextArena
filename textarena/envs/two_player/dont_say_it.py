"""
Don't Say It Game

Each player is given a secret word that they must try to get the other player to say during the course of the game. 
Players take turns speaking to each other, attempting to subtly guide the conversation towards the other's secret word. 
If a player successfully gets the other player to say their secret word, they win the game. 
If a player accidentally says the other player's secret word, they lose the game. 
The game ends either when one player says the other player's word or when the maximum number of turns is reached. 
If the turn limit is reached without either player saying the other's word, the game ends in a draw.

Key Rules:
1. Each player has a secret word that they must protect while trying to make the other player say their word.
2. Players can converse freely but should be subtle to avoid giving away their secret word.
3. The game ends if either player says the other's secret word or when the maximum number of turns is reached.

Parameters:
- `max_turns`: The maximum number of turns allowed before the game ends in a draw.
- `render`: If set to True, the game state and actions are printed for debugging purposes.
- `data_path`: The path to the JSON file containing the list of possible secret words.

Game Outcomes:
- A player wins if they successfully make the other player say their secret word.
- A player loses if they accidentally say the other player's secret word.
- The game is a draw if the turn limit is reached without either player saying the other's word.
"""

# TODO
# - when the secret words are used, they should be highlighted in the render text
# - add max turns and current turn count to the Game State

from typing import Any, Dict, Optional, Tuple, Union
import os, json, random
import textarena as ta

# nltk is used to get the words
import nltk 
from nltk.corpus import words 
nltk.download('words')



class DontSayItEnv(ta.Env):
    def __init__(
        self,
        hardcore: Optional[bool] = False, 
        max_turns: Optional[int] = 10,
    ):
        """
        Initialize the Don't Say It Game.
        Args:
            hardcore (bool): If True, use full English word-set. Otherwise, simplified wordset
            max_turns (int): Maximum number of turns before the game ends in a draw
        """
        self.ENVIRONMENT_NAME = "Don't Say It" if not hardcore else "Don't Say It (hardcore)"
        self.max_turns = max_turns 

        # get word list 
        if hardcore:
            self.word_list = words.words("en")
        else:
            self.word_list = words.words("en-basic")


        # Initialize game state (mostly used by wrappers (especially rendering))
        self.game_state = {
            "turn": 0,
            "max_turns": self.max_turns,
            "target_words": {},
            "logs": [],
        }

    def reset(
        self,
        seed: Optional[int] = None
    ) -> Tuple[Optional[Dict[int, str]], Dict[int, Any]]: # player-wise observations and info 
        """
        Reset the game to its initial state.
        Args:
            seed (Optional[int]): Seed for random number generator to ensure reproducibility.
        Returns:
            Tuple[str, str, Dict[str, str]]: Initial observations for both players and their secret words.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        self.game_state["turn"] = 0

        # Assign secret words to both players, ensuring they are different
        self.game_state["target_words"] = {
            0: random.choice(self.word_list),
            1: random.choice(self.word_list)
        }
        while self.game_state["target_words"][0] == self.game_state["target_words"][1]:
            self.game_state["target_words"][1] = random.choice(self.word_list)

        # Clear logs and add initial messages
        self.game_state["logs"] = []
        self.game_state["logs"].append("New game started!")

        # Generate the initial player-wise observations for both players and return them
        return (
            {
                0: self._generate_player_prompt(player_id=0),
                1: self._generate_player_prompt(player_id=1),
            },
            {
                "player_0_secret_word": self.game_state["target_words"][0],
                "player_1_secret_word": self.game_state["target_words"][1]
            }
        )

    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the initial prompt for a player, providing them with their secret word and instructions.
        Args:
            player_id (int): ID of the player (0 or 1).
        Returns:
            str: Initial prompt for the player.
        """
        prompt = (
            f"You are playing 'Don't Say It'. You are Player {player_id}\n"
            f"Your secret word is: '{self.game_state['target_words'][player_id]}'.\n"
            "Your goal is to get the other player to say your secret word before you say theirs.\n"
            "You can converse freely, but try to be subtle to avoid making it obvious.\n"
            "On your turn, simply type your message.\n"
        )
        if self.game_state["max_turns"]:
            prompt += f"The game lasts for {self.game_state['max_turns']} turns in total.\n"
        return prompt

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[
        Optional[Dict[int, str]],  # player-wise observations
        Optional[Dict[int, int]],  # player-wise reward
        bool,  # truncated
        bool,  # terminated
        Dict[str, Any],  # info
    ]:
        """
        Process the player's action. Checks if the player's action mentions the opponent's secret word.

        Args:
            player_id (int): The player's ID (0 or 1).
            action (str): The player's message or action.

        Returns:
            tuple: (observation, reward, done, info)
                - observation: The action taken.
                - reward: Dictionary with rewards for both players.
                - truncated: Boolean indicating if the game has reach the turn limit.
                - terminated: Boolean indicating if the game has concluded.
                - info: Additional information about the game state.
        """
        assert isinstance(action, str), \
            f"Actions are required to be strings. Received dtype: {type(action)}"

        assert player_id <=1, \
            f"Don't Say It is a 2-Player game. Player_id received: {player_id}. Should be {'{0,1}'}"

        # Increment turn count
        self.game_state["turn"] += 1

        # Update the observations for both players
        if self.game_state["max_turns"]:
            obs_str = f"[Player {player_id}, Turn: {self.game_state['turn']} / {self.game_state['max_turns']}] - {action}"
        else:
            obs_str = f"[Player {player_id}] - {action}"

        # convert observation strings to dictionary
        observations = {
            player_id: obs_str,
            1-player_id: obs_str
        } # for Don't Say It, both players see both actions. Keeping track of previous actions should be handeled outside
        # the main game code


        # Log the player's action for rendering
        self.game_state["logs"].append(f"Player {player_id}: {action}")

        # Check if the action mentions the opponent's secret word
        if self.game_state['target_words'][1-player_id].lower() in action.lower():
            # Opponent's secret word was mentioned, player loses
            self.game_state["logs"].append(f"Player {player_id} mentioned the hidden word!")
            self.game_state["logs"].append(f"Player {1 - player_id} wins!")
            reward = {player_id: -1, 1 - player_id: 1}
            terminated = True
            truncated = False
            info = {"reason": f"Player {player_id} mentioned the hidden word."}

        # Check if the maximum number of turns has been reached
        elif self.game_state["max_turns"] and self.game_state["turn"] >= self.game_state["max_turns"]:
            self.game_state["logs"].append("The turn limit has been reached.")
            self.game_state["logs"].append("The game is a draw.")
            reward = {0: 0, 1: 0}
            terminated = False
            truncated = True
            info = {"reason": "The turn limit has been reached. The game is a draw."}

        # Normal turn, neither word mentioned
        else:
            reward = None
            terminated = False
            truncated = False
            info = {"info": f"Player {player_id}: {action}"}
        
        return observations, reward, truncated, terminated, info

    def render(self):
        """
        Render minimal game state.
        """
        turn_info = f"Turn {self.game_state['turn']}/{self.game_state['max_turns'] if self.game_state['max_turns'] else '∞'}"
        print(turn_info)
        print("Last actions:")
        for log in self.game_state["logs"][-2:]:
            print(log)




