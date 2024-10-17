"""Literally just code for checking that the environments run given random strings"""

import os
import time

import textarena as ta
import textarena.envs.registration as env_reg
from textarena.agents import AgentInterface

print("Running tests over registry")
ta.pprint_registry_detailed()


class DummyStringAgent(AgentInterface[str]):
    def __init__(self, player_id=None):
        self.player_id = player_id

    def observation_map(self, messages: list[ta.Message]) -> str:
        return "\n\n".join([m[1] for m in messages])

    def __call__(self, observation_rendering: str) -> str:
        try:
            assert isinstance(observation_rendering, str)
        except AssertionError:
            print(f"Observation rendering is not a string: {observation_rendering}")
        return observation_rendering


class HumanAgent(AgentInterface[str]):
    def __init__(self, player_id=None):
        self.player_id = player_id

    def observation_map(self, messages: list[ta.Message]) -> str:
        return "\n\n".join([m[1] for m in messages])

    def __call__(self, observation_rendering: str) -> str:
        print(observation_rendering)
        return input("Put in yo response:")


## TEST 2 PLAYER GAMES
# build agents
agents = [HumanAgent(i) for i in range(10)]

for env, env_spec in env_reg.ENV_REGISTRY.items():
    if "multi_player" in env_spec.entry_point:
        print(f"Testing {env}")
        env = ta.make(env)
        observations, info = env.reset()
        done = False
        while not done:
            for player_id, agent in enumerate(agents[:6]):
                action = agent(agent.observation_map(observations[player_id]))
                observations, reward, truncated, terminated, info = env.step(
                    player_id, action
                )
                done = truncated or terminated
                if done:
                    break
        env.render()
        print("Game completed")
        print(info)
        time.sleep(0.1)

    if "two_player" in env_spec.entry_point:
        print(f"Testing {env}")
        env = ta.make(env)
        observations, info = env.reset()
        done = False
        while not done:
            for player_id, agent in enumerate([agent_0, agent_1]):
                action = agent(agent.observation_map(observations[player_id]))
                observations, reward, truncated, terminated, info = env.step(
                    player_id, action
                )
                done = truncated or terminated
                if done:
                    break
        env.render()
        print("Game completed")
        print(info)
        time.sleep(0.1)
    elif "single_player" in env_spec.entry_point:
        print(f"Testing {env}")
        env = ta.make(env)
        observations, info = env.reset()
        done = False
        while not done:
            action = agent_0(agent_0.observation_map(observations[0]))
            observations, reward, truncated, terminated, info = env.step(0, action)
            done = truncated or terminated
            if done:
                break
        env.render()
        print("Game completed")
        print(info)
        time.sleep(0.1)
    else:
        print(f"Skipping {env}")
        continue
