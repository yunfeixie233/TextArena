from typing import Any, Dict, List, Tuple, Optional, Union
import copy
import random
import textarena as ta
import re

## use nltk to get the words
import nltk
from nltk.corpus import words
nltk.download('words')

class HangmanEnv(ta.Env):
    """
    Hangman environment.
    """

    def __init__(
        self,
        hardcore: Optional[bool] = False
    ):
        """
        TODO
        """

        super().__init__()
        self.environment_name = "Hangman"
        self.hardcore = hardcore

        ## initialize the game state
        self.state = ta.State(
            num_players=1,
            render_keys=["rendered_board"],
        )

        ## load the word list (to be sampled from)
        if hardcore:
            self.word_list = words.words("en")
        else:
            self.word_list = words.words("en-basic")

    def reset(
        self,
        seed: Optional[int] = None
    ) -> Optional[ta.Observations]:
        """
        Reset the environment to its initial state.
        """

        ## seed the random number generator
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        ## initialize the game state
        self.game_board = self._generate_board() 
        self.game_board_hidden = self._hide_letters(self.game_board) 
        self.guessed_letters = set()

        ## reset the game state
        return self.state.reset(
            game_state={
                "board": copy.deepcopy(self.game_board_hidden),
                "rendered_board": self._render_board(self.game_board_hidden, show_letters=False),
                "num_incorrect_tries": 6
            },
            player_prompt_function=self._generate_player_prompt ## TODO
        )
    
    def _generate_player_prompt(self, player_id: int) -> str:
        """
        Generate the prompt for the player based on the current state of the game.
        """
        prompt = (
            f"You are Player {player_id}. You are playing Hangman.\n"
            "The objective of the game is to guess the word by providing one letter guesses or the entire word.\n"
            "Here is the current state of the Hangman grid. Each column is numbered.\n"
            "The cells that need to be populated with letters are represented by '_'.\n\n"
            "Current Hangman Grid:\n"
        )

        grid_str = self._render_board(self.game_board_hidden, show_letters=False)
        prompt += grid_str

        # prompt += "\n\nHere are the clues for the words you need to find:\n"
        # prompt += self._clue_generator()
        prompt += ("\n\nThere are two ways you can answer. You can provide one letter guesses in the format of [L], or you can guess the entire word in the format of [LIGHT].\n"
                   "If the given letter is in the word, it will be revealed in the grid.\n"
                   "If the given word is correct, you win.\n"
                   "As you play, the history of your choices will be appended below. Use the information to figure out the word and win.\n")
    
        return (-1, prompt)
    
    def _generate_board(self) -> List[str]:
        """
        Generate a new game board.
        """
        ## sample 1 word
        self.chosen_word = random.choice(self.word_list).upper()
        print(f"Chosen word: {self.chosen_word}")

        ## return word
        return list(self.chosen_word) ## e.g. ['H', 'A', 'N', 'G', 'M', 'A', 'N']
    
    def _hide_letters(self, board: List[str]) -> List[str]:
        """
        Hide the letters on the board.
        """
        return ['_' for _ in board]
    
    def _render_board(self, board: List[str], show_letters: bool = False) -> str:
        """
        Render the board.
        """
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
    
    def step(
        self,
        player_id: int,
        action: str
    ) -> Tuple[
        Optional[ta.Observations], # observations
        Optional[ta.Rewards], # reward
        bool, # truncated
        bool, # terminated
        ta.Info # info
    ]:
        """
        Process the player's action and update the game state accordingly.
        """

        # Update the observations
        self.state.add_observation(
            from_id=player_id,
            to_id=-1,
            message=action,
            for_logging=False
        )

        # Validate the actions
        # Note that the response can have multiple guesses at one go.
        action_search_pattern = re.compile(r"\[([a-zA-Z]+)\]", re.IGNORECASE)  # e.g., [A], [B], [C], [light], [LIGHT]
        matches = action_search_pattern.findall(action)
        matches = set(matches)  # Remove duplicates

        if not matches:
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"Invalid move format. Player {player_id} did not respond with a valid 'letter' or 'word'."]
            )
        else:
            for match in matches:
                letter = match.upper()  # Convert to uppercase for consistency
                ## check if the match is a word
                if len(letter) > 1:
                    if letter == self.chosen_word:
                        self.state.set_winners(
                            player_ids=[player_id],
                            reason=f"Congratulations! Player {player_id} completed the Hangman puzzle."
                        )
                        for i, char in enumerate(letter):
                            self._reveal_letter(char)  # Update the word progress to reveal this letter
                    else:
                        self.state.set_invalid_move(
                            player_ids=[player_id],
                            reasons=[f"Invalid move. The word is incorrect."]
                        )
                    break

                # Check if the letter has been guessed before
                if letter in self.guessed_letters:
                    self.state.set_invalid_move(
                        player_ids=[player_id],
                        reasons=[f"Invalid move. Player {player_id} guessed the letter '{letter}' which has already been guessed."]
                    )
                    break
                
                # Add the letter to the set of guessed letters
                self.guessed_letters.add(letter)

                # Check if the letter is in the target word
                if letter in self.chosen_word:
                    self._reveal_letter(letter)  # Update the word progress to reveal this letter
                    self.state.add_observation(
                        from_id=ta.GAME_ID,
                        to_id=-1,
                        message=f"Board state: {self._render_board(self.state.game_state['board'], show_letters=True)}",
                        for_logging=False
                    )
                else:
                    self.state.game_state["num_incorrect_tries"] -= 1
                    self.state.add_observation(
                        from_id=ta.GAME_ID,
                        to_id=-1,
                        message=f"Your guess of {letter} is not in the word. You have {self.state.game_state['num_incorrect_tries']} turns left.",
                        for_logging=False
                    )
                    break

            ## check if the game is over
            if self.state.game_state["num_incorrect_tries"] == 0:
                self.state.set_draw(reason="No turns left. Game over.")
            
            ## update the game board
            self.state.game_state["rendered_board"] = self._render_board(self.state.game_state["board"], show_letters=True)

        return self.state.step()
    
    def _reveal_letter(self, letter: str) -> None:
        """
        Reveal the letter in the target word.
        """
        for i, char in enumerate(self.chosen_word):
            if char == letter:
                self.state.game_state["board"][i] = letter
    
    def _is_game_over(self) -> bool:
        """
        Check if the game is over.
        """
        return self.state.game_state["board"] == self.game_board
    
    def render(self) -> None:
        """
        Render the environment.
        """
        print(self.state.game_state["rendered_board"])

