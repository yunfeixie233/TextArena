import textarena as ta
 
model_name = "[Test] Model-5"
model_description = "[Test] Model-5 description"
model_token="a408c0c2-a151-4732-8c01-be729e6a006a"
email = "Model-5@cfar.a-star.edu.sg"


# Initialize agent
agent = ta.agents.OpenRouterAgent(model_name="gpt-4o") 


env = ta.make_online(
    env_id=["SecretMafia-v0"], 
    model_name=model_name,
    model_description=model_description,
    model_token=model_token,
    email=email
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