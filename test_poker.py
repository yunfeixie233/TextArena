import textarena as ta
import time 


# initialize the agents
agents = {
    0: ta.basic_agents.OpenRouterAgent(model_name="GPT-4o"),
    1: ta.basic_agents.OpenRouterAgent(model_name="anthropic/claude-3.5-sonnet"),
}

# Initialize the environment
env = ta.make(env_id="Poker-v0")

# Wrap the environment in the LLMObservation wrapper
env = ta.wrappers.LLMObservationWrapper(env=env)




# render wrapper 
env = ta.TkinterRenderWrapper(
    env=env,
    player_names={
        0: "GPT-4o",
        1: "anthropic/claude-3.5-sonnet"
    },
    enable_recording=False
)


# Reset the environment
observations = env.reset()

# Play the game
terminated, truncated = False, False
while not (terminated or truncated):
    # get the current player id 
    current_player_id = env.get_current_player_id()

    # get the action
    action = agents[current_player_id](
        observations[current_player_id]
    )

    # step in the environment
    observations, reward, truncated, terminated, info = env.step(
        player_id=current_player_id,
        action=action
    )

    # time.sleep(5)
    input()

print(info)
env.close() # necessary for saving videos etc.