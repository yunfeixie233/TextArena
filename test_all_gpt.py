""" Use GPT to play each environment a few times. """
import unittest
import textarena as ta 
from textarena.envs import two_player
from textarena.envs.two_player import (
    ConnectFour,
    DontSayIt
)
from textarena.envs.two_player.ConnectFour import test
from textarena.envs.two_player.DontSayIt import test





# build agents
agent_0 = ta.basic_agents.GPTAgent(
    model_name="gpt-4o"
)

agent_1 = ta.basic_agents.GPTAgent(
    model_name="gpt-4o-mini"
)




ENV_NAMES = [
    "ConnectFour-v0",
    "ConnectFour-v0-blind",
    "ConnectFour-v0-large",
    "DontSayIt-v0",
    "DontSayIt-v0-hardcore",
    #"DontSayIt-v0-unlimited",
]


for env_name in ENV_NAMES:
    print(f"Playing: {env_name}")
    # make env
    env = ta.make(env_name)

    # wrap in llm observation wrapper
    env = ta.wrappers.LLMObservationWrapper(env=env)


    # reset
    observations = env.reset()

    done = False 
    while not done:
        for player_id, agent in enumerate([agent_0, agent_1]):
            # get agent observation 
            obs = observations[player_id]

            # get agent action 
            action = agent(obs)


            # execute action
            observations, rewards, truncated, terminated, info = env.step(
                player_id=player_id,
                action=action
            )


            done = truncated or terminated 

    # print the rewards
    for player_id, agent in enumerate([agent_0, agent_1]):
        print(f"{agent.agent_identifier}: {rewards[player_id]}")
    print(info["reason"], end="\n\n\n")

