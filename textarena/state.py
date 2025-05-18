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


class TwoPlayerState(ta.State):
    def __init__(self, num_players: int, seed: Optional[int]=None, max_turns: Optional[int]=None, error_allowance: Optional[int]=1):
        """
        Initialize the SinglePlayerState object.

        Args:
            num_players (int): The number of players in the game (asserts to 2 here)
            max_turns (Optional[int]): The maximum number of turns.
            error_allowance (Optional[int]): Number of errors allowed before a player loses the game.
            seed (Optional[int]): The random seed to be used
        """
        assert num_players==2, f"The number of players has to be 2, received {num_players}"

        self.max_turns = max_turns
        self.error_allowance = error_allowance
        super().__init__(num_players=num_players, seed=seed, max_turns=max_turns)

    def reset(self, game_state: Optional[Dict[str, Any]]=None, player_prompt_function: Optional[Callable]=None, role_mapping: Optional[Dict[int, str]]={0:"Player 0", 1:"Player 1"}):
        self.standard_resets(game_state=game_state, player_prompt_function=player_prompt_function, role_mapping=role_mapping)
        self.error_count = 0
        self.made_invalid_move = False
        self.previous_game_state = copy.deepcopy(self.game_state)

    def step(self, rotate_player: bool=True):
        if self.done: return (True, self.info)# if game happens to be terminated on last turn ...

        if not self.made_invalid_move:
            self.error_count = 0
            self.turn += 1 # increment turn counter
            self.previous_game_state = copy.deepcopy(self.game_state)


        if rotate_player and not self.made_invalid_move:
            self.current_player_id = 1-self.current_player_id
            self.error_count = 0

        self.made_invalid_move = False # reset
        info = self.info 
        self.info = {} # reset info
        return (self.done, info)

    def manually_set_current_player_id(self, new_player_id: int):
        if not self.made_invalid_move:
            self.current_player_id = new_player_id
            self.error_count = 0

    def set_winner(self, player_id: int, reason: str):
        self.rewards = {player_id: 1, 1-player_id: -1}
        self.info["reason"] = reason
        self.info["turn_count"] = self.turn + 1 # finished on the (n+1)th turn
        self.info["end_by_invalid"] = False
        self.done = True

    def set_draw(self, reason: str):
        self.rewards = {0: 0, 1: 0}
        self.info["reason"] = reason
        self.info["turn_count"] = self.turn + 1 # finished on the (n+1)th turn
        self.info["end_by_invalid"] = False
        self.done = True


    def set_invalid_move(self, reason: str):
        if self.error_allowance > self.error_count:
            self.error_count += 1 # increment error count
            self.made_invalid_move = True
            self.add_observation(to_id=self.current_player_id, message=f"Player {self.current_player_id} attempted an invalid move. Reason: {reason} Please resubmit a valid move and remember to follow the game rules to avoid penalties.")
            self.game_state = self.previous_game_state.copy()
        else:
            self.rewards = {self.current_player_id: -1, 1-self.current_player_id: 1}
            self.info["reason"] = reason
            self.info["turn_count"] = self.turn + 1 # finished on the (n+1)th turn
            self.info["end_by_invalid"] = True
            self.done = True



# class FFAMultiPlayerState(ta.State):
#     def __init__(self, num_players: int, min_players: int, max_players:int, seed: Optional[int]=None, max_turns: Optional[int]=None, error_allowance: Optional[int]=1):
#         """
#         Initialize the SinglePlayerState object.

#         Args:
#             num_players (int): The number of players in the game 
#             min_players (int): The minimum number of players for the game
#             max_players (int): The maxiumum number of players for the game
#             max_turns (Optional[int]): The maximum number of turns.
#             error_allowance (Optional[int]): Number of errors allowed before a player loses the game.
#             seed (Optional[int]): The random seed to be used
#         """
#         assert min_players<=num_players<=max_players, f"The number of players has to be between {min_players} and {max_players}; received {num_players}"

#         self.max_turns = max_turns
#         self.error_allowance = error_allowance
#         super().__init__(num_players=num_players, seed=seed, max_turns=max_turns)

#     def reset(self, game_state: Optional[Dict[str, Any]]=None, player_prompt_function: Optional[Callable]=None, role_mapping: Optional[Dict[int, str]]=None):
#         self.standard_resets(game_state=game_state, player_prompt_function=player_prompt_function, role_mapping=role_mapping)
#         self.error_count = 0
#         self.made_invalid_move = False
#         self.player_status = {i:{"alive":True, "death_turn": None, "reason": None} for i in range(self.num_players)}
#         self.previous_game_state = copy.deepcopy(self.game_state)

#     def step(self, rotate_player: bool=True):
#         if self.done: return (True, self.info)# if game happens to be terminated on last turn ...

#         if not self.made_invalid_move:
#             self.error_count = 0
#             self.turn += 1 # increment turn counter
#             self.previous_game_state = copy.deepcopy(self.game_state)


#         if rotate_player and not self.made_invalid_move:
#             # rotate to the next alive player
#             next_pid, alive = self._get_next_alive_player()
#             self.current_player_id = 1-self.current_player_id
#             self.error_count = 0

#         self.made_invalid_move = False # reset
#         info = self.info 
#         self.info = {} # reset info
#         return (self.done, info)

#     def _get_next_alive_player(self) -> Tuple[Optional[int], bool]:
#         """Finds the next alive player in a circular fashion."""
#         for i in range(1, self.num_players + 1):
#             candidate = (self.current_player_id + i) % self.num_players
#             if self.player_status[candidate]["alive"]: 
#                 return candidate, True
#         return None, False

#     def all_dead(self) -> bool:
#         for i in range(1, self.num_players + 1):
#             candidate = (self.current_player_id + i) % self.num_players
#             if self.player_status[candidate]["alive"]: 
#                 return False
#         return True
        


#     def manually_set_current_player_id(self, new_player_id: int):
#         if not self.made_invalid_move:
#             self.current_player_id = new_player_id
#             self.error_count = 0

#     def set_winner(self, player_id: int, reason: str):
#         self.rewards = {player_id: 1, 1-player_id: -1}
#         self.info["reason"] = reason
#         self.info["turn_count"] = self.turn + 1 # finished on the (n+1)th turn
#         self.info["end_by_invalid"] = False
#         self.done = True

#     def set_draw(self, reason: str):
#         self.rewards = {0: 0, 1: 0}
#         self.info["reason"] = reason
#         self.info["turn_count"] = self.turn + 1 # finished on the (n+1)th turn
#         self.info["end_by_invalid"] = False
#         self.done = True


#     def set_invalid_move(self, reason: str):
#         if self.error_allowance > self.error_count:
#             self.error_count += 1 # increment error count
#             self.made_invalid_move = True
#             self.add_observation(to_id=self.current_player_id, message=f"Player {self.current_player_id} attempted an invalid move. Reason: {reason} Please resubmit a valid move and remember to follow the game rules to avoid penalties.")
#             self.game_state = self.previous_game_state.copy()
#         else:
#             self.error_count = 0
#             self.player_status[self.current_player_id]["alive"] = False
#             self.player_status[self.current_player_id]["death_turn"] = self.turn
#             self.player_status[self.current_player_id]["reason"] = reason
#             self.player_status[self.current_player_id]["end_by_invalid"] = True
#             # self.rewards = {self.current_player_id: -1, 1-self.current_player_id: 1}
#             # self.info["reason"] = reason
#             # self.info["turn_count"] = self.turn + 1 # finished on the (n+1)th turn
#             # self.info["end_by_invalid"] = True
#             # self.done = True
