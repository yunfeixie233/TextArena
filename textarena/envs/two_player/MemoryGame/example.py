import textarena as ta

# Initialize the environment
env = ta.make(env_id="MemoryGame-v0-easy")

# Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

# Wrap the environment for pretty rendering
env = ta.wrappers.PrettyRenderWrapper(env=env)

# initalize agents
agents = {
    0: ta.basic_agents.OpenRouter(model_name="gpt-4o"),
    1: ta.basic_agents.OpenRouter(model_name="gpt-4o-mini")
    }

# reset the environment to start a new game
observations = env.reset(seed=490)

# Game loop
done = False
while not done:

    # Get the current player
    current_player_id = env.state.get("current_player")

    # Get the current observation for the player
    obs = observations[current_player_id]

    # Agent decides on an action based on the observation
    action = agents[current_player_id](obs)

    # Execute the action in the environment
    observations, rewards, truncated, terminated, info = env.step(current_player_id, action)

    # Check if the game has ended
    done = terminated or truncated

    # Optionally render the environment to see the current state
    env.render()

    if done:
        break

# Finally, print the game results
for player_id, agent in agents.items():
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")