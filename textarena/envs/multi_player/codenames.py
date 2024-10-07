## TODO:
## 1. the list of observations is retaining the previous observations which means it still keeps the initial team of red - e.g. you are the <current_role> for the red team.
## 2. And while the agent gets to view all past observations, the past observations are not clear - e.g. [Player 0] Turn: 0 - Play 2[Player 1] Turn: 0 - Instrument[Player 0]...
## Both of the above makes it hard for the agent to decide on its next action. Inevitable, the agent no longer obeys the instructions.

from typing import Any, Dict, Optional, Tuple, Union
import random
import textarena as ta

## use nltk to get the words
import nltk
from nltk.corpus import words
nltk.download('words')

## use regular expressions to clean the words
import re

class CodenamesEnv(ta.Env):
    def __init__(
        self, 
        hardcore: Optional[bool] = False,
        grid_size: Optional[int] = 5,
    ):
        """
        Initialize the Codenames Game.
        Args:
            hardcore (bool): If True, use full English word-set. Otherwise, simplified wordset
        """
        self.ENVIRONMENT_NAME = "Codenames" if not hardcore else "Codenames (hardcore)"
        self.grid_size = grid_size
        
        # get word list
        if hardcore:
            self.word_list = words.words("en")
        else:
            self.word_list = words.words("en-basic")
        
        # TODO -- Initialize game state (mostly used by wrappers (especially rendering))
        self.game_state = {
            "board": 0,
            "current_team": None,
            "clue": [],
            "done": False,
            "winner": {},
            "current_role": {},
            "logs": [],
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
            Tuple[str, str, Dict[str, str]]: Initial observations for both players and their secret words.
        """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()
        
        ## Assign words to all roles (red, blue, neutral, assassin), ensuring they are different
        self.words = random.sample(self.word_list, self.grid_size ** 2) # Randomly select words for the grid
        self.words_and_roles_array, self.roles_array = self._get_word_for_roles() # Assign roles to the words

        ## Initialize the game state
        self.game_state["board"] = self.roles_array.copy()
        self.game_state["current_team"] = 0 # 0: Red, 1: Blue
        self.game_state["current_role"] = "spymaster"
        self.game_state["clue"] = [0, 0]
        self.game_state["winner"] = None


        ## clear logs and add initial messages
        self.game_state["logs"] = []
        self.game_state["logs"].append("[GAME] New game started!")

        ## Generate the initial player-wise observations for both players and return them
        return(
            {   ## observations for each character (e.g. spymaster - blue team)
                0: self._generate_spymaster_prompt(player_id=0, team=0),
                1: self._generate_field_operatives_prompt(player_id=1, team=0),
                2: self._generate_spymaster_prompt(player_id=2, team=1),
                3: self._generate_field_operatives_prompt(player_id=3, team=1),
            },
            {   ## TODO - what should be in here?
                "words": self.words,
                "roles": self.roles_array,
                "words_and_roles": self.words_and_roles_array,
            }
        )
    
    def _generate_spymaster_prompt(self, player_id: int, team: str) -> str:
        """
        Generate the initial prompt for a spymaster.
        
        Args:
            team (str): The team ('red' or 'blue').
        
        Returns:
            str: Initial prompt for the spymaster.
        """
        prompt = (
            f"You are Player {player_id}. You are the spymaster for the {'red' if team == 0 else 'blue'} team in Codenames.\n"
            f"Here is the grid of words and the teams they belong to:\n"
            f"{', '.join(self.words_and_roles_array)}\n"
            "Your goal is to provide one-word clues that relate to multiple words on the grid.\n"
            "Ensure that your clues do not directly relate to the opposing team's words, neutral words, or the assassin word.\n"
            "On your turn, provide only a clue and the number of words it relates to.\n"
            "Your response should strictly be in the format: <clue> <number>\n"
            "The observation history of yours and your opponents turn will be provided.\n"
        )
        return prompt
    
    def _generate_field_operatives_prompt(self, player_id: int, team: str) -> str:
        """
        Generate the initial prompt for a operative.
        
        Args:
            team (str): The team ('red' or 'blue').
        
        Returns:
            str: Initial prompt for the operative.
        """
        prompt = (
            f"You are Player {player_id}. You are the operative for the {'red' if team == 0 else 'blue'} team in Codenames.\n"
            "Here is the grid of words:\n"
            f"{', '.join(self.words)}\n"
            "Your spymaster has provided a clue and the number of words, N, on the grid that it relates to.\n"
            "Your goal is to guess those N words that belongs to your team based on the spymaster's clues.\n"
            "Your response should be in the format: <word1>, <word2>, <wordN>\n"
            "The observation history of yours and your opponents turn will be provided.\n"
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
            player_id (int): The player's ID.
            action (str): The player's action.
        Returns:
            Tuple[Dict[int, str], float, bool, bool, Dict[str, str]]: Observations, reward, truncated, terminated, info.
        """
        ## clean action string using regular expressions to remove special characters and convert to lowercase
        action = re.sub(r'[^a-zA-Z0-9\s]', '', action)
        
        ## update the observations 
        observation = f'{"Red Team" if self.game_state["current_team"] == 0 else "Blue Team"} {"Spymaster" if player_id % 2 == 0 else "Operative"} said, "{action}"'
        
        ## convert observation to dictionary for appending to all players observations
        observations = {
            0: observation,
            1: observation,
            2: observation,
            3: observation,
        } 
        # For codenames, all players typically hear both teams spymaster and field operative.

        ## init reward
        reward = 0

        if player_id % 2 == 0: # spymaster
            ## Action is a clue
            clue_word, clue_number = action.split()

            ## update game state
            self.game_state["clue"] = [clue_word, int(clue_number)]
            self.game_state["current_role"] = 'operative'
            self.game_state["logs"].append(f"[Game] Player {player_id}: {clue_word} {clue_number}")

            ## update other returns
            truncated = False
            terminated = False
            info = {"reason": f"Player {player_id} provided clue: {clue_word} {clue_number}"}
            
        elif player_id % 2 != 0 and self.game_state["clue"][1] > 0:  # Operative and number of tries left
            # Action is selecting multiple words, separated by commas
            guess_words = [word.strip() for word in action.split()]

            # Initialize variables to track the overall outcome
            total_reward = 0

            # Update the game logs
            self.game_state["logs"].append(f"[Player {player_id}] {action}")

            for guess_word in guess_words:
                if guess_word not in self.words:
                    # Invalid word selected
                    total_reward -= 1  # Apply penalty for invalid guess
                    info = {"reason": f"Player {player_id} selected invalid word: '{guess_word}'"}
                    truncated = False
                    terminated = False
                    break  # Stop processing further guesses

                else:
                    # Retrieve the index and role of the guessed word
                    word_index = self.words.index(guess_word)
                    word_role = self.game_state["board"][word_index]

                    # Decrement the number of tries left
                    self.game_state["clue"][1] -= 1

                    if word_role == 0:
                        # Word has already been revealed
                        total_reward -= 0.5  # Apply penalty
                        info = {"reason": f"Player {player_id} selected already revealed word: '{guess_word}'"}
                        terminated = False
                        truncated = False
                        break  # Stop processing further guesses

                    elif word_role == 1 + self.game_state["current_team"]:
                        # Correct guess for the current team
                        total_reward += 1  # Reward for correct guess
                        self.game_state["board"][word_index] = 0  # Mark word as revealed

                        if self._check_win_condition():
                            # Current team has won the game
                            self.game_state["done"] = True
                            self.game_state["winner"] = "red" if self.game_state["current_team"] == 0 else "blue"
                            total_reward += 10  # Additional reward for winning
                            print(f"Team {self.game_state['winner']} has won the game!")

                            # Update termination flags and info
                            truncated = False
                            terminated = True
                            info = {"reason": f"Player {player_id} selected the final word: '{guess_word}'"}
                            break  # Game has ended

                        # Continue guessing if the game hasn't ended
                        info = {"reason": f"Player {player_id} selected correct word: '{guess_word}'"}

                    elif word_role == 3:
                        # Neutral word selected
                        total_reward += 0.0  # Minor penalty for neutral guess
                        self.game_state["board"][word_index] = 0  # Mark word as revealed

                        info = {"reason": f"Player {player_id} selected neutral word: '{guess_word}'"}
                        terminated = False
                        truncated = False
                        # Continue guessing till the number of tries left is zero

                    elif word_role == 2 - self.game_state["current_team"]:
                        # Opponent's word selected
                        total_reward -= 1  # Penalty for selecting opponent's word
                        self.game_state["board"][word_index] = 0  # Mark word as revealed

                        info = {"reason": f"Player {player_id} selected opponent word: '{guess_word}'"}
                        terminated = False
                        truncated = False
                        break  # Turn ends after selecting opponent's word

                    elif word_role == 4:
                        # Assassin word selected
                        total_reward -= 10  # Heavy penalty for selecting assassin
                        self.game_state["winner"] = "assassin"

                        truncated = False
                        terminated = True
                        info = {"reason": f"Player {player_id} selected assassin word: '{guess_word}'"}
                        break  # Game has ended

            if not terminated:
                # All guesses processed without triggering a break
                self._switch_turn()


            # Assign the accumulated reward
            reward = total_reward

            # If no guesses were made (empty action), handle as invalid action
            if not guess_words:
                self._switch_turn()
                info = {"reason": f"Player {player_id} provided no valid guesses."}

        elif self.game_state["clue"][1] == 0:
            # Handle invalid action outside the operative's turn
            self._switch_turn()
            truncated = False
            terminated = False
            info = {"reason": f"Player {player_id} has run out of turns."}


        return observations, reward, truncated, terminated, info
    
    def render(self):
        """
        Renders the current state of the game
        """
        print("\n--- Game State ---")
        for i in range(self.grid_size):
            row = ""
            for j in range(self.grid_size):
                idx = i * self.grid_size + j
                word = self.words[idx]
                role = self.game_state["board"][idx]
                row += f"{word} ({role})\t"

            print(row)
        print(f"Current team: {self.game_state['current_team']}")
        print(f"Clue: {self.game_state['clue']}")
        print(f"Done: {self.game_state['done']}")
        print(f"Winner: {self.game_state['winner']}")
        print(f"Logs: {self.game_state['logs'][-2:]}")

    def _switch_turn(self):
        """
        Switch the turn to the next team.
        """
        self.game_state["current_team"] = 1 - self.game_state["current_team"]
        self.game_state["current_role"] = 'spymaster'
        self.game_state["clue"] = [0, 0]
        self.game_state["logs"].append(f"[Game] Turn switched to team {'Red' if self.game_state['current_team'] == 0 else 'Blue'}")


    def _check_win_condition(self):
        """
        Check if the current team has won the game.
        Returns:
            bool: True if the current team has won, False otherwise.
        """
        return all(role == 0 or role == 1 + self.game_state["current_team"] for role in self.game_state["board"])
    
    def _get_word_for_roles(
        self,
    ) -> Dict[int, str]: # gets the words for each role
        """
        Get the words for each role.
        Returns:
            Tuple[int, int, int, int]: Number of words for each role
        """
        total_words = self.grid_size ** 2

        ## calculate the number of words for each role
        red_count = (total_words - 1) // 3 + 1 # team red will be the first team which go first, hence 1 additional word
        blue_count = (total_words - 1) // 3
        neutral_count = total_words - red_count - blue_count - 1
        assassin_count = 1

        ## create a list of their words
        roles_array = (
            [1] * red_count +  # Red team
            [2] * blue_count +  # Blue team
            [3] * neutral_count +  # Neutral
            [4] * assassin_count # Assassin
        )
        random.shuffle(roles_array)

        ## create a list of the words + roles as strings, e.g "car (red)"
        words_and_roles_array = [
            f"{self.words[idx]} ({'red' if role == 1 else 'blue' if role == 2 else 'neutral' if role == 3 else 'assassin'})"
            for idx, role in enumerate(roles_array)
        ]

        return words_and_roles_array, roles_array

