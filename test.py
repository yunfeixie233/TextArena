import textarena as ta

# Initialize agents
agents = {
    0: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 1: ta.agents.wrappers.Answe   rTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 1: ta.agents.HumanAgent(),
    # 2: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 3: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 4: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
    # 1: ta.agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
}

# Initialize environment from subset and wrap it
# env = ta.make(env_id="Negotiation-multiplayer-v0")
env = ta.make(env_id=["WordSearch-v0", "WordLadder-v0"])
env = ta.wrappers.LLMObservationWrapper(env=env)
# env = ta.wrappers.SimpleRenderWrapper(
#     env=env,
#     # player_names={0: "GPT-4o-mini", 1: "claude-3.5-haiku"},
# )
input(env.env_id)
env.reset(num_players=len(agents))
done = False
while not done:
    player_id, observation = env.get_observation()
    print(observation)
    action = agents[player_id](observation)
    print(player_id, action)
    done, info = env.step(action=action)
rewards = env.close()
print(rewards, info)
