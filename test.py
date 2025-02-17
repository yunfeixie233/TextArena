import textarena as ta

# Initialize agents
agents = {
    0: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o")),
    # 1: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o")),
    # 2: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o")),
    # 3: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o")),
    # 4: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o")),
    # 0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
    # 1: ta.agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
}

# Initialize environment from subset and wrap it
# env = ta.make(env_id="Negotiation-multiplayer-v0")
env = ta.make(env_id="GuessTheNumber-v0")
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.SimpleRenderWrapper(
    env=env,
    # player_names={0: "GPT-4o-mini", 1: "claude-3.5-haiku"},
)

env.reset() #num_players=len(agents))
done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, info = env.step(action=action)
rewards = env.close()
print(rewards)