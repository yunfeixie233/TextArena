import textarena as ta
 
model_name = "[Test] Model-4"
model_description = "[Test] Model-4 description"
model_token = "5ac9c9bd-bc52-4c16-8fd8-6c73cc6715b3"
email = "Model-4@cfar.a-star.edu.sg"


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