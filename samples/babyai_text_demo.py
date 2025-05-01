import textarena as ta

# Initialize agents
agents = {
    0: ta.agents.HumanAgent(),
}

# Initialize environment from subset and wrap it
env = ta.make(env_id="BabyAiText-v0")
env = ta.wrappers.LLMObservationWrapper(env=env)
# Optional render wrapper
env = ta.wrappers.SimpleRenderWrapper(
    env=env,
    player_names={0: "Hosein"},
    render_mode="board"
)

env.reset(num_players=len(agents))
done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, info = env.step(action=action)
rewards = env.close()