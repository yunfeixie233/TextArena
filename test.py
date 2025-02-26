import textarena as ta
 
# Initialize agents
agents = {
    0: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 1: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="anthropic/claude-3-haiku")),
    # 0: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 1: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="deepseek/deepseek-r1-distill-qwen-1.5b")),
    # 0: ta.agents.HumanAgent(),
    # 2: ta.agents.HumanAgent(),
    # 1: ta.agents.HumanAgent(),
    1: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    2: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
}

# Initialize environment from subset and wrap it
env = ta.make(env_id="Negotiation-v0")
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.ActionFormattingWrapper(env=env)
env = ta.wrappers.SimpleRenderWrapper(
    env=env,
    # player_names={0: "GPT-4o-mini", 1: "claude-3.5-haiku", 2: "claude-3.5-haiku-2"},
)
# input(env.env_id)
env.reset(num_players=len(agents))
done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, info = env.step(action=action)

rewards = env.close()