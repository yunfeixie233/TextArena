import requests
import time
import warnings
from typing import Optional, Tuple, Dict, Any
import textarena as ta  # Ensure textarena is properly imported

class OnlineEnv:
    """
    Represents an online game environment for a model.

    Attributes:
        env_id (str): Environment ID.
        model_name (str): Name of the model.
        model_token (str): Authentication token for the model.
        game_id (str): ID of the current game.
        player_id (int): Player ID within the game.
    """

    def __init__(
        self,
        env_id: str,
        model_name: str,
        model_token: str,
        game_id: str,
        player_id: int,
    ):
        self.env_id = env_id 
        self.model_name = model_name 
        self.model_token = model_token 
        self.game_id = game_id 
        self.player_id = player_id 

    def _wait_until_player_turn(self) -> Dict[str, Any]:
        """
        Wait until it's the player's turn to act.

        Returns:
            Dict[str, Any]: Observations from the game environment and done status.
        """
        while True:
            turn_status = ta.api.check_turn(
                env_id=self.env_id,
                model_name=self.model_name,
                model_token=self.model_token,
            )

            status = turn_status.get("status")
            if status == "Your turn":
                observations = turn_status.get("observations")
                done = turn_status.get("done", False)
                return {"observations": observations, "done": done}
            elif status == "Not your turn":
                time.sleep(1)  # Wait before checking again
            else:
                # Handle unexpected statuses
                raise Exception(f"Unexpected turn status: {status}")

    def reset(self, seed: Optional[int] = None) -> Optional[Dict[int, Tuple[int, str]]]:
        """
        Reset the environment. No seed should be provided for online environments.

        Args:
            seed (Optional[int], optional): Seed value. Should be None. Defaults to None.

        Returns:
            Optional[Dict[int, Tuple[int, str]]]: Initial observations after reset.
        """
        if seed is not None:
            warnings.warn("No seed should be provided when using the online environment.")
            # Proceed without using the seed

        # Wait until it's the player's turn to start
        result = self._wait_until_player_turn()
        return result["observations"]

    def step(
        self,
        action: str,
    ) -> Tuple[
        Optional[Dict[int, Tuple[int, str]]],  # Observations
        Optional[Dict[int, int]],               # Rewards
        bool,                                    # Truncated
        bool,                                    # Terminated
        Optional[Dict[str, Any]]                # Info
    ]:  
        """
        Submit an action to the environment and wait for the next turn.

        Args:
            action (str): Action text to submit.

        Returns:
            Tuple[
                Optional[Dict[int, Tuple[int, str]]],
                Optional[Dict[int, int]],
                bool,
                bool,
                Optional[Dict[str, Any]]
            ]: Tuple containing observations, rewards, truncated, terminated, and info.
        """
        # Ensure the correct player is making the action
        assert self.player_id is not None, "Player ID is not set."
        
        # Submit the action to the server
        ta.api.submit_step(
            env_id=self.env_id,
            model_name=self.model_name,
            model_token=self.model_token,
            action_text=action
        )
        print("Action submitted successfully. Waiting for opponent's turn.")

        # Wait until it's the player's turn again
        result = self._wait_until_player_turn()
        observations = result["observations"]
        done = result["done"]

        # Return the observations and done flags. Rewards and info are not handled here.
        return observations, None, done, done, None




# import requests
# import time

# class OnlineEnv:
#     def __init__(
#         env_id: str,
#         model_name: str,
#         model_token: str,
#         game_id: str,
#         player_id: int,
#     ):
#         self.env_id = env_id 
#         self.model_name = model_name 
#         self.model_token = model_token 
#         self.game_id = game_id 
#         self.player_id = player_id 


#     def _wait_until_player_turn(self):
#         """ TODO """
#         while True:
#             turn_status = ta.api.check_turn(
#                 env_id=self.env_id,
#                 model_name=self.model_name,
#                 model_token=self.model_token,
#             )

#             if turn_status["status"] == "Your turn":
#                 observations = turn_status["observations"]
#                 done = trun_status["done"]
#                 return observations
#             elif turn_status["status"] == "Not your turn":
#                 time.sleep(1)

#             else:
#                 # throw error
#                 pass 


#     def reset(self, seed: Optional[int]=None) -> Optional[ta.Observations]:
#         """ TODO """
#         raise seed is None, \
#             f"No seed should be provided when using the online env"
#         # please change the raise to a warning

#         # wait until it is the players turn
#         observations, done = self._wait_until_player_turn()

#         return observations 


#     def step(
#         self,
#         player_id: int,
#         action: str,
#     ) -> Tuple[
#         Optional[ta.Observations], # Observations: Dict[int, Tuple[int, str]]
#         Optional[ta.Rewards], # Rewards: Dict[int, int]
#         bool, # Truncated
#         bool, # Terminated
#         ta.Info, # Info: Optional[Dict[str, Any]]
#     ]:  
#         # assert player_id locally
#         assert player_id == self.player_id, \
#             f""
#         # pass the action to the environment and then wait until it is the players turn
#         ta.api.submit_step(
#             env_id=self.env_id,
#             model_name=self.model_name,
#             model_token=self.model_token,
#             player_id=player_id,
#             action=action
#         )
#         print(f"Action submitted successfully. Waiting for opponents to step.")
#         observations, done = self._wait_until_player_turn()
        

#         return observations, None, done, done, None  

