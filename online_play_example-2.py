import textarena as ta
 
model_name = "[Test] Model-2"
model_description = "[Test] Model-2 description"
model_token = "70deb050-7a18-4598-bc87-ba584068fe56"
email = "Model-2@cfar.a-star.edu.sg"


# Initialize agent
agent = ta.agents.OpenRouterAgent(model_name="gpt-4o") 


env = ta.make_online(
    env_id=["ConnectFour-v0"], 
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