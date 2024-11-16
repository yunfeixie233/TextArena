import asyncio
import requests
import websockets
import json

BASE_URL = "https://textarena.ngrok.io" #"http://127.0.0.1:8000"

def wrapped_request(url, data, request_type="get"):
    """ TODO """
    try:
        if request_type == "get":
            response = requests.get(url, params=data, timeout=10)
        elif request_type == "post":
            response = requests.post(url, json=data, timeout=10)
            print(response)
        else:
            raise Exception(f"Unexpected request type: {request_type}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        # Extract the error detail message from FastAPI
        if err.response is not None and err.response.status_code >= 400:
            detail = err.response.json().get("detail", "An error occurred.")
            print(f"Error {err.response.status_code}: {detail}")
        else:
            print("An unexpected error occurred.")
        raise

# def wrapped_request(url, data, request_type="get"):
#     """
#     Sends a request to the specified URL with retry logic.

#     Args:
#         url (str): The endpoint URL.
#         data (dict): The data to send in the request.
#         request_type (str): The type of request ('get' or 'post').

#     Returns:
#         dict: The JSON response from the server.

#     Raises:
#         Exception: If the request fails or times out twice.
#     """
#     MAX_RETRIES = 1
#     TIMEOUT = 10  # seconds

#     for attempt in range(MAX_RETRIES + 1):
#         try:
#             print(f"Attempt {attempt + 1}: Sending {request_type.upper()} request to {url} with data: {data}")
#             if request_type == "get":
#                 response = requests.get(url, params=data, timeout=TIMEOUT)
#             elif request_type == "post":
#                 response = requests.post(url, json=data, timeout=TIMEOUT)
#             else:
#                 raise Exception(f"Unexpected request type: {request_type}")

#             response.raise_for_status()  # Raise an error for HTTP codes >= 400
#             print(f"Response received: {response.json()}")
#             return response.json()
#         except requests.exceptions.HTTPError as err:
#             if err.response is not None and err.response.status_code == 400:
#                 error_detail = err.response.json().get("detail", "Unknown error detail.")
#                 print(f"400 Error Detail: {error_detail}")
#             raise
#         except requests.exceptions.Timeout:
#             print(f"Request timed out. Retrying... ({attempt + 1}/{MAX_RETRIES + 1})")
#         except requests.exceptions.RequestException as e:
#             print(f"Request failed: {e}")
#             if attempt == MAX_RETRIES:
#                 raise Exception(f"Request to {url} failed after {MAX_RETRIES + 1} attempts.") from e

#     raise Exception(f"Request to {url} failed after {MAX_RETRIES + 1} attempts due to timeout or connection issues.")


# import uuid

# def wrapped_request(url, data, request_type="get"):
#     """
#     Sends a request to the specified URL with retry logic.
#     """
#     MAX_RETRIES = 1
#     TIMEOUT = 10  # seconds

#     # Add a unique request ID if not already present
#     if "request_id" not in data:
#         data["request_id"] = str(uuid.uuid4())

#     for attempt in range(MAX_RETRIES + 1):
#         try:
#             print(f"Attempt {attempt + 1}: Sending {request_type.upper()} request to {url} with data: {data}")
#             if request_type == "get":
#                 response = requests.get(url, params=data, timeout=TIMEOUT)
#             elif request_type == "post":
#                 response = requests.post(url, json=data, timeout=TIMEOUT)
#             else:
#                 raise Exception(f"Unexpected request type: {request_type}")

#             response.raise_for_status()
#             print(f"Response received: {response.json()}")
#             return response.json()
#         except requests.exceptions.RequestException as e:
#             if attempt == MAX_RETRIES:
#                 raise Exception(f"Request to {url} failed after {MAX_RETRIES + 1} attempts.") from e



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
    return response["model_token"]

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
    response = wrapped_request(
        url=url, 
        data=data,
        request_type="post"
    )
    return response["message"]

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