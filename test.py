""" A minimal script showing how to run textarena locally """

import textarena as ta 

agents = {
    0: ta.agents.HumanAgent(),
    # 1: ta.agents.HumanAgent(),
    # 2: ta.agents.HumanAgent(),
    # 3: ta.agents.HumanAgent(),
    # 1: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 1: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 2: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 3: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 4: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 5: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 6: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 0: ta.agents.OpenRouterAgent(model_name="gpt-o4-mini-high"),
}

# initialize the environment
# env = ta.make(env_id="Poker-v0-train-small")
# env = ta.make(env_id="Chess-v0-train")
# env = ta.make(env_id="Poker-v0-train")
# env = ta.make(env_id="ConnectFour-v0-train")
# env = ta.make(env_id="TicTacToe-v0-train")
env = ta.make(env_id="Sokoban-v0-train")
# env = ta.wrappers.GameMessagesAndCurrentBoardObservationWrapper(env=env)
# env = ta.wrappers.GameBoardObservationWrapper(env=env)
# env = ta.wrappers.LLMObservationWrapper(env=env)
# env = ta.wrappers.ActionFormattingWrapper(env=env)
# env = ta.wrappers.SimpleRenderWrapper(env)


# env = ta.wrappers.SimpleRenderWrapper(env=env) #, render_mode="standard")
env.reset(num_players=len(agents))
# env.state.error_allowance=0
# main game loop
done = False 
while not done:
  player_id, observation = env.get_observation()
  action = agents[player_id](observation+"\nMake sure to return your final answer within \\boxed{}")

  print(action)
  done, info = env.step(action=action)
  print(info)
  print("\n\n")
rewards = env.close()
print(rewards)
print(info)