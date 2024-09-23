from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, Union

class GameInterface(ABC):
    """
    Abstract Base Class for all games within the TextArena framework.
    Defines the essential methods that any game must implement to ensure compatibility
    and consistent behavior across different games.
    """

    @abstractmethod
    def reset(self) -> Tuple[str, str, str]:
        """
        Reset the game to its initial state.

        Returns:
            Tuple[str, str, str]:
                - player_1_prompt: Initial prompt or instructions for Player 1.
                - player_2_prompt: Initial prompt or instructions for Player 2.
                - initial_observation: Initial observation or game state description.
        """
        pass

    @abstractmethod
    def get_valid_actions(self, player_id: int) -> Optional[Any]:
        """
        Retrieve the set of valid actions that a specified player can perform at the current state.

        Args:
            player_id (int): The ID of the player (e.g., 0 or 1).

        Returns:
            Optional[Any]:
                - A list of strings of valid actions.
                - None if there are no restrictions on actions.
        """
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        Provide additional information about the final game state.

        Returns:
            Dict[str, Any]: A dictionary containing relevant game state information,
                            such as the number of turns taken, scores, or other metrics.
        """
        pass

    @abstractmethod
    def step(
        self, 
        player_id: int, 
        action: str
    ) -> Tuple[
        Optional[str], 
        Optional[Dict[int, int]], 
        bool, 
        Dict[str, Any]
    ]:
        """
        Process a player's action and update the game state accordingly.

        Args:
            player_id (int): The ID of the player making the action (e.g., 0 or 1).
            action (str): The action taken by the player. 

        Returns:
            Tuple[
                Optional[str],          # observation: Description or result of the action taken.
                Optional[Dict[int, int]],# reward: Rewards for players (e.g., {0: 1, 1: -1}).
                bool,                    # done: Indicates if the game has ended.
                Dict[str, Any]           # info: Additional information about the game state or outcome.
            ]
        """
        pass

    @abstractmethod
    def _render(self) -> None:
        """
        (Optional) Render the current game state to the console or a graphical interface.
        Useful for debugging or providing visual feedback during gameplay.
        """
        pass
