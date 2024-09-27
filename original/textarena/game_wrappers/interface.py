from abc import ABC, abstractmethod
from typing import Any, Dict


class TwoPlayerGameInterface(ABC):
    """
    Abstract Base Class for two-player game wrappers within the TextArena framework.
    Defines the essential methods that any two-player game wrapper must implement to ensure compatibility
    and consistent behavior across different implementations.
    """

    @abstractmethod
    def __init__(
        self, 
        game_name: str,
        agent_1: Any,
        agent_2: Any,
        num_rounds: int = 1,
        verbose: bool = True,
        game_kwargs: Dict[str, Any] = {}
    ):
        """
        Initialize the two-player game wrapper with the specified game and agents.

        Args:
            game_name (str): The name of the game to be played.
            agent_1 (Any): The first agent participating in the game.
            agent_2 (Any): The second agent participating in the game.
            num_rounds (int, optional): The number of game rounds to play. Defaults to 1.
            verbose (bool, optional): Flag to enable or disable progress tracking. Defaults to True.
            game_kwargs (Dict[str, Any], optional): Additional keyword arguments for game initialization.
        """
        pass

    @abstractmethod
    def play_game(self) -> Dict[str, Any]:
        """
        Play the specified number of game rounds between the two agents.

        Returns:
            Dict[str, Any]: A dictionary containing logs and scores for each agent,
                            as well as overall game statistics like the number of turns and reasons for completion.
        """
        pass
