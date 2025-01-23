import nltk, random 
from nltk import pos_tag
from nltk.corpus import words
from typing import Any, Dict, Optional, Tuple, List

import textarena as ta



nltk.download("words")
nltk.download("averaged_perceptron_tagger_eng")


class DontSayItEnv(ta.Env):
    """Environment for Don't Say It game"""
    def __init__(
        self,
        hardcore: Optional[bool] = False,
        max_turns: Optional[int] = None,
    ):
        """
        Initialize the 'Don't Say It' game environment.

        Args:
            hardcore (bool): If True, use the full English word set; otherwise, use a simplified word set.
            max_turns (int): Maximum number of turns before the game ends in a draw.
        """
        # Load the word list
        self._load_word_list(hardcore=hardcore)

        # Initialize game state (mostly used by wrappers, especially rendering)
        self.state = ta.State(
            num_players=2,
            max_turns=max_turns,
        )

    @property
    def offline_renderer(self):
        from textarena.envs.two_player.DontSayIt.render.renderer import DontSayItRenderer
        return DontSayItRenderer

    @property
    def terminal_render_keys(self):
        return ["target_words"]

    def _load_word_list(self, hardcore: bool = False) -> None:
        """
        Load the word list based on the 'hardcore' parameter.

        Args:
            hardcore (bool): Determines whether to load the full or simplified word list.
        """
        # Get word list
        if hardcore:
            word_list = words.words("en")
        else:
            word_list = words.words("en-basic")

        # Filter words based on POS tags
        # NN: Noun, VB: Verb, JJ: Adjective
        self.word_list = [
            word for word in word_list if pos_tag([word])[0][1] in ["NN", "VB", "JJ"]
        ]

    def reset(self, seed: Optional[int]=None):
        """
        Reset the 'Don't Say It' game to its initial state.

        Args:
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Optional[ta.Observations]: Initial observations for both players as a dictionary.
        """
        if seed is not None:
            random.seed(seed)

        # Assign secret words to players
        target_words = {
            0: random.choice(self.word_list),
            1: random.choice(self.word_list),
        }
        while target_words[0] == target_words[1]:
            target_words[1] = random.choice(self.word_list)

        self.state.reset(
            game_state={"target_words": target_words},
            player_prompt_function=self._generate_player_prompt
        )

    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        """
        Generate the initial prompt for a player, providing them with their secret word and instructions.

        Args:
            player_id (int): ID of the player (0 or 1).

        Returns:
            ta.Message: Initial prompt for the player.
        """
        prompt = (
            f"You are playing 'Don't Say It'. You are Player {player_id}\n"
            f"Your secret word is: '{self.state.game_state['target_words'][player_id]}'.\n"
            "Your goal is to get the other player to say your secret word before you say theirs.\n"
            "You can converse freely, but try to be subtle to avoid making it obvious.\n"
            "On your turn, simply type your message.\n"
        )
        if self.state.max_turns:
            prompt += f"The game lasts for {self.state.max_turns} turns in total.\n"
        return prompt

    def get_current_player_id(self):
        return self.state.current_player 

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """
        Process the player's action.

        Args:
            action (str): The player's message.

        Returns:
            tuple: (observations, rewards, truncated, terminated, info)
        """
        # update the observations and log the action
        self.state.add_observation(
            from_id=self.state.current_player_id,
            to_id=-1, # Broadcast to all
            message=action,
            for_logging=True
        )

        # Check if the action mentions the opponent's secret word
        if self.state.game_state["target_words"][1 - self.state.current_player_id].lower() in action.lower().split():
            self.state.set_winners(
                player_ids=[1-self.state.current_player_id], # opponent wins
                reason=f"Player {self.state.current_player_id} mentioned the opponent's secret word."
            )            

        return self.state.step()

