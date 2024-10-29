from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional, Callable

GAME_ID = -1  # literal for use in game messages
Message = Tuple[int, str]  # maps role to content
Observations = dict[int, List[Message]]  # consists of the message seen by each player after the action
Rewards = Dict[int, int]  # maps player ID to reward
Info = Dict[str, Any]  # additional information about the environment


class State:
    """
    A class to manage the state of the game, 
    including observations, rewards, and some game logic.
    """
    def __init__(
        self,
        num_players: int,
        max_turns: Optional[int] = None,
        render_keys: Optional[List[str]] = None,
        role_mapping: Optional[Dict[int, str]] = {},
    ):
        """
        Initialize the State object.

        Args:
            num_players (int): Number of players in the game.
            max_turns (Optional[int]): Maximum number of turns before the game is truncated.
            render_keys (Optional[List[str]]): Keys in the game_state to be rendered during logging.
            role_mapping (Optional[Dict[int, str]]): Mapping from player IDs to role names.
        """
        self.num_players = num_players
        self.max_turns = max_turns
        self.render_keys = render_keys 

        # set standard state parameters
        self.logs = [] 
        self.turn = 0
        self.current_player = 0

        self.role_mapping = role_mapping 
        self.role_mapping[-1] = "GAME"



    def reset(
        self,
        game_state: Dict[str, Any],
        player_prompt_function: Callable,
    ):
        """
        Reset the game state.

        Args:
            game_state (Dict[str, Any]): Initial game state to be set.
        """
        self.game_state = game_state
        self.current_player = 0
        self.turn = 0

        self.logs.append((GAME_ID, "Game started."))

        self._reset_game_parameters()

        # generate the player prompts
        for player_id in range(self.num_players):
            self.add_observation(
                from_id=GAME_ID,
                to_id=player_id,
                message=player_prompt_function(player_id=player_id),
                for_logging=False
            )

        return self.get_observations()


    def _reset_game_parameters(self):
        """
        Reset the game parameters at the start of the game or after each step.
        """
        self.terminated = False 
        self.truncated = False 
        self.info = {}
        self.rewards = None 
        self.observations = {pid: [] for pid in range(self.num_players)}

    def add_observation(self, from_id: int, to_id: int, message: str, for_logging: bool = True):
        """
        Add an observation message to the observations and logs.

        Args:
            from_id (int): The ID of the sender (player or game).
            to_id (int): The ID of the receiver (-1 for all players).
            message (str): The message content.
            for_logging (bool): If True, the message is added to the logs.
        """
        if for_logging:
            # log the observation
            self.logs.append((from_id, message))

        # add to observations
        if to_id == -1:
            for pid in self.observations:
                self.observations[pid].append(
                    (from_id, message)
                )
        else:
            assert to_id in self.observations, \
                f"The provided 'to_id' {to_id} does not exists. ({list(self.observations.keys())})"
            self.observations[to_id].append(
                (from_id, message)
            )

    def add_log(self, from_id: int, message: str):
        """ TODO """
        self.logs.append((from_id, message))


    def check_action_format(self, action, player_id):
        """
        Check the validity of a player's action.

        Args:
            action (str): The action to check.
            player_id (int): The ID of the player performing the action.

        Raises:
            AssertionError: If the action or player ID is invalid.
        """
        assert isinstance(
            action, str
        ), f"Actions are required to be strings. Received dtype: {type(action)}"
        assert isinstance(
            player_id, int
        ), f"Player ids are required to be integers. Received dtype: {type(player_id)}"
        assert (
            player_id == self.current_player
        ), f"The passed player_id is not as expected. Player id received: {player_id}; Expected: {self.current_player}"

    def get_observations(self) -> Optional[Observations]:
        """
        Retrieve the current observations and reset the observations dictionary.

        Returns:
            Dict[int, List[Tuple[int, str]]]: The current observations for each player.
        """
        observations = self.observations
        self.observations = {pid: [] for pid in range(self.num_players)}
        return observations

    def step(self):
        """
        Advance the game state by one turn.

        Returns:
            Tuple[
                Dict[int, List[Tuple[int, str]]],  # observations
                Optional[Dict[int, int]],           # rewards
                bool,                               # truncated
                bool,                               # terminated
                Dict[str, Any],                     # info
            ]: The updated game state after the step.
        """

        # increment turn counter
        self.turn += 1

        
        # check if the turn limit has been reached
        if self.max_turns is not None and self.turn >= self.max_turns:
            # set the rewards
            self.rewards = {pid:0 for pid in range(self.num_players)}

            # log the reason & update info
            reason = "Turn limit reached"
            self.logs.append((GAME_ID, reason))
            self.info["detailed_reason"] = reason 
            self.info["reason"] = "Draw." 
            self.truncated  = True 


        observations = self.get_observations()
        info = self.info 
        terminated = self.terminated
        truncated = self.truncated 
        rewards = self.rewards


        # update current player 
        self.current_player = (self.current_player+1) % self.num_players

        self._reset_game_parameters()

        return observations, rewards, truncated, terminated, info 



    def set_winners(self, player_ids: List[int], reason: Optional[str]):
        """
        Set the winners of the game.

        Args:
            player_ids (List[int]): List of player IDs who have won.
            reason (Optional[str]): Reason for winning.
        """

        # set the rewards
        self.rewards = {}
        for player_id in range(self.num_players):
            if player_id in player_ids:
                self.rewards[player_id] = 1
            else:
                self.rewards[player_id] = -1


        # log the reason & update info
        self.logs.append((GAME_ID, reason))
        self.info["detailed_reason"] = reason 
        self.info["reason"] = "Winner determined."
        self.terminated = True 


    def set_draw(self, reason: Optional[str]):
        """
        Declare the game as a draw.

        Args:
            reason (Optional[str]): Reason for the draw.
        """
        # set the rewards
        self.rewards = {pid:0 for pid in range(self.num_players)}

        # log the reason & update info
        self.logs.append((GAME_ID, reason))
        self.info["detailed_reason"] = reason 
        self.info["reason"] = "Draw." 
        self.terminated = True 


    def set_invalid_move(self, player_ids: List[int], reasons: Optional[List[str]]):
        """
        Handle an invalid move made by a player.

        Args:
            player_ids (List[int]): List of player IDs who made an invalid move.
            reason (Optional[str]): Reason for the invalid move.
        """

        # set the rewards
        self.rewards = {}
        for player_id in range(self.num_players):
            if player_id in player_ids:
                self.rewards[player_id] = -1
            else:
                self.rewards[player_id] = 0

        # log the reason & update info
        self.logs.append((GAME_ID, "; ".join(reasons)))
        self.info["detailed_reason"] = "; ".join(reasons) 
        self.info["reason"] = "Invalid Move."
        self.terminated = True 




class Env(ABC):
    """
    Abstract base class for text-based game environments.

    This class outlines the interface for the environment, including methods for resetting the environment,
    stepping through the environment (taking actions), and rendering the environment state.
    """

    #environment_name: str  # the name of the environment
    game_state: State  # the state of the environment

    @abstractmethod
    def reset(
        self, seed: Optional[int] = None
    ) -> Optional[Observations]:
        """
        Resets the environment to an initial state.

        Args:
            observations (Optional[Dict[int, str]]): Initial observations for the players.
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Depending on implementation, should return initial observations and any additional info.
        """
        raise NotImplementedError

    @abstractmethod
    def step(
        self,
        player_id: int,
        action: str,
    ) -> tuple[
        Observations,  # player-wise observations
        Rewards,  # player-wise reward
        bool,  # truncated
        bool,  # terminated
        Info,  # info
    ]:
        """
        Performs a single step in the environment.

        Args:
            player_id (int): The ID of the player taking the action.
            action (str): The action to be taken by the player.

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): New observations for each player.
                - rewards (Optional[Dict[int, int]]): Reward for each player.
                - truncated (bool): Whether the episode has been truncated (e.g., time limit reached).
                - terminated (bool): Whether the episode has been terminated (e.g., goal reached).
                - info (Dict[str, Any]): Additional information about the environment.
        """
        raise NotImplementedError

    @abstractmethod
    def render(self):
        """
        Renders the current state of the environment.

        This method should output a representation of the environment's state to the console or other output.
        """
        raise NotImplementedError


class Wrapper(Env):
    """
    Base class for environment wrappers.

    This class wraps an environment to allow modular transformations or extensions of its functionality.
    """

    def __init__(self, env: Env):
        """
        Initialize the Wrapper.

        Args:
            env (Env): The environment to wrap.
        """
        self.env = env
        #self.environment_name = env.environment_name
        self.state = env.state
        assert isinstance(env, Env)

    def __getattr__(self, name):
        """
        Delegate attribute access to the wrapped environment.

        This method is called only if the attribute wasn't found the usual ways.
        It allows the wrapper to pass through attributes and methods to the underlying environment.

        Args:
            name (str): The attribute name.

        Returns:
            The attribute from the wrapped environment.
        """
        return getattr(self.env, name)

    def reset(
        self, seed: Optional[int] = None
    ) -> Optional[Observations]:
        """
        Resets the environment and returns initial observations.

        Args:
            seed (Optional[int]): Seed for the random number generator to ensure reproducibility.

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): Initial observations for each player.
                - info (Optional[Dict[str, Any]]): Additional information about the environment.
        """
        return self.env.reset(seed=seed)

    def step(
        self,
        player_id: int,
        action: str,
    ) -> tuple[
        Optional[Observations],  # player-wise observations
        Optional[Rewards],  # player-wise reward
        bool,  # truncated
        bool,  # terminated
        Info,  # info
    ]:
        """
        Performs a step in the environment with the given action.

        Args:
            player_id (int): The ID of the player taking the action.
            action (str): The action to be taken.

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): Observations after the action.
                - rewards (Optional[Dict[int, int]]): Rewards for each player.
                - truncated (bool): Whether the episode is truncated.
                - terminated (bool): Whether the episode is terminated.
                - info (Optional[Dict[str, Any]]): Additional information.
        """
        return self.env.step(player_id=player_id, action=action)

    def render(self):
        """
        Renders the environment.

        This method calls the render method of the wrapped environment.
        """
        return self.env.render()


class ObservationWrapper(Wrapper):
    """
    Abstract base class for observation wrappers.

    This class is used to modify the observations returned by the environment.
    Subclasses should implement the `observation` method to define how observations are transformed.
    """

    def reset(
        self, _: Optional[int] = None
    ) -> Observations:  # observations and info
        """
        Resets the environment and applies the observation transformation.

        Args:
            seed (Optional[int]): Seed for the random number generator.

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): Transformed observations.
                - info (Dict[str, Any]): Additional information.
        """
        raise NotImplementedError
        # observations, info = self.env.reset(seed=seed)
        # return self.observation(observations), info

    def step(
        self,
        player_id: int,
        action: str,
    ) -> tuple[
        Observations,  # player-wise observations
        Rewards,  # player-wise reward
        bool,  # truncated
        bool,  # terminated
        Info,  # info
    ]:
        """
        Performs a step in the environment with the given action.

        Args:
            player_id (int): The ID of the player taking the action.
            action (str): The action to be taken.

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): Observations after the action.
                - rewards (Optional[Dict[int, int]]): Rewards for each player.
                - truncated (bool): Whether the episode is truncated.
                - terminated (bool): Whether the episode is terminated.
                - info (Optional[Dict[str, Any]]): Additional information.
        """
        observations, reward, truncated, terminated, info = self.env.step(
            player_id=player_id, action=action
        )
        return self.observation(observations), reward, truncated, terminated, info

    def observation(
        self, observations: Observations  # player-wise observations
    ) -> Optional[Dict[int, str]]:
        """Transforms the observations.

        Args:
            observations (Optional[Dict[int, str]]): The observations to transform.

        Returns:
            Optional[Dict[int, str]]: The transformed observations.
        """
        raise NotImplementedError


class RenderWrapper(Wrapper):
    """
    Abstract base class for render wrappers.

    This class is used to modify the rendering of the environment.
    Subclasses should implement the `render` method to define custom rendering behavior.
    """

    def render(self):
        """
        Renders the environment.

        Subclasses should implement this method to provide custom rendering behavior.
        """
        raise NotImplementedError


class ActionWrapper(Wrapper):
    """
    Abstract base class for action wrappers.

    This class is used to modify the actions before they are passed to the environment.
    Subclasses should implement the `action` method to define how actions are transformed.
    """

    def step(self, player_id: int, action: str) -> tuple[
        Optional[Observations],
        Optional[Rewards],
        bool,
        bool,
        Optional[Info],
    ]:
        """
        Performs a step in the environment with the transformed action.

        Args:
            player_id (int): The ID of the player taking the action.
            action (str): The action to be transformed and taken.

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): Observations after the action.
                - rewards (Optional[Dict[int, int]]): Rewards for each player.
                - truncated (bool): Whether the episode is truncated.
                - terminated (bool): Whether the episode is terminated.
                - info (Optional[Dict[str, Any]]): Additional information.
        """
        return self.env.step(player_id=player_id, action=self.action(action))

    def action(self, action: str) -> str:
        """
        Transforms the action.

        Args:
            action (str): The original action.

        Returns:
            str: The transformed action.
        """
        raise NotImplementedError



class GameMaker(ABC):
    """ TODO """
    @abstractmethod
    def __call__(self, text_input: str) -> str:
        """ TODO """
        raise NotImplementedError

class JudgeVote(ABC):
    """ TODO """
    @abstractmethod
    def __init__(self, optinos: List[str], num_judges: int):
        """ TODO """
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, transcript: str) -> Dict[str, int]:
        """ TODO """
        raise NotImplementedError
    
class GameMasterAction(ABC):
    """
    Interface for a game master that responds to player actions and maintains game continuity.
    """

    @abstractmethod
    def __init__(self, options: List[str]):
        """
        Initialize the game master with a specific answer and settings for interaction.

        Args:
            secret_answer (str): The target answer or solution the players are trying to guess.
            num_judges (int): Number of judges or agents to simulate for complex voting scenarios.
        """
        raise NotImplementedError

    @abstractmethod
    def respond_to_action(self, player_action: str) -> str:
        """
        Respond to the player's action (e.g., question in "20 Questions") based on the game's state.

        Args:
            player_action (str): The action or question posed by the player.

        Returns:
            str: The game master's response.
        """
        raise NotImplementedError