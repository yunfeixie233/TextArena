import textarena as ta
 
model_name = "meta-llama/llama-3.3-70b-instruct"
model_description = "Standard meta-llama/llama-3.3-70b-instruct model."
email = "guertlerlo@cfar.a-star.edu.sg"
model_token = "42da6f9c-7154-4994-b420-d9b2833409b9"


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
    info = None
    try:
        while not done:
            try:
                player_id, observation = env.get_observation()
                if player_id is None or not observation:
                    break

                action = agent(observation)
                if not action:
                    break

                done, info = env.step(action=action)

            except RuntimeError:
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break
    finally:
        env.close()
        if info:
            print(info)