import textarena as ta 

agents = {
    0: ta.agents.HumanAgent(),
    1: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),#gpt-4o"),
    # 1: ta.agents.HumanAgent(),
    # 2: ta.agents.HumanAgent(),
    # 3: ta.agents.HumanAgent(),
    # 4: ta.agents.HumanAgent(),
    # 1: ta.agents.OpenRouterAgent(model_name="openai/o3-mini"),#gpt-4o"),
    # 2: ta.agents.OpenRouterAgent(model_name="openai/o3-mini"),#gpt-4o"),
    # 3: ta.agents.OpenRouterAgent(model_name="openai/o3-mini"),#gpt-4o"),
    # 4: ta.agents.OpenRouterAgent(model_name="openai/o3-mini"),#gpt-4o")
}

# initialize the environment
env = ta.make(env_id="TicTacToe-v0")

# env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.FirstLastObservationWrapper(env=env)

# reset it
env.reset(num_players=len(agents))


# main game loop
done = False 
while not done:
  player_id, observation = env.get_observation()
  # print(f"\n\n CURRENT IPID: {env.state.current_player_id}")
  action = agents[player_id](observation)
  done, info = env.step(action=action)
rewards = env.close()
print(rewards)