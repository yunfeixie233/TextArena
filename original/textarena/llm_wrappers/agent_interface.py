from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, List

class AgentInterface(ABC):
    """
    Abstract Base Class for all agent wrappers within the TextArena framework.
    Defines the essential methods that any agent must implement to ensure compatibility
    and consistent behavior across different agent implementations.
    """

    @abstractmethod
    def __init__(
        self, 
        unique_identifier: str, 
        verbose: bool = False
    ):
        """
        Initialize the agent with a unique identifier and verbosity setting.

        Args:
            unique_identifier (str): A unique identifier for the agent.
            verbose (bool, optional): Flag to enable or disable verbose output. Defaults to False.
        """
        pass

    @abstractmethod
    def reset(self, game_prompt: str) -> None:
        """
        Reset the agent with a new main prompt.

        Args:
            game_prompt (str): The main prompt or instructions for the player.
        """
        pass

    @abstractmethod
    def get_action(
        self, 
        observation: str, 
        valid_actions: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        Generate an action based on the current observation and valid actions.

        Args:
            observation (str): The current state or observation of the game specific to the player.
            valid_actions (List[str], optional): A list of valid actions.

        Returns:
            Tuple[str, str]: A tuple containing the generated action and the prompt used to generate it.
        """
        pass
