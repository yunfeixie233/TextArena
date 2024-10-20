from typing import Any, Dict, Optional, Tuple, Union
import time
import copy
import random
import textarena as ta

# nltk is used to get the words
import nltk
from nltk.corpus import words
nltk.download('words')

class CrosswordsEnv(ta.Env):
    """
    Crosswords environment.
    """

    def __init__(self, hardcore: bool = False, num_words: int = 5, max_incorrect: int = 3, time_limit: Optional[int] = None):
        """
        Initialize the Crosswords environment.

        Args:
            difficulty (str): The difficulty level of the crossword puzzle.
        """
        super().__init__()
        self.ENVIRONMENT_NAME = "Don't Say It" if not hardcore else "Don't Say It (hardcore)"
        self.num_words = num_words
        self.mac_incorrect = max_incorrect

        ## get word list
        if hardcore:
            self.word_list = words.words("en")
        else:
            self.word_list = words.words("en-basic")

        ## TODO: Decide on the game state.
        self.game_state = {
            "turn": 0,
            "max_turns": self.max_turns,
            "target_words": {},
            "logs": [],
        }
    
    def reset(self, seed: Optional[int] = None) -> Tuple[Optional[Dict[int, str]], Dict[int, Any]]:
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
        self.game_state["target_words"] = random.sample(self.word_list, self.num_words)
        self.game_state["grid"] = self._generate_grid(self.game_state["target_words"]) ## TODO: Implement this method
        self.game_state["logs"] = []

        observations = {
            0: self._generate_player_prompt(0)
        }
        info = {
            "target_words": self.game_state["target_words"]
        }

        return observations, info

    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the prompt for the player based on the current state of the game.
        """
        prompt = (
            f"You are Player {player_id}. You are playing classic Crosswords. "
            "Here is the current state of the Crossword grid. Each row is separated by a newline character. "
        )


    def _generate_crossword(self, words, directions):
        """
        Generate a crossword grid with the given words and their directions.
        """

        ## TODO - create a synthetic dataset for the words and the respective clues. 
        ## TODO - Allow for the optino of word, or letters.
        

        words_sorted = sorted(words, key=lambda w: len(w), reverse=True)

        grid_size = self._determine_initial_grid_size(words_sorted)
        grid = self._create_empty_grid(grid_size)

        placed_words = {} # word: (row, col), where 0 is the starting index

        for word in words_sorted:
            placed = False
            if not placed_words: # first word
                # place the first word in the center of the grid
                if directions[word] == "across":
                    row = grid_size // 2
                    col = (grid_size - len(word)) // 2
                else:
                    row = (grid_size - len(word)) // 2
                    col = grid_size // 2
                
                if self._can_place_word(grid, word, directions[word], row, col):
                    self._place_word_on_grid(grid, word, directions[word], row, col)
                    placed_words[word] = (row, col)
                    placed = True
            
            else:
                # attempt to find overlaps
                possible_positions = self._find_overlaps(word, grid, placed_words, directions)
                random.shuffle(possible_positions) # randomize to add variability
                for pos in possible_positions:
                    row, col = pos
                    if self._can_place_word(grid, word, directions[word], row, col):
                        self._place_word_on_grid(grid, word, directions[word], row, col)
                        placed_words[word] = (row, col)
                        placed = True
                        break

            if not placed:
                # if no overlap placement possible, place the word at the first available position
                for row in range(grid_size):
                    for col in range(grid_size):
                        if self._can_place_word(grid, word, directions[word], row, col):
                            self._place_word_on_grid(grid, word, directions[word], row, col)
                            placed_words[word] = (row, col)
                            placed = True
                            break
                    if placed:
                        break
            
            if not placed:
                print(f"Could not place the word: {word}")

        return grid, placed_words

    def _determine_initial_grid_size(self, words):
        """
        Determine the initial size of the grid based on the length of the longest word.
        """
        max_length = max(len(word) for word in words)

        return max_length * 2 # ensures that the grid size is larger than the longest word to allow placement
    
    def _create_empty_grid(self, size):
        """
        Create an empty grid of the specified size.
        """
        return [["#" for _ in range(size)] for _ in range(size)]
    
    def _can_place_word(self, grid, word, direction, row, col):
        """
        Check if a word can be placed on the grid at the specified position.
        """
        if direction == "across":
            if col + len(word) > len(grid):
                return False
            for i, letter in enumerate(word):
                current_cell = grid[row][col + i]
                if current_cell != "#" and current_cell != letter:
                    return False
        else:
            if row + len(word) > len(grid):
                return False
            for i, letter in enumerate(word):
                current_cell = grid[row + i][col]
                if current_cell != "#" and current_cell != letter:
                    return False
                
        return True
    
    def _place_word_on_grid(self, grid, word, direction, row, col):
        """
        Place a word on the grid at the specified position.
        """
        if direction == "across":
            for i, letter in enumerate(word):
                grid[row][col + i] = letter
        else:
            for i, letter in enumerate(word):
                grid[row + i][col] = letter

    def _find_overlaps(self, word, grid, placed_words, directions):
        """Find all possible valid overlaps for the word with already placed words."""
        overlaps = []
        for placed_word in placed_words:
            for i, letter in enumerate(word):
                for j, placed_letter in enumerate(placed_word):
                    if letter == placed_letter:
                        # Determine the position based on directions
                        if directions[word] == 'across' and directions[placed_word] == 'down':
                            # Word is across, placed_word is down
                            row = placed_words[placed_word][0] - i
                            col = placed_words[placed_word][1] + j
                        elif directions[word] == 'down' and directions[placed_word] == 'across':
                            # Word is down, placed_word is across
                            row = placed_words[placed_word][0] + j
                            col = placed_words[placed_word][1] - i
                        else:
                            continue  # Same direction, skipping for simplicity
                        overlaps.append((row, col))
        return overlaps
    
    def _print_grid(self, grid, show_letters=False):
        """Print the grid for text display."""
        for row in grid:
            if show_letters:
                print(' '.join(cell for cell in row))
            else:
                print(' '.join(['_' if cell != '#' else '#' for cell in row]))

    def _hide_letters(self, grid):
        """Hide the letters in the grid."""
        return [['_' if cell != '#' else cell for cell in row] for row in grid]
        

