import textarena as ta 

agents = {
    # 0: ta.agents.HumanAgent(),
    1: ta.agents.OpenRouterAgent(model_name="meta-llama/llama-3.3-70b-instruct"),
    2: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    3: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    4: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
}

# initialize the environment
env = ta.make(env_id="SecretMafia-v0")

env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.SimpleRenderWrapper(env=env, render_mode="board")

# reset it
env.reset(num_players=len(agents))

# main game loop
done = False 
while not done:
  player_id, observation = env.get_observation()
  action = agents[player_id](observation)
  done, info = env.step(action=action)
rewards = env.close()
print(rewards)