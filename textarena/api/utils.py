import os
from pathlib import Path
from typing import Optional, Tuple
import dotenv

def initialize_env():
    """
    Initialize environment variables by loading .env file.
    Returns True if successful.
    """
    env_path = Path(".env")
    if not env_path.exists():
        print(f"Warning: No .env file found at {env_path.absolute()}")
        return False
        
    # Force reload environment
    dotenv.load_dotenv(env_path, override=True)
    return True

def try_loading_token(model_name: str, debug: bool = True) -> Tuple[Optional[str], str]:
    """
    Attempt to load an API token for a given model from environment variables.
    Always ensures environment is initialized first.
    """
    # Always initialize environment first
    initialize_env()
    
    # Convert model name to env variable format
    token_key = (
        f"MODEL_TOKEN_{model_name.replace(' ', '_').replace('-', '_').replace('(', '_').replace(')', '_').upper()}"
    )
    
    if debug:
        print(f"Looking for token with key: {token_key}")
    
    # Get token from environment
    token = os.getenv(token_key)
    
    if debug:
        if token:
            print(f"Successfully loaded token for {token_key}")
        else:
            print(f"No token found for {token_key}")
            
    return token, token_key

def store_token(token_key: str, model_token: Optional[str]) -> bool:
    """
    Store a model token in the .env file and ensure it's loaded into environment.
    """
    if model_token is None:
        return False
        
    try:
        env_path = Path(".env")
        
        # Read existing content
        existing_content = ""
        if env_path.exists():
            with open(env_path, "r") as f:
                existing_content = f.read()
        
        # Update or append token
        if f"{token_key}=" in existing_content:
            lines = existing_content.splitlines()
            updated_lines = []
            for line in lines:
                if line.startswith(f"{token_key}="):
                    updated_lines.append(f'{token_key}="{model_token}"')
                else:
                    updated_lines.append(line)
            new_content = "\n".join(updated_lines)
        else:
            new_content = f'{existing_content.rstrip()}\n{token_key}="{model_token}"'
        
        # Write to file
        with open(env_path, "w") as f:
            f.write(new_content)
            
        # Immediately reload environment
        initialize_env()
        
        return True
        
    except Exception as e:
        print(f"Error storing token: {e}")
        return False