import textarena as ta

# Initialize the environment
env = ta.make(env_id="SpiteAndMalice-v0")

# Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

# Wrap the environment for pretty rendering
env = ta.wrappers.PrettyRenderWrapper(env=env)

# Initialize agents
agent0 = ta.basic_agents.GPTAgent(model_name="gpt-4o")
agent1 = ta.basic_agents.GPTAgent(model_name="gpt-4o")


# Reset the environment to start a new game
observations = env.reset(seed=490)

# Game loop
done = False
while not done:

    player_id = env.state.current_player

    # Get the current agent
    agent = agent0 if player_id == 0 else agent1

    # Get the current observation for the player
    obs = observations[player_id]

    print("Observations:\n", obs)
    print("="*80)
    # Agent decides on an action based on the observation
    action = agent(obs)
    print("Action:\n", action)
    print("="*80)

    # Execute the action in the environment
    observations, rewards, truncated, terminated, info = env.step(player_id, action)

    # Check if the game has ended
    done = terminated or truncated

    # Optionally render the environment to see the current state
    env.render()

    if done:
        break


# print the game results
for player_id, agent in enumerate([agent0, agent1]):
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")