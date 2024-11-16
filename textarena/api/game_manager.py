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
    result = ta.api.join_matchmaking(
        env_id=env_id,
        model_name=model_name,
        model_token=model_token,
        queue_time_limit=queue_time_limit
    )
    print(result)

    time.sleep(10)
    from datetime import datetime
    print(f"Joined the matchmaking queue ", datetime.now().strftime("%H:%M:%S"))

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
            queue_time_limit = current_matchmaking_status.get("queue_time_limit", 300)
            print(f"Waiting in matchmaking queue for {env_id}...({queue_time:.0f}s/{queue_time_limit:.0f}s)", end="\r")
        elif status == "Match found":
            game_id = current_matchmaking_status["game_id"]
            player_id = current_matchmaking_status["player_id"]
            opponent_names = current_matchmaking_status["opponent_name"]
            num_players = current_matchmaking_status["num_players"]

            # Initialize and return the online environment
            online_env = OnlineEnv(
                env_id=env_id,
                model_name=model_name,
                model_token=model_token,
                game_id=game_id,
                player_id=player_id,
                num_players=num_players
            )

            print("\n")
            print("="*30, "[MATCH FOUND]", "="*30)
            print(f"Environment:\t {env_id}")
            print(f"Opponent(s):\t {opponent_names}")
            print(f"You are playing as Player {player_id}\n\n\n")
            
            return online_env, player_id
        else:
            # Handle unexpected statuses
            raise Exception(f"Unexpected matchmaking status: {status}")
        
        time.sleep(5)  # Wait before the next status check

