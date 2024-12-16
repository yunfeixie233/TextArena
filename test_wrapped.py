import textarena as ta

# initialize the agents
agents = {
    0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
    1: ta.agents.wrappers.ThoughtAgentWrapper(
        ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")
    ),
}

# Initialize the environment
env = ta.make(env_id="UltimateTicTacToe-v0")

# Wrap the environment in the LLMObservation wrapper
env = ta.wrappers.LLMObservationWrapper(env=env)


# env = ta.wrappers.PrettyRenderWrapper(
#     env=env, 
#     player_names={0: "haiku", 1: "sonnet"},
#     # record_video=True,
#     # video_path="chess_game.mp4"
# )

env = ta.wrappers.SimpleRenderWrapper(
    env=env,
    player_names={0: "haiku", 1: "sonnet"}
)


env.reset()
done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, info = env.step(action=action)
rewards = env.close()

