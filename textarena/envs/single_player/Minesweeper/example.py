import textarena as ta

## initializa the environment
env = ta.make("Minesweeper-v0-easy")

## Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

## Wrap the environment for pretty rendering
env = ta.wrappers.PrettyRenderWrapper(env=env)

## initalize agents
agent0  = ta.basic_agents.OpenRouter(model_name="gpt-4o-mini")

## reset the environment to start a new game
observations = env.reset(seed=490)

## Game loop
done = False
while not done:

    # Get the current player
    player_id = env.state.current_player

    # Get the current agent
    agent = agent0

    # Get the current observation for the player
    obs = observations[player_id]

    # Agent decides on an action based on the observation
    action = agent(obs)

    # Execute the action in the environment
    observations, rewards, truncated, terminated, info = env.step(player_id, action)

    # Check if the game has ended
    done = terminated or truncated

    # Optionally render the environment to see the current state
    env.render()

    if done:
        break

## Finally, print the game results
for player_id, agent in enumerate([agent0]):
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")