import re, random
from typing import Any, Dict, Optional, Tuple, List

import textarena as ta


class DiplomacyEnv(ta.Env):
    """ Env for Diplomacy """
    def __init__(self, game_rules: str, max_turns: int):
        """ 
        Initialize the Diplomacy game environment 

        Args:
            max_turns (int): The maximum number of turns before
                the game ends in a draw 
        """
        super().__init__()
        self.game_rules = game_rules
        self.max_turns = max_turns 

    def reset(self, num_players: int, seed: Optional[int]=None):
        """ TODO """
        self.state = ta.State(num_players=num_players, min_players=3, max_players=7, max_turns=self.max_turns)

        # create game state 


        self.state.reset(seed=seed, game_state=game_state, player_prompt_function=self._generate_player_prompt)

    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """ TODO """
        prompt = (
            f"You are Player {player_id} in a game of Diplomacy playing as {TODO}"
            TODO
        )    
        return prompt


    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """ Execute the player moves """
        return self.state.step(rotate_player=False)



    def _rotate_current_player(self):
        pass 


    def _augment_final_observation(self):
        return 