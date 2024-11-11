import textarena as ta 
from textarena.api.online_env import OnlineEnv
import time 
from typing import Optional

import textarena as ta
from textarena.api.online_env import OnlineEnv
import time
from typing import Optional, Tuple

def make_online(
    env_id: str, 
    model_name: str, 
    model_token: str,
    queue_time_limit: Optional[float] = None
) -> Tuple[OnlineEnv, int]:
    """
    Join the matchmaking queue and wait until a match is found.

    Args:
        env_id (str): Environment ID to join.
        model_name (str): Name of the model.
        model_token (str): Authentication token for the model.
        queue_time_limit (Optional[float], optional): Max time to wait in queue. Defaults to 300.

    Returns:
        Tuple[OnlineEnv, int]: Initialized online environment and player ID.
    """
    # Join the matchmaking queue
    ta.api.join_matchmaking(
        env_id=env_id,
        model_name=model_name,
        model_token=model_token,
        queue_time_limit=queue_time_limit
    )

    print(f"Join the matchmaking queue ")

    # Continuously check matchmaking status until a match is found
    while True:
        current_matchmaking_status = ta.api.check_matchmaking_status(
            env_id=env_id,
            model_name=model_name,
            model_token=model_token
        )
        
        status = current_matchmaking_status.get("status")
        if status == "Searching":
            queue_time = current_matchmaking_status.get("queue_time", 0)
            print(f"Waiting for match to be found. Current time in queue: {queue_time} seconds")
        elif status == "Match found":
            game_id = current_matchmaking_status["game_id"]
            player_id = current_matchmaking_status["player_id"]
            # Initialize and return the online environment
            online_env = OnlineEnv(
                env_id=env_id,
                model_name=model_name,
                model_token=model_token,
                game_id=game_id,
                player_id=player_id
            )
            return online_env, player_id
        else:
            # Handle unexpected statuses
            raise Exception(f"Unexpected matchmaking status: {status}")
        
        time.sleep(5)  # Wait before the next status check


# def make_online(
#     env_id: str, 
#     model_name: str, 
#     model_token: str,
#     queue_time_limit: Optional[float]=None
# ) -> OnlineEnv:
#     # join the matchmaking queue 
#     ta.api.join_matchmaking(
#         env_id=env_id,
#         model_name=model_name,
#         model_token=model_token,
#         queue_time_limit=queue_time_limit
#     )

#     # check until matched
#     while True:
#         current_matchmaking_status = check_matchmaking_status(
#             env_id=env_id,
#             model_name=model_name,
#             model_token=model_token,
#         )
#         if current_matchmaking_status["status"] == "Searching":
#             print(f"Waiting for match to be found. Current time in queue: {}")
#         elif current_matchmaking_status["status"] == "Match found":
#             game_id = current_matchmaking_status["game_id"]
#             player_id = current_matchmaking_status["player_id"]
#             return OnlineEnv(
#                 env_id=env_id,
#                 model_name=model_name,
#                 model_token=model_token,
#                 game_id=game_id,
#                 player_id=player_id
#             ), player_id
#         else:
#             # raise exception
#             pass 

