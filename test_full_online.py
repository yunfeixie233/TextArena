import textarena as ta 

model_name = "GPT-4o-mini new2" # has to be unique
model_desc = "OpenAI's GPT-4o model."
email = "Guertlerlweqrwero@cfar.a-star.edu.sg"

# register the model
model_token = ta.register_online_model(
    model_name=model_name, 
    model_description=model_desc,
    email=email
)

# build agent
agent = ta.basic_agents.OpenRouterAgent(model_name="GPT-4o-mini")


for _ in range(50):
    # make the online environment
    env = ta.make_online(
        env_id="ConnectFour-v0",
        model_name=model_name,
        model_token=model_token,
    )

    # wrap for easy LLM use
    env = ta.LLMObservationWrapper(env=env)
    # env = ta.ClipWordsActionWrapper(env=env)

    # reset and get initial observations
    observations = env.reset()

    truncated, terminated = False, False
    while not (truncated or terminated):
        # get the current player id 
        player_id = env.get_current_player_id()

        # get agent action
        action = agent(observations[player_id])

        # print(observations[player_id])
        # input(action)

        # step
        observations, _, truncated, terminated, _ = env.step(player_id, action)


    # print the game outcome and change in elo
    env.close()
