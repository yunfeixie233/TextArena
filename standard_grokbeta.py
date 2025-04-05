import textarena as ta
 
model_name = "x-ai/grok-beta"
model_description = "Standard x-ai/grok-beta model."
email = "guertlerlo@cfar.a-star.edu.sg"
model_token = "184112d9-ad6d-4a62-9f91-145491008fe5"


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