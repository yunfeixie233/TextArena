import random
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Tuple, Optional, Callable

class ObservationType(Enum):
    PROMPT = auto() # the player prompts
    PLAYER_ACTION = auto() # a player submitting an action 
    GAME_ACTION_DESCRIPTION = auto() # the game describing a player action
    GAME_MESSAGE = auto() # minor game messages not directly dependent on actions
    GAME_BOARD = auto() # the actual game-board visualization
    GAME_ADMIN = auto() # invalid moves, win/loss, etc.


GAME_ID = -1  # literal for use in game messages
Message = Tuple[int, str, ObservationType]  # maps role to content
Observations = dict[int, List[Message]]  # consists of the message seen by each player after the action
Rewards = Dict[int, int]  # maps player ID to reward
Info = Dict[str, Any]  # additional information about the environment



class State:
    def __init__(self, num_players: int, seed: Optional[int]=None, max_turns: Optional[int]=None):
        if seed is not None: random.seed(seed) # set the random seed
        self.max_turns = max_turns 
        self.num_players = num_players
        self.current_player_id = 0

    def check_turn_limit(self):
        return self.turn >= self.max_turns and self.done == False

    def update_current_player_id(self, player_id: int):
        assert player_id in self.role_mapping, f"Tried to update current player to {player_id}, which does not exist. Available players: {list(self.role_mapping.keys())}"

    def standard_resets(self, game_state: Optional[Dict[str, Any]]=None, player_prompt_function: Optional[Callable]=None, role_mapping: Optional[Dict[int, str]]={}):
        self.game_state = game_state
        self.role_mapping = role_mapping
        
        # reset standard game parameters
        self.turn = 0
        self.done = False 
        self.step_info = {}
        self.game_info = {pid: {} for pid in range(self.num_players)}
        self.observations = {pid: [] for pid in range(self.num_players)}
        self.rewards = None
        self.logs = []

        # set role mapping
        if self.role_mapping is None:
            for pid in range(self.num_players):
                self.role_mapping[pid] = f"Player {pid}"
        self.role_mapping[GAME_ID] = self.role_mapping.get(GAME_ID, "GAME") # add if not provided

        # generate the player prompts
        if player_prompt_function is not None:
            for player_id in range(self.num_players):
                self.add_observation(to_id=player_id, message=player_prompt_function(player_id=player_id, game_state=self.game_state), observation_type=ObservationType.PROMPT)

    def add_observation(self, message: str, observation_type: ObservationType, from_id: int=GAME_ID, to_id: int=-1):
        self.logs.append((from_id, message))
        if to_id == -1:
            for pid in range(self.num_players):
                self.observations[pid].append((from_id, message, observation_type))
        else:
            assert to_id in self.observations, f"The provided 'to_id' {to_id} does not exists. ({list(self.observations.keys())})"
            self.observations[to_id].append((from_id, message, observation_type))

    def get_current_player_observation(self):
        current_player_observation = self.observations[self.current_player_id]
        self.observations[self.current_player_id] = []
        return current_player_observation

    def step(self):
        if self.done: return (True, self.info)# if game happens to be terminated on last turn ...
        self.turn += 1 # increment turn counter
        info = self.info 
        self.info = {} # reset info
        return (self.done, info)

    def close(self):
        return self.rewards





class StateOLD:
    """ A class to manage the state of the game, including observations, rewards, and some game logic """
    def __init__(
        self,
        num_players: int,
        min_players: Optional[int] = None,
        max_players: Optional[int] = None,
        even_player_num: Optional[int] = False,
        odd_player_num: Optional[int] = False,
        max_turns: Optional[int] = None,
        role_mapping: Optional[Dict[int, str]] = {},
        check_truncated: Optional[bool] = True,
        error_allowance: Optional[int] = 1,
        seed: Optional[int] = None,
    ):
        """
        Initialize the State object.

        Args:
            num_players (int): Number of players in the game.
            max_turns (Optional[int]): Maximum number of turns before the game is truncated.
            role_mapping (Optional[Dict[int, str]]): Mapping from player IDs to role names.
            check_truncated (Optional[bool]): Whether to check for truncated games.
            error_allowance (Optional[int]): Number of errors allowed before a player loses the game.
        """
        # assert the number of players
        assert min_players<=num_players<=max_players, \
            f"The number of players needs to be in range {min_players}<=num_player<={max_players}. You provided {num_players}"

        if even_player_num:
            assert num_players%2==0, \
                f"The number of players needs to be even. You provided {num_players}"

        if odd_player_num:
            assert num_players%2==1, \
                f"The number of players needs to be odd. You provided {num_players}"

        self.num_players = num_players
        self.max_turns = max_turns
        self.check_truncated = check_truncated
        self.error_allowance = error_allowance
        self.error_count = 0

        # set standard state parameters
        self.turn = 0
        self.current_player_id = 0

        self.role_mapping = role_mapping
        self.role_mapping[-1] = "GAME"

        # set the seed
        if seed is not None:
            random.seed(seed)

    def standard_resets(self, game_state: Optional[Dict[str, Any]]=None, player_prompt_function: Optional[Callable]=None, role_mapping: Optional[Dict[int, str]]=None):
        """ Reset the game state """
        self.game_state = game_state
        self.current_player_id = 0
        self.turn = 0
        self.prevent_player_change = False 

        if not role_mapping is None:
            for pid, role in role_mapping.items():
                self.role_mapping[pid] = role
        self._reset_game_parameters()
        # generate the player prompts
        if player_prompt_function is not None:
            for player_id in range(self.num_players):
                message=player_prompt_function(player_id=player_id, game_state=self.game_state)
                self.add_observation(from_id=GAME_ID, to_id=player_id, message=message)

    def _reset_game_parameters(self):
        """ Reset the game parameters at the start of the game or after each step """
        self.done = False 
        self.info = {}
        self.rewards = None
        self.observations = {pid: [] for pid in range(self.num_players)}

    def add_observation(self, from_id: int, to_id: int, message: str):
        """
        Add an observation message to the observations.

        Args:
            from_id (int): The ID of the sender (player or game).
            to_id (int): The ID of the receiver (-1 for all players).
            message (str): The message content.
        """
        # add to observations
        if to_id == -1:
            for pid in range(self.num_players):
                self.observations[pid].append((from_id, message))
        else:
            assert to_id in self.observations, f"The provided 'to_id' {to_id} does not exists. ({list(self.observations.keys())})"
            self.observations[to_id].append((from_id, message))

    def get_turn_count(self):
        return self.turn

    def step(self, rotate_player: bool = True):
        """
        Advance the game state by one turn.

        Args:
            rotate_player (bool): Whether to rotate the current player after the step.

        Returns:
            Tuple[bool, Dict[str, Any]] # done, info 
        """
        if self.done:  # if game happens to be terminated on last turn...
            return (True, self.info)

        # increment turn counter
        if not self.prevent_player_change:
            self.turn += 1

        # check if the turn limit has been reached
        if self.max_turns is not None and self.turn >= self.max_turns and self.check_truncated:
            self.rewards = {pid: 0 for pid in range(self.num_players)} # set the rewards

            # log the reason & update info
            reason = "Turn limit reached"
            self.info["detailed_reason"] = reason
            self.info["reason"] = "Draw."
            self.done = True

        info = self.info
        done = self.done
        rewards = self.rewards

        # update current player
        if rotate_player and not self.prevent_player_change:
            prev_player = self.current_player_id
            self.current_player_id = (self.current_player_id + 1) % self.num_players
            self.error_count = 0

        self.info = {}
        self.reward = None
        self.prevent_player_change = False

        return (done, info)

    def manually_update_current_player(self, new_player_id):
        if not self.prevent_player_change:
            self.current_player_id = new_player_id
            self.error_count = 0

    def get_current_player_observation(self):
        current_player_observation = self.observations[self.current_player_id]
        self.observations[self.current_player_id] = [] # reset observations
        return current_player_observation

    def close(self):
        return self.rewards

    def set_winners(self, player_ids: List[int], reason: Optional[str]):
        self.rewards = {} # set the rewards
        for player_id in range(self.num_players):
            self.rewards[player_id] = 1 if player_id in player_ids else -1

        # log the reason & update info
        message=f"Player {player_ids[0]} won the game. Reason: {reason}"
        self.add_observation(from_id=GAME_ID, to_id=-1, message=message)
        self.info["reason"] = reason
        self.info["trun_count"] = self.turn
        self.done = True

    def set_draw(self, reason: Optional[str]):
        """ Declare the game as a draw """
        self.rewards = {pid: 0 for pid in range(self.num_players)} # set the rewards

        # log the reason & update info
        message=f"The game ended in a draw. Reason: {reason}"
        self.add_observation(from_id=GAME_ID, to_id=-1, message=message)
        self.info["reason"] = reason
        self.info["trun_count"] = self.turn
        self.done = True

    def set_invalid_move(self, player_id: int, reason: Optional[str]):
        """ Handle an invalid move made by a player """
        if self.error_allowance > self.error_count:
            self.error_count += 1 # increment error count
            self.prevent_player_change = True 
            message=f"Player {player_id} attempted an invalid move. Reason: {reason} Please resubmit a valid move and remember to follow the game rules to avoid penalties."
            self.add_observation(from_id=GAME_ID, to_id=player_id, message=message)
        else:
            self.rewards = {} # set the rewards
            for pid in range(self.num_players):
                self.rewards[pid] = -1 if pid==player_id else 0

            # log the reason & update info
            message=f"Player {player_id} lost the game by way of invalid move. Reason: {reason}"
            self.add_observation(from_id=GAME_ID, to_id=-1, message=message)
            self.info["reason"] = f"Invalid Move: {reason}"
            self.info["trun_count"] = self.turn
            self.done = True

    def set_custom_game_outcome(self, player_reward_dict: Dict[int, float], reason: Optional[str]=None):
        self.rewards = player_reward_dict # set the rewards
        if reason is not None: # log the reason & update info
            self.add_observation(from_id=GAME_ID, to_id=-1, message=f"Custom Game Outcome. Reason: {reason}")
        self.info["reason"] = reason
        self.done = True

    def set_singleplayer_game_outcome(self, reward: float, reason: Optional[str]=None):
        self.rewards = {0: reward} # set the rewards
        if reason is not None:
            self.add_observation(from_id=GAME_ID, to_id=-1, message=f"Game Complete. Reason: {reason}")
        self.info["reason"] = reason
        self.info["turn_count"] = self.turn
        self.done = True


class Env(ABC):
    """
    Abstract base class for text-based game environments.

    This class outlines the interface for the environment, including methods for resetting the environment,
    stepping through the environment (taking actions), and rendering the environment state.
    """
    game_state: State  # the state of the environment

    @abstractmethod
    def reset(self, num_players: int, seed: Optional[int]=None):
        """
        Resets the environment to an initial state.

        Args:
            num_players (int): Number of players in the game.
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.
        """
        raise NotImplementedError

    @abstractmethod
    def step(self, action: str) -> Tuple[bool, Info]:
        """
        Performs a single step in the environment.

        Args:
            player_id (int): The ID of the player taking the action.
            action (str): The action to be taken by the player.

        Returns:
            Tuple containing:
                - done (bool): Whether the episode has concluded
                - info (Dict[str, Any]): Additional information about the environment.
        """
        raise NotImplementedError

    def get_observation(self):
        return self.state.current_player_id, self.state.get_current_player_observation()

    def close(self):
        rewards = self.state.close()
        return rewards

class Wrapper(Env):
    """ Base class for environment wrappers. """
    def __init__(self, env):
        # Confirm we are not double-wrapping with the same wrapper type
        if isinstance(env, Wrapper) and env.is_wrapped_with(type(self)):
            raise ValueError(f"Environment is already wrapped with {type(self).__name__}. Double-wrapping is not allowed.")
        self.env = env

    def __getattr__(self, name):
        return getattr(self.env, name)

    def reset(self, num_players: int , seed: Optional[int] = None):
        return self.env.reset(num_players=num_players, seed=seed)

    def step(self, action: str) -> Tuple[bool, Info]:
        return self.env.step(action=action)

    def get_observation(self):
        return self.env.get_observation()

    def close(self):
        return self.env.close()

    def __deepcopy__(self, memo):
        import copy
        copied_env = copy.deepcopy(self.env, memo) # Deepcopy the wrapped environment
        cls = self.__class__ # Create a new wrapper of the same type
        copied_wrapper = cls(copied_env)
        for k, v in self.__dict__.items(): # Copy any other attributes (excluding .env)
            if k != "env":
                setattr(copied_wrapper, k, copy.deepcopy(v, memo))
        return copied_wrapper

    def is_wrapped_with(self, wrapper_class: type) -> bool:
        env = self
        while isinstance(env, Wrapper):
            if isinstance(env, wrapper_class):
                return True
            env = env.env
        return False


class ObservationWrapper(Wrapper):
    def get_observation(self):
        player_id, observation = self.env.get_observation()
        return player_id, self.observation(player_id, observation)
    
    def observation(self):
        raise NotImplementedError


class RenderWrapper(Wrapper):
    def step(self, action: str) -> Tuple[bool, Optional[Info]]:
        return self.env.step(action=action)
    
    def reset(self, num_players: int , seed: Optional[int] = None):
        self.reset_render()
        return self.env.reset(num_players=num_players, seed=seed)

    def reset_render(self):
        raise NotImplementedError


class ActionWrapper(Wrapper):
    def step(self, action: str) -> Tuple[bool, Optional[Info]]:
        return self.env.step(action=self.action(action))

    def action(self, action: str) -> str:
        raise NotImplementedError


class Agent(ABC):
    """ Generic agent class that defines the basic structure of an agent """
    @abstractmethod
    def __call__(self, observation: str) -> str:
        """
        Process the observation and return the action.

        Args:
            observation (str): The input string to process.

        Returns:
            str: The response generated by the agent.
        """
        pass


class AgentWrapper(Agent):
    """ TODO """
    def __init__(self, agent: Agent):
        """ TODO """
        self.agent = agent 
        assert isinstance(agent, Agent)

    def __getattr__(self, name):
        """ TODO """
        return getattr(self.agent, name)

    def __call__(self, observation: str) -> str:
        return self.agent(observation=observation)




