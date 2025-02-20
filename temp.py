import textarena as ta

# Initialize agents
agents = {
    0: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 1: ta.agents.HumanAgent(),
    1: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 2: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 3: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 4: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 5: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
}


# Initialize environment and wrap it
env = ta.make(env_id="TicTacToe-v0")
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.ActionFormattingWrapper(env=env)


env.reset(num_players=len(agents))
done = False
while not done:
    player_id, observation = env.get_observation()
    print(observation)
    action = agents[player_id](observation)
    done, info = env.step(action=action)
rewards = env.close()