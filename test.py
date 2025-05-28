""" A minimal script showing how to run textarena locally """

import textarena as ta 

agents = {
    0: ta.agents.HumanAgent(),
    # 1: ta.agents.HumanAgent(),
    1: ta.agents.OpenRouterAgent(model_name="gpt-4o-mini"),
    # 1: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 2: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 3: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 4: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 5: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 6: ta.agents.OpenRouterAgent(model_name="gpt-4o"),
    # 0: ta.agents.OpenRouterAgent(model_name="gpt-o4-mini-high"),
}

# initialize the environment

env = ta.make(env_id="TicTacToe-v0-raw")
env = ta.wrappers.GameMessagesAndCurrentBoardWithInvalidMovesObservationWrapper(env=env)
# env = ta.make(env_id="Poker-v0-train-small")
# env = ta.make(env_id="Snake-v0-train-small")
# env = ta.make(env_id="Dataset-AIME24-v0")
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
  action = agents[player_id](observation)
  done, info = env.step(action=action)
rewards = env.close()
print(rewards)
print(info)