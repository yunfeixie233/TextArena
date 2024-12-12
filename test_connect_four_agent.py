import textarena as ta
import time 

# initialize the agents
agents = {
    0: ta.ActorCriticAgentWrapper(ta.OpenRouterAgent(model_name="GPT-4o-mini")),
    1: ta.ChainAgentWrapper(
        [
            # ta.InterpreterAgentWrapper(ta.OpenRouterAgent(model_name="GPT-4o-mini")),
            ta.ThoughtAgentWrapper(agent=ta.OpenRouterAgent(model_name="GPT-4o-mini"), debugging=True),
        ]
    )
}

# Initialize the environment
env = ta.make(env_id="ConnectFour-v0")

# Wrap the environment in the LLMObservation wrapper
env = ta.wrappers.LLMObservationWrapper(env=env)




# Reset the environment
observations = env.reset()

# render wrapper 
env = ta.TkinterRenderWrapper(
    env=env,
    player_names={
        0: "GPT-4o-mini",
        1: "GPT-4o-mini (wrapped)"
    },
    enable_recording=True
)


# Play the game
terminated, truncated = False, False
while not (terminated or truncated):
    # get the current player id 
    current_player_id = env.get_current_player_id()

    # get the action
    action = agents[current_player_id](
        observations[current_player_id]
    )
    print(f"Action: {action}")

    # step in the environment
    observations, reward, truncated, terminated, info = env.step(
        player_id=current_player_id,
        action=action
    )

    # time.sleep(5)
    # input()

print(info)
# input()
# input()
env.close() # necessary for saving videos etc.