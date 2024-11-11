""" WordChains Environment """

import re 
import random 


import nltk 
import enchant
from nltk.corpus import words 
nltk.download("words")


import textarena as ta 


class WordChainsEnv(ta.Env):
    """ Environment for Word Chains Game """
    def __init__(self, max_turns: Optional[int]=None):
        """
        Initialize the Word Chains Game.

        Args:
            max_turns (int): Maximum number of turns before the game ends in a draw.
        """

        # Ensure NLTK words are loaded
        self.word_lis = list(set(word.lower() for word in words.words()))

        # Initialize Enchant dictionaries for US and UK English
        try:
            self.word_checker_us = enchant.Dict("en_US")
            self.word_checker_uk = enchant.Dict("en_GB")
        except enchant.errors.DictNotFoundError as e:
            raise ValueError(f"Enchant dictionary not found: {e}. Ensure that the en_US and en_GB dictionaries are installed.")


        # Initialize game state
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
            render_keys=["current_word", "required_start_letter"]
        )

    def reset(self, seed: Optional[int] = None) -> ta.Observation:
        """ TODO """
        if seed is not None:
            random.seed(seed)
        else:
            random.seed()

        starting_word = random.choice(self.word_list)


        return self.state.reset(
            game_state={
                "current_word": starting_word,
                "used_words": set(starting_word),
                "required_start_letter": starting_word[-1].lower()
            },
            player_prompt_function=self._generate_player_prompt
        )


    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """ TODO """
        prompt = (
            f"You are Player {player_id} in the Word Chains Game.\n"
            "Players take turns to provide valid English words that start with the last letter of the previous word.\n"
            "Repetition of words is not allowed.\n"
            "If you provide an invalid word, repeat a word, or fail to follow the sequence, you lose.\n"
            "Please wrap your word in square brackets, e.g., '[apple]', '[monkey'], etc. .\n"
            f"The starting word is [{game_state['current_word']}]. Please provide the next word.\n"
            "On your turn, simply type your word.\n"
        )
        if self.state.max_turns:
            prompt += f"The game will end after {self.state.max_turns} turns if no player loses.\n"
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
        """ TODO """
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

        # Extract the word from the action
        word_match = re.search(r"\[(\w+)\]", action)
        if not word_match:
            # Invalid format
            self.state.set_invalid_move(
                player_ids=[player_id],
                reasons=[f"The Player {player_id} did not provide a new word."]
            )

        else:
            word = word_match.group(1).lower()
            # Check if the word starts with the required letter
            if not word.startswith(self.state.game_state["required_start_letter"]):
                # Invalid format
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"The word provided by Player {player_id} did start with the correct letter."]
                )

            # Check if the word is a valid English word
            elif not (
                self.word_checker_us.check(word) or self.word_checker_uk.check(word)
            ):
                # Invalid word
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=[f"The word provided by Player {player_id} is not a valid english word."]
                )


                