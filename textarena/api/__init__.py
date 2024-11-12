from textarena.api.api_client import (
    register_online_model,       # Function to register a new model
    join_matchmaking,            # Function to join matchmaking
    check_matchmaking_status,    # Function to check matchmaking status
    check_turn,                  # Function to check turn status
    submit_step,                 # Function to submit a step/action
    get_results,                 # Function to get the game results
)

from textarena.api.game_manager import make_online  # Function to manage online game setup

__all__ = [
    "register_online_model",
    "join_matchmaking",
    "check_matchmaking_status",
    "check_turn",
    "submit_step",
    "make_online",
    "get_results"
]