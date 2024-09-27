import importlib
import os
from typing import Any
import gymnasium as gym

def make(env_name: str, render_mode: str = None, **kwargs: Any) -> gym.Env:
    """
    Creates and returns an instance of the specified environment.

    Args:
        env_name (str): The name of the environment to create (e.g., "codenames", "hangman").
        render_mode (str, optional): The rendering mode. Defaults to None.
        **kwargs: Additional keyword arguments for the environment.

    Returns:
        gym.Env: An instance of the specified environment.

    Raises:
        ValueError: If the environment name is not recognized or cannot be instantiated.
    """
    env_name_lower = env_name.lower()
    class_name = f"{env_name.capitalize()}Env"

    # Define the path based on the environment name
    # Assuming the structure: textarena/<env_name>/<env_name>_env.py
    package_path = f"textarena.{env_name_lower}.{env_name_lower}_env"

    try:
        # Dynamically import the environment module
        env_module = importlib.import_module(package_path)
    except ImportError as e:
        raise ValueError(f"Environment module '{env_name_lower}_env.py' not found in 'textarena/{env_name_lower}/'.") from e

    try:
        # Retrieve the environment class from the module
        env_class = getattr(env_module, class_name)
    except AttributeError as e:
        raise ValueError(f"Environment class '{class_name}' not found in module '{env_name_lower}_env.py'.") from e

    try:
        # Instantiate and return the environment
        return env_class(**kwargs)
    except Exception as e:
        raise ValueError(f"Failed to instantiate environment '{class_name}': {str(e)}") from e
