import re, random, copy
from typing import Any, Dict, List, Tuple, Optional, Union

import textarena as ta
from textarena.envs.games.Hangman.renderer import create_board_str

## use nltk to get the words
import nltk
from nltk.corpus import words
nltk.download('words')


class HangmanEnv(ta.Env):
    """ Hangman environment """

    def __init__(self, hardcore: Optional[bool] = False):
        """
        Initialize the Hangman environment

        Args:
            hardcore: Whether to play in hardcore mode.
        """
        super().__init__()
        self.hardcore = hardcore
        self.word_list = words.words("en") if hardcore else words.words("en-basic") ## load the word list (to be sampled from)

    def get_board_str(self):
        return create_board_str(game_state=self.state.game_state)

    def reset(self, num_players: int, seed: Optional[int] = None):
        """ Reset the environment to its initial state """
        self.state = ta.State(num_players=num_players, min_players=1, max_players=1, seed=seed) ## initialize the game state
        self.game_board = self._generate_board()  ## initialize the game state
        self.game_board_hidden = self._hide_letters(self.game_board) 
        self.guessed_letters = set()
        game_state = {"board": copy.deepcopy(self.game_board_hidden), "tries_left": 6} ## reset the game state
        return self.state.reset(game_state=game_state, player_prompt_function=self._generate_player_prompt)
    
    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """ Generate the prompt for the player based on the current state of the game """
        prompt = (
            f"You are Player {player_id}. You are playing Hangman.\n"
            "The objective of the game is to guess the word by providing one letter guesses or the entire word.\n"
            "Here is the current state of the Hangman grid. Each column is numbered.\n"
            "The cells that need to be populated with letters are represented by '_'.\n\n"
            "There are two ways you can answer. You can provide one letter guesses in the format of [L], or you can guess the entire word in the format of [LIGHT].\n"
            "If the given letter is in the word, it will be revealed in the grid.\n"
            "If the given word is correct, you win.\n"
            "As you play, the history of your choices will be appended below. Use the information to figure out the word and win.\n"
            "Some rules:\n"
            "1. You can only guess one letter at a time.\n"
            "2. You can only guess the entire word once.\n"
            "3. You have 6 incorrect tries before the game ends.\n\n"
            "Current Hangman Grid:\n"
        )
        grid_str = self._render_board(self.game_board_hidden, show_letters=False)
        prompt += grid_str
        return prompt
    
    def _generate_board(self) -> List[str]:
        """ Generate a new game board -> List[str]: The game board """
        self.chosen_word = random.choice(self.word_list).upper() # sample 1 word
        return list(self.chosen_word) ## e.g. ['H', 'A', 'N', 'G', 'M', 'A', 'N']
    
    def _hide_letters(self, board: List[str]) -> List[str]:
        """ Hide the letters on the board -> List[str]: The hidden game board """
        return ['_' for _ in board]
    
    def _render_board(self, board: List[str], show_letters: bool = False) -> str:
        """ Render the board"""
        header = " ".join(f"C{i:02}" for i in range(len(board)))
        lines = [header]
        # We only need a single row for the word
        row_str = ""  # Label for the single row
        for i, val in enumerate(board):
            if show_letters:
                row_str += f"  {val} "
            else:
                row_str += "  _ "
        lines.append(row_str)

        return "\n".join(lines)
    
    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """ Process the player's action and update the game state accordingly """
        player_id = self.state.current_player_id
        self.state.add_observation(from_id=player_id, to_id=-1, message=action) # Update the observations

        # Validate the actions
        # Note that the response can have multiple guesses at one go.
        action_search_pattern = re.compile(r"\[([a-zA-Z]+)\]", re.IGNORECASE)  # e.g., [A], [B], [C], [light], [LIGHT]
        matches = action_search_pattern.findall(action)
        matches = set(matches)  # Remove duplicates

        if not matches:
            reason=f"Invalid move format. Player {player_id} did not respond with a valid 'letter' or 'word'."
            self.state.set_invalid_move(player_id=player_id, reason=reason)
        else:
            for match in matches:
                letter = match.upper()  # Convert to uppercase for consistency
                if len(letter) > 1: ## check if the match is a word
                    if letter == self.chosen_word:
                        reason=f"Congratulations! Player {player_id} completed the Hangman puzzle."
                        self.state.set_winners(player_ids=[player_id], reason=reason)
                        for i, char in enumerate(letter):
                            self._reveal_letter(char)  # Update the word progress to reveal this letter
                    else:
                        self.state.set_invalid_move(player_id=player_id, reason=f"Invalid move. The word is incorrect."); break

                if letter in self.guessed_letters: # Check if the letter has been guessed before
                    reason=f"Invalid move. Player {player_id} guessed the letter '{letter}' which has already been guessed."
                    self.state.set_invalid_move(player_id=player_id, reason=reason)
                    break
                
                self.guessed_letters.add(letter) # Add the letter to the set of guessed letters
                if letter in self.chosen_word: # Check if the letter is in the target word
                    self._reveal_letter(letter)  # Update the word progress to reveal this letter
                    message=f"Board state: \n{self._render_board(self.state.game_state['board'], show_letters=True)}"
                    self.state.add_observation(from_id=ta.GAME_ID, to_id=-1, message=message)
                else:
                    self.state.game_state["tries_left"] -= 1
                    message=f"Your guess of {letter} is not in the word. You have {self.state.game_state['tries_left']} turns left."
                    self.state.add_observation(from_id=-1, to_id=player_id, message=message)
                    break
            
            if self.state.game_state["tries_left"] == 0: ## check if the game is over
                self.state.set_draw(reason="No turns left. Game over.")
                pct_complete = self._get_percentage_completion()
                reason=f"You are out of tries. You guessed {pct_complete*100} percentage of the characters correctly."
                self.state.set_singleplayer_game_outcome(reward=pct_complete, reason=reason)
            elif self._is_game_over():
                reason=f"Congratulations! You have completed the Hangman puzzle."
                self.state.set_singleplayer_game_outcome(reward=1, reason=reason)
            
        return self.state.step()
    
    def _reveal_letter(self, letter: str) -> None:
        """ Reveal the letter in the target word """
        for i, char in enumerate(self.chosen_word):
            if char == letter:
                self.state.game_state["board"][i] = letter
    
    def _is_game_over(self) -> bool:
        """ Check if the game is over -> bool: True if the game is over, False otherwise """
        return self.state.game_state["board"] == self.game_board

        def _get_percentage_completion(self) -> float:
        """ Compute the percentage of correctly guessed letters (excluding underscores) Returns a float in [0, 1] """
        total_letters = len(self.game_board)
        revealed_letters = sum(1 for a, b in zip(self.state.game_state["board"], self.game_board) if a == b)
        return revealed_letters / total_letters

    
