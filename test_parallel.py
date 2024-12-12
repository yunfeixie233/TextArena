import textarena as ta
from multiprocessing import Pool
import functools
import logging
from typing import Dict, List, Optional
import requests
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_model_game(env_id: str, model_info: Dict) -> Dict:
    """
    Run a single model in the specified environment with error handling.
    
    Args:
        env_id (str): The ID of the environment to run
        model_info (dict): Dictionary containing model name and description
    
    Returns:
        dict: Results dictionary containing model name and game outcome
    """
    try:
        model_name = model_info['name']
        model_desc = model_info['description']
        email = f"Guertlerlo+{model_name.replace(' ', '_')}@cfar.a-star.edu.sg"

        logger.info(f"Starting game for model: {model_name}")

        # Register the model
        try:
            model_token = ta.register_online_model(
                model_name=model_name,
                model_description=model_desc,
                email=email
            )
        except Exception as e:
            logger.error(f"Failed to register model {model_name}: {str(e)}")
            return {
                'model_name': model_name,
                'status': 'failed',
                'error': f"Registration failed: {str(e)}"
            }

        # Build agent
        agent = ta.basic_agents.OpenRouterAgent(model_name=model_info['base_model'])

        # Make the online environment
        env = ta.make_online(
            env_id=env_id,
            model_name=model_name,
            model_token=model_token,
        )

        # Wrap for easy LLM use
        env = ta.LLMObservationWrapper(env=env)

        # Reset with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                observations = env.reset()
                break
            except (requests.exceptions.JSONDecodeError, requests.exceptions.RequestException) as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Reset attempt {attempt + 1} failed for {model_name}, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff

        truncated, terminated = False, False
        turn_count = 0
        max_turns = 50  # Safeguard against infinite loops

        while not (truncated or terminated) and turn_count < max_turns:
            try:
                # Get the current player id
                player_id = env.get_current_player_id()

                # Get agent action
                action = agent(observations[player_id])

                # Step
                observations, _, truncated, terminated, info = env.step(player_id, action)
                turn_count += 1

            except Exception as e:
                logger.error(f"Error during game step for {model_name}: {str(e)}")
                truncated = True
                break

        # Get results and close
        try:
            results = env.get_results() if hasattr(env, 'get_results') else None
            env.close()
        except Exception as e:
            logger.error(f"Error getting results for {model_name}: {str(e)}")
            results = None

        return {
            'model_name': model_name,
            'status': 'completed',
            'results': results,
            'turns': turn_count
        }

    except Exception as e:
        logger.error(f"Unexpected error for {model_info['name']}: {str(e)}")
        return {
            'model_name': model_info['name'],
            'status': 'failed',
            'error': str(e)
        }

def run_parallel_games(env_id: str, model_list: List[Dict], num_rounds: int = 25) -> List[Dict]:
    """
    Run multiple models in parallel for the specified environment with error handling.
    
    Args:
        env_id (str): The ID of the environment to run
        model_list (list): List of dictionaries containing model configurations
        num_rounds (int): Number of rounds to run
    
    Returns:
        list: List of results dictionaries for each model
    """
    all_results = []
    
    for round_num in range(num_rounds):
        logger.info(f"Starting round {round_num + 1}/{num_rounds}")
        
        try:
            # Create partial function with fixed env_id
            run_game = functools.partial(run_model_game, env_id)
            
            # Run games in parallel with error handling
            with Pool() as pool:
                round_results = pool.map(run_game, model_list)
                
            all_results.extend(round_results)
            
            # Log round summary
            successful = sum(1 for r in round_results if r['status'] == 'completed')
            logger.info(f"Round {round_num + 1} completed: {successful}/{len(model_list)} models successful")
            
        except Exception as e:
            logger.error(f"Error in round {round_num + 1}: {str(e)}")
            continue
            
    return all_results

# Example usage
if __name__ == "__main__":
    # Specify the environment ID
    ENV_ID = "ConnectFour-v0"
    
    # Define the models to test
    MODELS = [
        {
            'name': "GPT-4o-mini test version",
            'description': "OpenAI's GPT-4o model.",
            'base_model': "GPT-4o-mini"
        },
        {
            'name': "Gemma",
            'description': "Google Gemma.",
            'base_model': "google/gemma-2-9b-it"
        },
        {
            'name': "Mistral 7B",
            'description': "Mistral 7B model.",
            'base_model': "mistralai/mistral-7b-instruct-v0.3"
        },
        {
            'name': "DeepSeek V2.5",
            'description': "DeepSeek model.",
            'base_model': "deepseek/deepseek-chat"
        }
    ]
    
    # Run all models in parallel
    results = run_parallel_games(ENV_ID, MODELS, num_rounds=20)  # Reduced rounds for testing
    
    # Print results summary
    print("\nResults Summary:")
    print("-" * 50)
    for result in results:
        status = result['status']
        model_name = result['model_name']
        if status == 'completed':
            print(f"{model_name}: Completed successfully")
            if result['results']:
                print(f"Results: {result['results']}")
            print(f"Turns: {result['turns']}")
        else:
            print(f"{model_name}: Failed - {result.get('error', 'Unknown error')}")
        print("-" * 50)