from textarena.envs.two_player.dont_say_it import DontSayItEnv
import time, os, openai

from textarena.wrappers import (
    PrettyRenderWrapper,
    LLMObservationWrapper,
    ClipWordsActionWrapper
)


import textarena as ta
import json 
import copy 


env_name = "ConnectFour-v0"


# ta.pprint_registry()

# create the necessary folder
sft_folder = os.path.join("textarena", "sft_dataset", env_name)
if not os.path.exists(sft_folder):
    os.makedirs(sft_folder)




for _ in range(15):
    # build agents
    # agent_0 = ta.basic_agents.HFLocalAgent(
    #     model_name="meta-llama/Llama-3.2-1B",
    #     quantize=True
    # )
    agent_0 = ta.basic_agents.GPTAgent(
        model_name="gpt-4o"
    )
    agent_1 = ta.basic_agents.GPTAgent(
        model_name="gpt-4o-mini"
    )

    # env = DontSayItEnv(hardcore=True)
    env = ta.make(env_name)

    # wrap for LLM use
    env = LLMObservationWrapper(env=env)

    # env = ClipWordsActionWrapper(env, max_num_words=150)

    # wrap env
    env = PrettyRenderWrapper(
        env=env,
        agent_identifiers={
            0: agent_0.agent_identifier,
            1: agent_1.agent_identifier
        }
    )


    observations = env.reset()
    # input(env.game_state)

    # we need to keep track of str obs, str act, full_obs, agent names, rewards, truncated, terminated, info
    tracker = []

    done=False
    while not done:
        for player_id, agent in enumerate([agent_0, agent_1]):
            # get the agent prompt
            action = agent(
                observations[player_id]
            )
            # print(observations[player_id])
            # input(action)
            full_str_observation = observations[player_id]
            full_structured_observation = env.full_observations[player_id].copy()

            observations, rewards, truncated, terminated, info = env.step(player_id, action)
            # env.render()
            # time.sleep(1)

            step_track = {
                "player_id": player_id,
                "agent_identifier": agent.agent_identifier,
                "full_str_observation": full_str_observation,
                "full_observation": full_structured_observation,
                "str_action": action,
                "reward": rewards[player_id] if rewards is not None else None,
                "terminated": terminated,
                "truncated": truncated,
                "info": info,
                "role_mapping": env.state.role_mapping
            }

            tracker.append(step_track)




            done = truncated or terminated

            if done:
                break

    # store tracker as json
    with open(os.path.join(sft_folder, f"game_{len(os.listdir(sft_folder))}.json"), "w", encoding="utf-8") as f:
        json.dump(tracker, f, ensure_ascii=False, indent=4)