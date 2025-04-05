import textarena as ta
 
model_name = "minimax/minimax-01"
model_description = "Standard minimax/minimax-01 model."
email = "guertlerlo@cfar.a-star.edu.sg"
model_token = "7088a135-1905-46fb-b603-0ec276b87fad"


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