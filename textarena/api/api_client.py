import requests, json, sys
from textarena.api.utils import try_loading_token, store_token

BASE_URL = "https://api.textarena.ai" #"http://127.0.0.1:8000"

def wrapped_request(url, data, request_type="get"):
    """ Wrapper for HTTP requests with simplified error messages. """
    if request_type == "get":
        response = requests.get(url, params=data, timeout=10)
    elif request_type == "post":
        response = requests.post(url, json=data, timeout=10)
    else:
        raise ValueError(f"Unexpected request type: {request_type}")

    if response.status_code != 200:
        try:
            # Extract custom reason
            error_reason = json.loads(response.content).get("detail", "No details provided")
        except (json.JSONDecodeError, KeyError):
            error_reason = response.text
        # Return the clean error message without traceback
        print(f"\nError: {response.status_code}. Reason: {error_reason}. Exiting.")
        sys.exit(1)

    return response.json()

def register_online_model(model_name, model_description, email):
    """
    Register a new model with the server.

    Args:
        model_name (str): Unique name of the model.
        model_description (str): Description of the model.
        email (str): Contact email for the model.

    Returns:
        str: The model token provided by the server.
    """
    # check if the model already has a local token
    model_token, token_key = try_loading_token(model_name=model_name)
    if model_token is None:
        print(f"No model_token found in .env. Expected key: {token_key}")
        # try registering
        url = f"{BASE_URL}/register_model"
        data = {
            "model_name": model_name,
            "description": model_description,
            "email": email
        }
        response = wrapped_request(
            url=url, 
            data=data,
            request_type="post"
        )
        # store token
        store_token(token_key=token_key, model_token=response["model_token"])
        return response["model_token"]
    return model_token

def join_matchmaking(env_id, model_name, model_token, queue_time_limit=300):
    """
    Join the matchmaking queue for a specific environment.

    Args:
        env_id (str): Environment ID to join.
        model_name (str): Name of the model.
        model_token (str): Authentication token for the model.
        queue_time_limit (float, optional): Maximum time to wait in queue. Defaults to 300.

    Returns:
        str: Confirmation message from the server.
    """
    url = f"{BASE_URL}/join_matchmaking"
    data = {
        "env_id": env_id,
        "model_name": model_name,
        "model_token": model_token,
        "queue_time_limit": queue_time_limit
    }
    # print(data)
    response = wrapped_request(
        url=url, 
        data=data,
        request_type="post"
    )
    return response["message"]

def leave_matchmaking(env_id: str, model_name: str, model_token: str):
    """
    Send a request to leave the matchmaking queue.
    
    Args:
        env_id (str): Environment ID to leave.
        model_name (str): Name of the model.
        model_token (str): Authentication token for the model.
        
    Returns:
        dict: Response from the server.
    """
    url = f"{BASE_URL}/leave_matchmaking"
    payload = {
        "env_id": env_id,
        "model_name": model_name,
        "model_token": model_token
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error leaving matchmaking: {e}")
        raise

def check_matchmaking_status(env_id, model_name, model_token):
    """
    Check the current matchmaking status for a model.

    Args:
        env_id (str): Environment ID to check.
        model_name (str): Name of the model.
        model_token (str): Authentication token for the model.

    Returns:
        dict: Current matchmaking status and related information.
    """
    url = f"{BASE_URL}/check_matchmaking_status"
    data = {
        "env_id": env_id,
        "model_name": model_name,
        "model_token": model_token
    }
    response = wrapped_request(
        url=url, 
        data=data,
        request_type="get"
    )
    return response

def check_turn(env_id, model_name, model_token, game_id, player_id):
    """
    Check if it's the model's turn in the current game.

    Args:
        env_id (str): Environment ID.
        model_name (str): Name of the model.
        model_token (str): Authentication token for the model.

    Returns:
        dict: Turn status and observations if it's the model's turn.
    """
    url = f"{BASE_URL}/check_turn"
    data = {
        "env_id": env_id,
        "model_name": model_name,
        "model_token": model_token,
        "game_id": game_id,
        "player_id": player_id
    }
    response = wrapped_request(
        url=url, 
        data=data,
        request_type="get"
    )
    return response

def submit_step(env_id, model_name, model_token, game_id, action_text):
    """
    Submit an action (step) to the server.

    Args:
        env_id (str): Environment ID.
        model_name (str): Name of the model.
        model_token (str): Authentication token for the model.
        action_text (str): The action to perform.

    Returns:
        dict: Server response after submitting the action.
    """
    url = f"{BASE_URL}/step"
    data = {
        "env_id": env_id,
        "model_name": model_name,
        "model_token": model_token,
        "game_id": game_id,
        "action_text": action_text
    }
    response = wrapped_request(
        url=url, 
        data=data,
        request_type="post"
    )
    return response


def get_results(game_id, model_name, env_id):
    """ TODO """
    url = f"{BASE_URL}/get_results"
    data = {
        "game_id": game_id,
        "model_name": model_name,
        "env_id": env_id
    }
    response = wrapped_request(
        url=url, 
        data=data,
        request_type="post"    
    )
    return response