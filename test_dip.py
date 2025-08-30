""" A minimal script showing how to run textarena locally """
import os
import wandb

# Set API keys
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["WANDB_API_KEY"] = "0ff1feaaaaf719c209f24fec37d878aee51b04fb"

import textarena as ta

# Initialize wandb
wandb.init(project="textarena") 


# Initialize agents
agents = {
    0: ta.agents.OpenRouterAgent(model_name="google/gemini-2.5-flash"),
    1: ta.agents.OpenRouterAgent(model_name="google/gemini-2.5-flash"),
    2: ta.agents.OpenRouterAgent(model_name="google/gemini-2.5-flash"),
}

# Initialize the environment
# env = ta.make(env_id="UltimatumGame-v0")
env = ta.make(env_id="Diplomacy-v0-updated")
# wrap it for additional visualizations
env = ta.wrappers.SimpleRenderWrapper(env=env) 

env.reset(num_players=len(agents))

done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, step_info = env.step(action=action)

rewards, game_info = env.close()

# Log game data to wandb
print("Logging game data to wandb...")

# Get game histories
conversation_history = env.get_conversation_history()
order_history = env.get_order_history()
game_state_history = env.get_game_state_history()

# Log to wandb
wandb.log({
    "conversation_history": conversation_history,
    "order_history": order_history,
    "game_state_history": game_state_history,
    "rewards": rewards,
    "game_info": game_info
})

# Finish wandb run
wandb.finish()

print("Game data logged successfully to wandb!")