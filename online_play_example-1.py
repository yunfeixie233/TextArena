import textarena as ta
 
model_name = "[Test] Model-1"
model_description = "[Test] Model-1 description"
model_token = "362e0bcf-0fa6-4315-9ec9-9373ff4d6d41"
email = "Model-1@cfar.a-star.edu.sg"


# Initialize agent
agent = ta.agents.OpenRouterAgent(model_name="gpt-4o") 


env = ta.make_online(
    env_id=["SecretMafia-v0"], 
    model_name=model_name,
    model_token=model_token,
    model_description=model_description,
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