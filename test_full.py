import textarena as ta 
from textarena.wrappers import (
    PrettyRenderWrapper,
    LLMObservationWrapper,
    ClipWordsActionWrapper
)

# build agents
agent_0 = ta.basic_agents.OpenRouter(
    model_name="GPT-4o"
)
agent_1 = ta.basic_agents.OpenRouter(
    model_name="GPT-4o-mini"
)

# make the environment
env = ta.make("DontSayIt-v0")

# wrap for easy LLM use
env = LLMObservationWrapper(env=env)
env = ClipWordsActionWrapper(env=env, max_num_words=500)

# wrap for nice printing
env = PrettyRenderWrapper(
    env=env,
    agent_identifiers={
        0: agent_0.model_name,
        1: agent_1.model_name,
    }
)


# reset and get initial observations
observations = env.reset()

done = False 
while not done:
    # iterate over players
    for player_id, agent in enumerate([agent_0, agent_1]):
        # get agent action
        action = agent(observations[player_id])

        # step
        observations, reward, truncated, terminated, info = env.step(player_id, action)

        # render
        env.render()

        # check if done
        done = truncated or terminated
        if done:
            break