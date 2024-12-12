import os
from pathlib import Path
from typing import Optional
import dotenv
import textarena as ta

def try_loading_token(model_name):
    """ TODO """
    # Convert model name to env variable format
    token_key = f"MODEL_TOKEN_{model_name.replace(' ', '_').replace('-', '_').replace('(', '_').replace(')', '_').upper()}"
    
    # Check for existing token
    token = os.getenv(token_key)

    return token, token_key 


def store_token(token_key, model_token):
    """ TODO """
    
    if model_token is not None:
        # create file if necessary
        with open(".env", "a") as f:
            f.write(f'\n{token_key}="{model_token}"')

        # Reload environment variables 
        dotenv.load_dotenv(".env", override=True)

