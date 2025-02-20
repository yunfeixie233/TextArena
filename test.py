import textarena as ta

# Initialize agents
agents = {
    # 0: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 1: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    0: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="deepseek/deepseek-r1-distill-qwen-32b")),
    1: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="deepseek/deepseek-r1-distill-qwen-32b")),
    # 0: ta.agents.HumanAgent(),
    # 1: ta.agents.HumanAgent(),
    # 2: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 3: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 4: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 5: ta.agents.wrappers.AnswerTokenAgentWrapper(ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")),
    # 0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
    # 1: ta.agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
}

# agents = {
#     0: ta.agents.HumanAgent(),
#     1: ta.agents.HumanAgent(),
#     2: ta.agents.HumanAgent(),
# }

# Initialize environment from subset and wrap it
# env = ta.make(env_id="Negotiation-multiplayer-v0")
env = ta.make(env_id="TicTacToe-v0")
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.ActionFormattingWrapper(env=env)
# env = ta.wrappers.TerminalRenderWrapper(
#     env=env, player_names={0: "Name 1", 1: "Name 2"}, full_screen=True, record_video=False
# )
# env = ta.wrappers.SimpleRenderWrapper(
#     env=env,
#     # player_names={0: "GPT-4o-mini", 1: "claude-3.5-haiku"},
# )
# input(env.env_id)
env.reset(num_players=len(agents))
done = False
while not done:
    player_id, observation = env.get_observation()
    print(observation)
    # print(f"+"*10)
    # print(f"Player {player_id}")
    action = agents[player_id](observation)
    # print(action)
    # print(player_id, action)
    done, info = env.step(action=action)
rewards = env.close()
print(rewards, info)



    # # Create the chess environment
    # chess_env = ChessEnv(is_open=True, max_turns=50, show_valid=True)
    
    # # Wrap with the enhanced terminal renderer
    # wrapped_env = TerminalRenderWrapper(
    #     env=chess_env,
    #     player_names={0: "White Player", 1: "Black Player"},
    #     full_screen=True,
    #     record_video=False
    # )
    
    # # Initialize the game
    # wrapped_env.reset(num_players=2)
    
    # # Now the game would be rendered with the enhanced terminal renderer
    # print("Game initialized with TerminalRenderWrapper")