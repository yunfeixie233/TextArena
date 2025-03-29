import textarena as ta
import logging
import sys
import traceback

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('client_debug.log')
    ]
)

# Log unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

logging.info("Starting online play example with debugging")

model_name = "user_123 Model"
model_description = "user_123 model description"
email = "user_123@cfar.a-star.edu.sg"

try:
    # Initialize agent
    logging.info("Initializing agent")
    agent = ta.agents.OpenRouterAgent(model_name="gpt-4o") 
    logging.info("Agent initialized")

    logging.info(f"Making online environment with ID: DontSayIt-v0")
    env = ta.make_online(
        env_id=["DontSayIt-v0"], 
        model_name=model_name,
        model_description=model_description,
        email=email,
    )
    logging.info("Online environment created")
    
    env = ta.wrappers.LLMObservationWrapper(env=env)
    logging.info("Environment wrapped with LLMObservationWrapper")

    logging.info("Resetting environment")
    observation = env.reset(num_players=1)
    logging.info(f"Environment reset complete: {observation}")

    done = False
    game_info = {}  # Initialize info dictionary
    turn_count = 0
    
    while not done:
        turn_count += 1
        logging.info(f"=== Turn {turn_count} ===")
        
        logging.info("Getting observation")
        player_id, observation = env.get_observation()
        logging.info(f"Got observation for player {player_id}")
        
        if player_id is None:
            logging.error("No valid observation received, ending game")
            break
            
        logging.info("Generating action with agent")
        try:
            action = agent(observation)
            logging.info(f"Generated action: {action}")
        except Exception as e:
            logging.error(f"Error generating action: {e}")
            logging.error(traceback.format_exc())
            break
            
        logging.info("Taking step with action")
        try:
            done, info = env.step(action=action)
            logging.info(f"Step completed. Done: {done}, Info: {info}")
            
            if info:  # Update info if we got any
                game_info.update(info)
                logging.info(f"Updated game info: {game_info}")
                
            if "error" in game_info:
                logging.error(f"Game ended with error: {game_info['error']}")
                break
        except Exception as e:
            logging.error(f"Error taking step: {e}")
            logging.error(traceback.format_exc())
            break
            
    logging.info("Game loop ended, closing environment")
    try:
        rewards = env.close()
        logging.info(f"Environment closed, rewards: {rewards}")
    except Exception as e:
        logging.error(f"Error closing environment: {e}")
        logging.error(traceback.format_exc())
        rewards = {}
        
    logging.info("Game summary:")
    logging.info(f"Game info: {game_info}")
    logging.info(f"Rewards: {rewards}")
    logging.info(f"Total turns: {turn_count}")
    
    print("Game info:", game_info)
    print("Rewards:", rewards)
    print(f"Total turns: {turn_count}")
    
except Exception as e:
    logging.error(f"Unexpected error in main script: {e}")
    logging.error(traceback.format_exc())
    print(f"Error: {e}")
    
logging.info("Script execution complete")