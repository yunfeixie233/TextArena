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
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Union

import os, json, random
from textarena.games.game_interface import GameInterface


import nltk 
from nltk.corpus import words 
nltk.download('words')


class DontSayItGame(GameInterface):
    def __init__(self, hardcore=False, max_turns=10, render=False):
        """
        Initialize the Don't Say It Game.

        Args:
            hardcore (bool): If True, use full english, words. Otherwise, use simple subset
            max_turns (int): Maximum number of turns before the game ends in a draw.
            render (bool): If True, prints game states and actions for debugging.
            data_path (str): Path to the JSON file containing the list of possible words.
        """
        self.name = "Don't Say It" if not hardcore else "Don't Say It (hardcore)"
        self.max_turns = max_turns
        self.render = render

        # get word list
        if hardcore:
            self.word_list = words.words('en')
        else:
            self.word_list = words.words('en-basic')


    def reset(self) -> Tuple[str, str, str]:
        """
        Reset the game to its initial state. Assigns a random secret word to each player and
        generates the initial prompts.

        Returns:
            dict: Initial prompts for both players.
        """
        self.turn = 0
        # Assign secret words to both players, ensuring they are different
        self.target_words = {
            0: random.choice(self.word_list),
            1: random.choice(self.word_list) 
        }
        while self.target_words[0] == self.target_words[1]:
            self.target_words[1] = random.choice(self.word_list)  # Ensure different words

        # Generate initial prompts for both players
        return (
            self._generate_player_prompt(player_id=0),
            self._generate_player_prompt(player_id=1),
            ""
        )

    def _generate_player_prompt(self, player_id):
        """
        Generate the initial prompt for a player, providing them with their secret word and instructions.

        Args:
            player_id (int): ID of the player (0 or 1).

        Returns:
            str: Initial prompt for the player.
        """
        prompt = (
            f"You are playing 'Don't Say It'.\n"
            f"Your secret word is: '{self.target_words[player_id]}'.\n"
            "Your goal is to get the other player to say your secret word before you say theirs.\n"
            "You can converse freely, but try to be subtle to avoid making it obvious.\n"
            f"The game lasts for {self.max_turns} turns in total.\n"
            "On your turn, simply type your message.\n"
        )
        return prompt

    def get_valid_actions(self, player_id: int) -> Optional[Any]:
        """
        Return the valid actions for the given player.

        Args:
            player_id (int): The player's ID (0 or 1).

        Returns:
            None: No restrictions on actions in this game.
        """
        return None

    def get_info(self) -> Dict[str, Any]:
        """
        Return additional information about the final game state.

        Returns:
            num_turns: The total number of turns executed
        """
        return {'num_turns': self.turn}

    def step(
        self, 
        player_id: int, 
        action: str
    ) -> Tuple[
        Optional[str], # observation
        Optional[Dict[int, int]], # reward
        bool, # done 
        Dict[str, Any], #info
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
                - done: Boolean indicating if the game has ended.
                - info: Additional information about the game state.
        """
        self.turn += 1

        # the observation is simply the other players action
        observation = action 

        self._render(message=f"[Player {player_id}, Secret Word: {self.target_words[player_id]}] {action}")

        # Check if the action mentions the opponent's secret word
        if self.target_words[1 - player_id].lower() in action.lower():
            # Opponent's secret word was mentioned, player loses
            self._render(message=f"Player {player_id} mentioned the hidden word.")
            return None, {player_id: -1, 1 - player_id: 1}, True, {"reason": f"Player {player_id} mentioned the hidden word."}

        # Check if the maximum number of turns has been reached
        elif self.turn >= self.max_turns:
            self._render(message="The turn limit has been reached.")
            return None, {0: 0, 1: 0}, True, {"reason": "The turn limit has been reached. The game is a draw."}

        # Normal turn, no word mentioned
        else:
            return observation, None, False, {"info": f"Player {player_id}: {action}"}


    def _render(self, message: str) -> None:
        """ Print the current game state """
        if self.render:
            print(message, end="\n\n")