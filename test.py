import textarena as ta 

agents = {
    # 0: ta.agents.HumanAgent(),
    # 1: ta.agents.HumanAgent(),
    # 2: ta.agents.HumanAgent(),
    # 3: ta.agents.HumanAgent(),
    # 4: ta.agents.HumanAgent(),
    0: ta.agents.OpenRouterAgent(model_name="meta-llama/llama-3.3-70b-instruct"),
    1: ta.agents.OpenRouterAgent(model_name="meta-llama/llama-3.3-70b-instruct"),
    2: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    3: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    4: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 5: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 6: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 7: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 8: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 9: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 10: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 11: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 12: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 13: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 14: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 6: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
}

# initialize the environment
env = ta.make(env_id="SecretMafia-v0")
# env = ta.make(env_id="TruthAndDeception-v0")

env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.SimpleRenderWrapper(env=env, render_mode="board")
# env = ta.wrappers.FirstLastObservationWrapper(env=env)
# env = ta.wrappers.ActionFormattingWrapper(env=env)

# reset it
env.reset(num_players=len(agents))


# main game loop
done = False 
while not done:
  player_id, observation = env.get_observation()
  # print("PLAYER  ", player_id)
  action = agents[player_id](observation)
  # print(action)
  done, info = env.step(action=action)
rewards = env.close()
print(rewards)