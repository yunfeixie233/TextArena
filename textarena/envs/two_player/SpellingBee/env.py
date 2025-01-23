
import re, random, string, enchant, numpy
from typing import Optional, Tuple, List, Dict, Any
import numpy as np 

import textarena as ta



class SpellingBeeEnv(ta.Env):
    """
    Environment for the Spelling Bee Game.
    """

    def __init__(self, num_letters: int):
        """
        Initialize the Spelling Bee Game environment.

        Args:
            num_letters (int): Number of unique allowed letters.
        """
        self.environment_name = "Spelling Bee Game"

        self.num_letters = num_letters

        # Initialize game state variables
        self.state = ta.State(
            num_players=2,
            max_turns=None,
        )

        # Initialize Enchant dictionaries for US and UK English
        try:
            self.word_checker_us = enchant.Dict("en_US")
            self.word_checker_uk = enchant.Dict("en_GB")
        except enchant.errors.DictNotFoundError as e:
            raise ValueError(f"Enchant dictionary not found: {e}. Ensure that the en_US and en_GB dictionaries are installed.")

    @property
    def offline_renderer(self):
        from textarena.envs.two_player.SpellingBee.render.renderer import SpellingBeeRenderer
        return SpellingBeeRenderer        

    @property
    def terminal_render_keys(self):
        return ["allowed_letters"]


    def reset(self, seed: Optional[int]=None):
        """
        Reset the Spelling Bee game to its initial state.

        Args:
            seed (Optional[int]): Seed for random number generator to ensure reproducibility.

        Returns:
            Tuple[Dict[int, List[Tuple[int, str]]], Dict[int, Any]]: Initial prompts for both players and additional info.
        """
        if seed is not None:
            random.seed(seed)

        # Generate allowed letters
        self.allowed_letters = self._generate_allowed_letters()

        self.state.reset(
            game_state={
                "allowed_letters": self.allowed_letters,
                "player_words": {0: None, 1: None},
            },
            player_prompt_function=self._generate_player_prompt
        )

    def _generate_allowed_letters(self) -> set:
        """
        Generate a random set of unique lowercase letters with a frequency-weighted distribution.
        """
        if self.num_letters > 26:
            raise ValueError("num_letters cannot exceed 26.")

        # Frequency of letters in the English language (rough estimates)
        letter_frequencies = {
            'a': 8.17, 'b': 1.49, 'c': 2.78, 'd': 4.25, 'e': 12.70, 'f': 2.23,
            'g': 2.02, 'h': 6.09, 'i': 7.00, 'j': 0.15, 'k': 0.77, 'l': 4.03,
            'm': 2.41, 'n': 6.75, 'o': 7.51, 'p': 1.93, 'q': 0.10, 'r': 5.99,
            's': 6.33, 't': 9.06, 'u': 2.76, 'v': 0.98, 'w': 2.36, 'x': 0.15,
            'y': 1.97, 'z': 0.07
        }

        letters = list(letter_frequencies.keys())
        weights = list(letter_frequencies.values())

        # Convert weights to probabilities that sum to 1.
        total_weight = sum(weights)
        probs = [w / total_weight for w in weights]

        # Use numpy.random.choice to sample without replacement
        allowed = np.random.choice(letters, size=self.num_letters, replace=False, p=probs)
        return set(allowed)


    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        """
        Generate the initial prompt for a player based on the allowed letters.

        Args:
            player_id (int): The player's ID (0 or 1).

        Returns:
            prompt (str): The initial prompt for the player.
        """
        prompt = (
            f"You are Player {player_id} in the Spelling Bee Game.\n"
            f"Allowed Letters: {''.join(sorted(self.allowed_letters))}\n"
            "Create the longest possible English word using only the allowed letters.\n"
            "You may use each letter multiple times.\n"
            "Please wrap your word in square brackets, e.g., '[example]'.\n"
            "On your turn, simply type your word.\n"
        )
        return prompt

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """
        Process the player's action.

        Args:
            action (str): The player's submitted word.

        Returns:
            tuple: (observations, rewards, truncated, terminated, info)
        """
        # update the log
        self.state.add_log(
            from_id=self.state.current_player_id,
            message=action
        )
        

        # add full action as player word for later verification
        # check if a word was given
        word = action.strip().lower()
        match = re.search(r"\[(\w+)\]", word)
        if match:
            # extract word
            word = match.group(1)
        else:
            word = None

        self.state.game_state["player_words"][self.state.current_player_id] = word


        if all (
            player_action is not None for player_action in self.state.game_state["player_words"].values()
        ):
            self.state.add_observation(
                from_id=ta.GAME_ID,
                to_id=-1,
                message=f"Submitted words:\n\tPlayer 0: {self.state.game_state['player_words'][0]}\n\tPlayer 1: {self.state.game_state['player_words'][1]}"
            )
            # verify both words
            w0_is_valid, w0_reason, w0_len = self._check_word_validity(
                word=self.state.game_state["player_words"][0],
                player_id=0
            )
            w1_is_valid, w1_reason, w1_len = self._check_word_validity(
                word=self.state.game_state["player_words"][1],
                player_id=1
            )

            if w0_is_valid and w1_is_valid:
                # compare word length to determine winner
                if w0_len == w1_len:
                    # draw
                    self.state.set_draw(reason="Both words have the same length.")
                else:
                    # determine winner
                    winner_id = 0 if w0_len > w1_len else 1
                    self.state.set_winners(
                        player_ids=[winner_id],
                        reason=f"Player {winner_id} won by providing a longer word."
                    )
            
            # invalid words
            else: 
                player_ids = numpy.array([0, 1])
                reasons = numpy.array([w0_reason, w1_reason])
                validity = numpy.array([w0_is_valid, w1_is_valid])

                self.state.set_invalid_move(
                    player_ids=player_ids[~validity],
                    reasons=reasons[~validity]
                )

        return self.state.step()



    def _evaluate_words(self) -> Dict[str, int]:
        """
        Evaluate the submitted words based on validity and length.

        Returns:
            Dict[str, int]: A dictionary with 'Player 0' and 'Player 1' as keys and their corresponding vote counts.
        """
        word_p0 = self.state.game_state["player_words"][0]
        word_p1 = self.state.game_state["player_words"][1]

        # Check validity
        is_valid_p0, reason_p0 = self._check_word_validity(word_p0)
        is_valid_p1, reason_p1 = self._check_word_validity(word_p1)

        votes = {"Player 0": 0, "Player 1": 0}

        # Both words invalid
        if not is_valid_p0 and not is_valid_p1:
            # No votes for either
            pass  # votes remain 0
        elif is_valid_p0 and not is_valid_p1:
            votes["Player 0"] += 1
        elif not is_valid_p0 and is_valid_p1:
            votes["Player 1"] += 1
        else:
            # Both words are valid; vote based on length
            len_p0 = len(word_p0)
            len_p1 = len(word_p1)
            if len_p0 > len_p1:
                votes["Player 0"] += 1
            elif len_p1 > len_p0:
                votes["Player 1"] += 1
            else:
                # Tie; no votes
                pass

        return votes

    def _check_word_validity(self, word: str, player_id: int) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if the submitted word is valid.

        Args:
            word (str): The submitted word.

        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (is_valid, reason, length)
        """
        allowed_letters = self.state.game_state["allowed_letters"]
        if word is None: 
            return False, f"No word was provided by Player {player_id}", None


        word_letters = set(word)


        # Check if all letters in the word are within the allowed letters
        if not word_letters.issubset(allowed_letters):
            return False, f"The word by Player {player_id} contains illegal characters.", None

        # Check if the word is a valid English word using Enchant
        is_valid = self.word_checker_us.check(word) or self.word_checker_uk.check(word)
        if not is_valid:
            return False, f"The word by Player {player_id} is not a valid English word.", None

        return True, None, len(word)