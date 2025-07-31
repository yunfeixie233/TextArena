""" A minimal script showing how to run textarena locally """

import textarena as ta 

model_name="moonshotai/kimi-k2"
# model_name="deepseek/deepseek-r1-0528"
agents = {
    # 0: ta.agents.HumanAgent(),
    # 1: ta.agents.HumanAgent(),
    # 2: ta.agents.HumanAgent(),
    # 3: ta.agents.HumanAgent(),
    0: ta.agents.OpenRouterAgent(model_name=model_name),
    1: ta.agents.OpenRouterAgent(model_name=model_name),
    2: ta.agents.OpenRouterAgent(model_name=model_name),
    3: ta.agents.OpenRouterAgent(model_name=model_name),
}

# initialize the environment
env = ta.make(env_id="SettlersOfCatan-v0-train")
env = ta.wrappers.SimpleRenderWrapper(env=env, render_mode="multi")
env.reset(num_players=len(agents))

# main game loop
done = False 
while not done:
  player_id, observation = env.get_observation()
  action = agents[player_id](observation)
  done, step_info = env.step(action=action)
rewards, game_info = env.close()
print(rewards)
print(game_info)
