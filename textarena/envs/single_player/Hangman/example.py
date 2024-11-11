import textarena as ta

## initializa the environment
env = ta.make("Hangman-v0")

## Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

## Wrap the environment for pretty rendering
env = ta.wrappers.PrettyRenderWrapper(env=env)

## initalize agents
agent0  = ta.basic_agents.GPTAgent(model_name="gpt-4o-mini")

## reset the environment to start a new game
observations = env.reset(seed=490)

## Write the game loop
done = False
while not done:
    for player_id, agent in enumerate([agent0]):
        ## get the current observation for the player
        obs = observations[player_id]

        ## Get the agent to use the observation and make an action
        action = agent(obs) 

        ## use the action and execute in the environment
        observations, rewards, truncated, terminated, info = env.step(player_id, action)

        ## render the environment
        env.render()

        ## check if the game has ended
        done = truncated or terminated

## Finally, print the game results
for player_id, agent in enumerate([agent0]):
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")