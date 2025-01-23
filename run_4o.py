import textarena as ta

import time
import numpy as np 

from config import NUM_ROUNDS


model_name = "GPT 4o"
open_router_name = "openai/gpt-4o-2024-11-20"
email = f"{open_router_name.split('/')[1]}@example.com"


# Step 1: Register your model (only needs to be done once)
model_token = ta.register_online_model(
    model_name=model_name,
    model_description="Standard {open_router_name} model.",
    email=email
)


for _ in range(NUM_ROUNDS):
    # Step 2: Initialize agent
    agent = ta.agents.OpenRouterAgent(model_name=open_router_name)

    # Step 3: Initialize online environment
    env = ta.make_online(
        env_id="BalancedSubset-v0",
        model_name=model_name,
        model_token=model_token
    )

    # Step 4: Add wrappers for easy LLM use
    env = ta.wrappers.LLMObservationWrapper(env=env)
    # env = ta.wrappers.PrettyRenderWrapper(
    #     env=env,
    #     player_name="GPT-4o-Mini"
    # )

    # Step 5: Main game loop
    env.reset()
    done = False
    while not done:
        player_id, observation = env.get_observation()
        print("\n\n\n")
        print(f"Observation: {observation}")
        action = agent(observation)
        print(f"Action: {action}")
        print("###########################################################")
        done, info = env.step(action=action)
    rewards = env.close()

    time.sleep(np.random.randint(10, 50))

        