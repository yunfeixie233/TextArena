import textarena as ta 
from textarena.wrappers import (
    PrettyRenderWrapper,
    LLMObservationWrapper,
    ClipWordsActionWrapper
)

model_token = "de3d864f65b3d3a77dfbaf1b1e4f8a40" 

if model_token is None:
    # register the model
    model_token = ta.register_online_model(
        model_name="GPT-4o (Leon)", # has to be unique
        model_description="OpenAI's GPT-4o model.",
        email="Guertlerlo@cfar.a-star.edu.sg"
    )
    print(model_token)
    exit()

# build agent
agent = ta.basic_agents.OpenRouter(
    model_name="GPT-4o"
)


for _ in range(7):
    # make the online environment
    env, player_id = ta.make_online(
        env_id="ConnectFour-v0",
        model_name="GPT-4o (Leon)",
        model_token=model_token,
    )

    # wrap for easy LLM use
    env = LLMObservationWrapper(env=env)
    # env = ClipWordsActionWrapper(env=env)

    # reset and get initial observations
    observations = env.reset()

    done = False 
    while not done:
        # get agent action
        action = agent(observations[player_id])

        # step
        observations, _, truncated, terminated, _ = env.step(player_id, action)

        # render
        env.render()

        # check if done
        done = truncated or terminated

    # print the game outcome and change in elo
    env.print_results()
