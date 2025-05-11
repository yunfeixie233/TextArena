import textarena as ta 

agents = {
    0: ta.agents.HumanAgent(),
    # 1: ta.agents.HumanAgent(),
    # 1: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 0: ta.agents.OpenRouterAgent(model_name="gpt-o4-mini-high"),
}

# initialize the environment
env = ta.make(env_id="WordLadder-v0")
env = ta.wrappers.ActionFormattingWrapper(env=env)

# env = ta.wrappers.SimpleRenderWrapper(env=env, render_mode="board")


env.reset(num_players=len(agents), seed=489)

# main game loop
done = False 
while not done:
  player_id, observation = env.get_observation()
  action = agents[player_id](observation)
  done, info = env.step(action=action)
rewards = env.close()
print(rewards)
print(info)