from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Union

class Env(ABC):
    """
    Abstract base class for text-based game environments.

    This class outlines the interface for the environment, including methods for resetting the environment,
    stepping through the environment (taking actions), and rendering the environment state.
    """
    @abstractmethod
    def reset(
        self,
        observations: Optional[Dict[int, str]] = None,
        seed: Optional[int] = None
    ):
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
    ) -> Tuple[
        Optional[Dict[int, str]], # player-wise observations
        Optional[Dict[int, int]], # player-wise reward
        bool, # truncated
        bool, # terminated
        Dict[str, Any], # info
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
        self,
        seed: Optional[int] = None
    ) -> Tuple[Optional[Dict[int, str]], Optional[Dict[str, Any]]]:
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
    ) -> Tuple[
        Optional[Dict[int, str]], # player-wise observations
        Optional[Dict[int, int]], # player-wise reward
        bool, # truncated
        bool, # terminated
        Dict[str, Any], # info
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

    def __init__(self, env:Env):
        """
        Initialize the ObservationWrapper.

        Args:
            env (Env): The environment to wrap.
        """
        super().__init__(env)

    def reset(
        self, 
        seed:Optional[int]=None
    ) -> Tuple[Optional[Dict[int, str]], Dict[str, Any]]: # observations and info
        """
        Resets the environment and applies the observation transformation.

        Args:
            seed (Optional[int]): Seed for the random number generator.

        Returns:
            Tuple containing:
                - observations (Optional[Dict[int, str]]): Transformed observations.
                - info (Dict[str, Any]): Additional information.
        """
        observations, info = self.env.reset(seed=seed)
        return self.observation(observations), info

    def observation(
        self, observations: Optional[Dict[int, str]]  # player-wise observations
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
    def __init__(self, env: Env):
        """
        Initialize the RenderWrapper.

        Args:
            env (Env): The environment to wrap.
        """
        super().__init__(env)

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
    def __init__(self, env:Env):
        """
        Initialize the ActionWrapper.

        Args:
            env (Env): The environment to wrap.
        """
        super().__init__(env)

    def step(
        self, player_id:int, action:str
    ) -> Tuple[
        Optional[Dict[int, str]], 
        Optional[Dict[int, int]], 
        bool, 
        bool, 
        Optional[Dict[str, Any]]
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
        return self.env.step(
            player_id=player_id,
            action=self.action(action)
        )

    def action(self, action:str) -> str:
        """
        Transforms the action.

        Args:
            action (str): The original action.

        Returns:
            str: The transformed action.
        """
        raise NotImplementedError