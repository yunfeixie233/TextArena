import textarena as ta
 
model_name = "anthropic/claude-3-haiku"
model_description = "Standard anthropic/claude-3-haiku model."
email = "guertlerlo@cfar.a-star.edu.sg"
model_token = "ff0eade7-c2e0-4f17-9e4c-5c86501266fc"


# Initialize agent
agent = ta.agents.OpenRouterAgent(model_name=model_name) 

while True:
    env = ta.make_online(
        env_id=["all"], 
        model_name=model_name,
        model_description=model_description,
        email=email,
        model_token=model_token,
    )
    env = ta.wrappers.LLMObservationWrapper(env=env)


    env.reset(num_players=1)

    done = False
    while not done:
        player_id, observation = env.get_observation()
        action = agent(observation)
        done, info = env.step(action=action)
    env.close()
    print(info)