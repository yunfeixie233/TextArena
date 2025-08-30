""" A minimal script showing how to run textarena locally """
import os
os.environ["OPENROUTER_API_KEY"] = "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"
import textarena as ta 


# Initialize agents
agents = {
    0: ta.agents.OpenRouterAgent(model_name="google/gemini-2.5-flash"),
    1: ta.agents.OpenRouterAgent(model_name="google/gemini-2.5-flash"),
}

# Initialize the environment
env = ta.make(env_id="UltimatumGame-v0")
# env = ta.make(env_id="SimpleNegotiation-v0")
# wrap it for additional visualizations
env = ta.wrappers.SimpleRenderWrapper(env=env) 

env.reset(num_players=len(agents))

done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, step_info = env.step(action=action)

rewards, game_info = env.close()