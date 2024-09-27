import gymnasium as gym
from gymnasium import spaces
import random
from typing import Dict, List, Tuple
from textarena.codenames.agents import CodenamesAgent

# Fixed list of 25 words
WORDS = [
    "apple", "table", "moon", "king", "computer",
    "tower", "cloud", "dog", "car", "bridge",
    "river", "sky", "queen", "horse", "book",
    "star", "piano", "fire", "ocean", "mountain",
    "forest", "beach", "house", "ship", "key"
]

GRID_SIZE = 5  # 5x5 grid

class CodenamesEnv(gym.Env):
    """
    A simplified Codenames environment for Gymnasium.
    """
    
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(CodenamesEnv, self).__init__()
        
        # Define action and observation spaces
        # We'll use separate action spaces for spymaster and operative
        # Actions will be handled based on the current role
        
        # Action space for spymaster: Clue word (from a predefined list) and number
        # For simplicity, we'll limit clues to a subset of words or allow any string
        # Gymnasium doesn't support variable-length text, so we'll handle clues separately
        self.spymaster_action_space = spaces.Tuple((
            spaces.Discrete(len(WORDS)),  # Index of the clue word from WORDS list
            spaces.Discrete(10)           # Number for the clue (e.g., "vehicle 2"
        ))
        
        # Action space for operative: Selecting a word index (0-24)
        self.operative_action_space = spaces.Discrete(len(WORDS))
        
        # Observation space: 
        # - Board state: Each word can be in one of several states
        #   0: Revealed
        #   1: Red team
        #   2: Blue team
        #   3: Neutral
        #   4: Assassin
        # - Current clue (handled separately)
        # - Current team turn (red or blue)
        self.observation_space = spaces.Dict({
            'board': spaces.MultiDiscrete([5] * len(WORDS)),
            'current_team': spaces.Discrete(2),  # 0: Red, 1: Blue
            'clue': spaces.Tuple((
                spaces.Discrete(len(WORDS)),  # Clue word index
                spaces.Discrete(10)           # Clue number
            ))
        })
        
        # Initialize the Agent
        self.agent = CodenamesAgent()
        
        # Initialize the game state
        self.reset()
    
    def reset(self) -> Dict:
        """
        Resets the game to the initial state.
        """
        # Assign roles to words
        # For simplicity, we'll assign:
        # - 9 red words
        # - 8 blue words
        # - 7 neutral words
        # - 1 assassin word
        
        roles = (
            [1] * 9 +  # Red team
            [2] * 8 +  # Blue team
            [3] * 7 +  # Neutral
            [4]        # Assassin
        )
        random.shuffle(roles)  # Shuffle the roles
        
        self.board = roles.copy()
        self.current_team = 0  # 0: Red, 1: Blue
        self.clue = [0, 0]      # No clue initially
        self.done = False
        self.winner = None
        self._current_role = 'spymaster'  # Start with spymaster
        
        # Return the initial observation
        return self._get_observation()
    
    def step(self, action) -> Tuple[Dict, float, bool, Dict]:
        """
        Executes one step in the environment.
        """
        if self.done:
            raise Exception("Game is over. Please reset the environment.")
        
        observation = self._get_observation()
        reward = 0
        info = {}
        
        if self.current_role == 'spymaster':
            # Action is a clue
            clue_word, clue_number = action
            self.clue = [clue_word, clue_number]
            print(f"Spymaster provides clue: {clue_word} {clue_number}")
            self.current_role = 'operative'  # Switch to operative
        
        elif self.current_role == 'operative' and self.clue[1] > 0:
            # Action is selecting a word
            guess_word = action

            if guess_word not in WORDS:
                # Invalid word role
                print(f"Invalid word: '{guess_word}'")
                reward = -1
                self._switch_turn()

            else:
                # valid word role
                word_idx = WORDS.index(guess_word)
                word_role = self.board[word_idx]
                self.clue[1] -= 1  # Decrement the clue number
                
                if word_role == 0:
                    # Already revealed
                    print(f"Word '{WORDS[word_idx]}' already revealed. Penalizing.")
                    reward = -1  # Penalize invalid action
                elif word_role == 1 + self.current_team:
                    # Correct team word
                    print(f"Correct guess: '{WORDS[word_idx]}'")
                    reward = 1
                    self.board[word_idx] = 0  # Reveal the word
                    # Check for win condition
                    if self._check_win_condition():
                        self.done = True
                        self.winner = 'red' if self.current_team == 0 else 'blue'
                        reward += 10
                        print(f"Team {self.winner} has won the game!")
                elif word_role == 3:
                    # Neutral word
                    print(f"Neutral guess: '{WORDS[word_idx]}'")
                    reward = -0.5
                    self.board[word_idx] = 0  # Reveal the word
                    # self._switch_turn()
                elif word_role == 2 - self.current_team:
                    # Opponent's word
                    print(f"Opponent's word guessed: '{WORDS[word_idx]}'")
                    reward = -1
                    self.board[word_idx] = 0  # Reveal the word
                    self._switch_turn()
                elif word_role == 4:
                    # Assassin
                    print(f"Assassin guessed: '{WORDS[word_idx]}'! Game over.")
                    reward = -10
                    self.done = True
                    self.winner = 'assassin'

        else:
            self._switch_turn()
        
        return self._get_observation(), reward, self.done, info
    
    def render(self, mode='human'):
        """
        Renders the current state of the game.
        """
        print("\n--- Codenames Board ---")
        for i in range(GRID_SIZE):
            row = ""
            for j in range(GRID_SIZE):
                idx = i * GRID_SIZE + j
                word = WORDS[idx]
                role = self.board[idx]
                if role == 0:
                    status = "Revealed"
                elif role == 1:
                    status = "Red"
                elif role == 2:
                    status = "Blue"
                elif role == 3:
                    status = "Neutral"
                elif role == 4:
                    status = "Assassin"
                row += f"{word}({status})\t"
            print(row)
        print(f"Current Team: {'Red' if self.current_team == 0 else 'Blue'}")
        if self.clue != [0, 0]:
            clue_word = self.clue[0]
            clue_number = self.clue[1]
            print(f"Clue: {clue_word} {clue_number}")
        print("------------------------\n")
    
    def close(self):
        """
        Cleans up the environment.
        """
        pass
    
    ## Helper internal methods
    def _get_observation(self) -> Dict:
        """
        Returns the current observation.
        """
        return {
            'board': self.board.copy(),
            'current_team': self.current_team,
            'clue': self.clue
        }
    
    def _check_win_condition(self) -> bool:
        """
        Checks if the current team has won.
        """
        target = 1 if self.current_team == 0 else 2
        return target not in self.board
    
    def _switch_turn(self):
        """
        Switches the current team's turn.
        """
        self.current_team = 1 - self.current_team
        self.current_role = 'spymaster'
        self.clue = [0, 0]
        print(f"Switching turn to {'Red' if self.current_team == 0 else 'Blue'} team.")

    def _get_textual_board_state(self, current_role):
        description = "Current Board State:\n"
        for idx, role in enumerate(self.board):
            word = WORDS[idx]

            ## Operative should only know what words are revealed, not the roles of the words
            ## Spymaster should know the roles of all words (s.g. what's revealed, what's red, what's blue, what's neutral, what's the assassin)
            if current_role == 'operative':
                if role == 0:
                    status = "revealed"
                else:
                    status = "unrevealed"
            else:
                if role == 0:
                    status = "revealed"
                elif role == 1:
                    status = "red"
                elif role == 2:
                    status = "blue"
                elif role == 3:
                    status = "neutral"
                elif role == 4:
                    status = "assassin"

            description += f"- {word}: {status}\n"
        # description += f"Current Clue: '{WORDS[self.clue[0]]}' {self.clue[1]}\n"
        # description += f"Your Team: {'Red' if self.current_team == 0 else 'Blue'}\n"
        return description

    @property
    def current_role(self) -> str:
        """
        Returns the current role ('spymaster' or 'operative').
        """
        if hasattr(self, '_current_role'):
            return self._current_role
        else:
            self._current_role = 'spymaster'
            return self._current_role
    
    @current_role.setter
    def current_role(self, value: str):
        self._current_role = value
