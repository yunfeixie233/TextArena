import textarena as ta
import time 


# initialize the agents
agents = {
    0: ta.basic_agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
    1: ta.basic_agents.OpenRouterAgent(model_name="anthropic/claude-3.5-sonnet"),
}

# Initialize the environment
env = ta.make(env_id="Chess-v0")

# Wrap the environment in the LLMObservation wrapper
env = ta.wrappers.LLMObservationWrapper(env=env)


env = ta.BrowserRenderWrapper(env, player_names={0: "White", 1: "Black"})

# # render wrapper 
# env = ta.TkinterRenderWrapper(
#     env=env,
#     player_names={
#         0: "haiku",
#         1: "sonnet"
#     },
#     enable_recording=False
# )


# Reset the environment
env.reset()

# Play the game
terminated, truncated = False, False
while not (terminated or truncated):
    # get the current player id and observation
    player_id, observation = env.get_observation()

    # print(observation)

    # get the action
    action = agents[player_id](observation)
    # print(action)
    # action = "[e2e4]"


    # step in the environment
    reward, truncated, terminated, info = env.step(action=action)

    # time.sleep(5)
    # input()

print(info)
env.close() # necessary for saving videos etc.

exit()


# clean example game loop

env.reset()
terminated, truncated = False, False 
while not (terminated or truncated):
    player_id, observation = env.get_observation()

    action = agents[player_id](observation)

    reward, truncated, terminated, info = env.step(action=action)

env.close()