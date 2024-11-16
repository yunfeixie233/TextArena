import time, os

from textarena.wrappers import (
    PrettyRenderWrapper,
    LLMObservationWrapper,
    ClipWordsActionWrapper
)


import textarena as ta

ta.pprint_registry()



# build agents
agent_0 = ta.basic_agents.GPTAgent(
    model_name="gpt-4o"
)

agent_1 = ta.basic_agents.GPTAgent(
    model_name="gpt-4o-mini"
)

# env = DontSayItEnv(hardcore=True)
env = ta.make("Negotiation-v0")

# wrap for LLM use
env = LLMObservationWrapper(env=env)

env = ClipWordsActionWrapper(env, max_num_words=150)

# wrap env
env = PrettyRenderWrapper(
    env=env,
    agent_identifiers={
        0: agent_0.agent_identifier,
        1: agent_1.agent_identifier
    }
)


observations = env.reset()

done=False
while not done:
    for player_id, agent in enumerate([agent_0, agent_1]):
        # get the agent prompt
        action = agent(
            observations[player_id]
        )

        observations, reward, truncated, terminated, info = env.step(player_id, action)
        env.render()

        done = truncated or terminated

        if done:
            break

