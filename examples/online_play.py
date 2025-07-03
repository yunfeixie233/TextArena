import textarena as ta
 
MODEL_NAME = "test-gpt4o-v6"
MODEL_DESCRIPTION = "Stancsscsdard OpenAI GPT-4o model."
EMAIL = "debug@example.com"

# Initialize agent
agent = ta.agents.OpenRouterAgent(model_name="gpt-4o") 

env = ta.make_online(
    env_id=["SpellingBee-v0", "SimpleNegotiation-v0", "Poker-v0"], 
    model_name=MODEL_NAME,
    model_description=MODEL_DESCRIPTION,
    email=EMAIL,
    agent=agent
)
env.reset(num_players=1) # always set to 1 when playing online, even when playing multiplayer games.

done = False
while not done:
    player_id, observation = env.get_observation()
    action = agent(observation)
    done, step_info = env.step(action=action)

rewards, game_info = env.close()