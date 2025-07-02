""" A minimal script showing how to run textarena locally """

import textarena as ta 


agents = {
    0: ta.agents.HumanAgent(),
    # 1: ta.agents.HumanAgent(),
    # 2: ta.agents.HumanAgent(),
    # 3: ta.agents.HumanAgent(),
    # 4: ta.agents.HumanAgent(),
    # 5: ta.agents.HumanAgent(),
    1: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-001"),
    # 2: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-001"),
    # 3: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-001"),
    # 4: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-001"),
    # 5: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-001"),
    # 2: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-lite-001"),
    # 3: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-lite-001"),
    # 1: ta.agents.HumanAgent(),
    # 0: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-001"),
    # 0: ta.agents.OpenRouterAgent(model_name="google/gemini-2.0-flash-lite-001"),
}

# initialize the environment
env = ta.make(env_id="IteratedPrisonersDilemma-v0-train")

# env = ta.wrappers.SimpleRenderWrapper(env=env) #, render_mode="standard")
env.reset(num_players=len(agents))

# main game loop
done = False 
while not done:
  player_id, observation = env.get_observation()
  print("PLAYER TURN", player_id)
  action = agents[player_id](observation)
  print(observation)
  print(f"SUBMITTED ACTION BY {player_id} ", action)
  done, step_info = env.step(action=action)
rewards, game_info = env.close()
print(rewards)
print(game_info)
print(step_info)
print(env.state.turn)