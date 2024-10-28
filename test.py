import time, os, openai

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
env = ta.make("Chess-v0-long")

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
# input(observations)

done=False
while not done:
    for player_id, agent in enumerate([agent_0, agent_1]):
        # get the agent prompt
        action = agent(
            observations[player_id]
        )
        # print(observations[player_id])
        # input(action)

        observations, reward, truncated, terminated, info = env.step(player_id, action)
        env.render()
        input(observations)
        time.sleep(1)

        done = truncated or terminated

        if done:
            break

for l in env.state.logs:
    print(l, end="\n\n") 
# time.sleep(1)
# _, _, truncated, terminated, _ =env.step(1, "Another test, just to see.")
# env.render()
# time.sleep(1)   
# done = truncated or terminated


# while True:
#     # Player 0's turn
#     #print(f"\n{agent_identifiers.get(0, 'Player 0')}'s turn.")
#     #print(obs0)
#     action0 = input("Enter your message: ")
#     obs1, reward, truncated, terminated, info = env.step(player_id=0, action=action0)
#     env.render()
#     if terminated or truncated:
#         break

#     # Player 1's turn
#     #print(f"\n{agent_identifiers.get(1, 'Player 1')}'s turn.")
#     #print(obs1)
#     action1 = input("Enter your message: ")
#     obs0, reward, truncated, terminated, info = env.step(player_id=1, action=action1)
#     env.render()
#     if terminated or truncated:
#         break