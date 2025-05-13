import random, copy
from typing import List, Dict, Any, Optional, Callable

import textarena as ta


class SinglePlayerState(ta.State):
    def __init__(self, num_players: int, seed: Optional[int]=None, max_turns: Optional[int]=None, error_allowance: Optional[int]=1):
        """
        Initialize the SinglePlayerState object.

        Args:
            num_players (int): The number of players in the game (asserts to 1 here)
            max_turns (Optional[int]): The maximum number of turns.
            error_allowance (Optional[int]): Number of errors allowed before a player loses the game.
            seed (Optional[int]): The random seed to be used
        """
        assert num_players==1, f"The number of players has to be 1, received {num_players}"

        self.max_turns = max_turns
        self.error_allowance = error_allowance
        super().__init__(num_players=num_players, seed=seed, max_turns=max_turns)

    def reset(self, game_state: Optional[Dict[str, Any]]=None, player_prompt_function: Optional[Callable]=None, role_mapping: Optional[Dict[int, str]]={0:"Player"}):
        self.standard_resets(game_state=game_state, player_prompt_function=player_prompt_function, role_mapping=role_mapping)
        self.error_count = 0
        self.made_invalid_move = False

        self.previous_game_state = copy.deepcopy(self.game_state)

    def step(self):
        if self.done: return (True, self.info)# if game happens to be terminated on last turn ...

        if not self.made_invalid_move:
            self.error_count = 0
            self.turn += 1 # increment turn counter
            self.previous_game_state = copy.deepcopy(self.game_state)

        self.made_invalid_move = False # reset
        info = self.info 
        self.info = {} # reset info
        return (self.done, info)


    def set_outcome(self, reward: float, reason: Optional[str]=None):
        self.rewards = {0: reward}
        self.info["reason"] = reason
        self.info["turn_count"] = self.turn + 1 # finished on the (n+1)th turn
        self.done = True

    def set_invalid_move(self, reason: Optional[str]):
        if self.error_allowance > self.error_count:
            self.error_count += 1 # increment error count
            self.made_invalid_move = True
            self.add_observation(message=f"You attempted an invalid move. Reason: {reason} Please resubmit a valid move and remember to follow the game rules to avoid penalties.")
            self.game_state = self.previous_game_state.copy()
        else:
            self.set_outcome(reward=-1, reason=f"Invalid Move: {reason}")
