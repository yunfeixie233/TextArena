import textarena as ta
import random

# Initialize agents with specific models and starting ELO scores
agents = [
    ta.basic_agents.GPTAgent(model_name="gpt-4o-mini"),
    ta.basic_agents.GPTAgent(model_name="gpt-3.5-turbo"),
]

# Define the games to play
game_env_dict = ta.envs.registration.classify_games(filter_category="single_player")
game_env_list = list(game_env_dict.values())[0]

# ELO settings
game_rounds = 1    # Number of rounds per agent per game
k_factor = 32      # K-factor for ELO updates

# Loop through each game environment
for game_env in game_env_list:
    print(f"\nStarting game environment: {game_env}")
    env = ta.make(game_env)
    env = ta.wrappers.LLMObservationWrapper(env=env)
    env = ta.wrappers.PrettyRenderWrapper(env=env)

    # Loop through each agent for the specified number of rounds
    for round_num in range(1, game_rounds + 1):
        seed = random.randint(1, 1000)
        for agent in agents:
            print(f"\nStarting Round {round_num} for {agent.model_name} in {game_env}")
            
            # Reset the environment and retrieve initial observations
            observations = env.reset(seed=seed)
            done = False

            # Game loop for each agent
            while not done:
                for player_id, agent in enumerate([agent]):
                    obs = observations[player_id]
                    action = agent(obs)
                    observations, rewards, truncated, terminated, info = env.step(player_id, action)
                    env.render()
                    done = truncated or terminated

            # Update ELO based on game outcome
            round_reward = rewards[player_id] if rewards else 0
            agent.update_elo(reward=round_reward, opponent_elo=1500, k=k_factor) # Opponent ELO set to 1500 for single player. 

            # Log the round outcome for the agent
            print(f"Round {round_num} for {agent.model_name} in {game_env} completed.")
            print(f"Outcome: {'Win' if round_reward > 0 else 'Loss'}")
            print(f"New ELO rating for {agent.model_name}: {agent.elo}")
            print("Game logs:")
            for log_entry in env.state.logs:
                print(log_entry)

# Display final leaderboard sorted by ELO
leaderboard_file = "single_player_elo_leaderboard.md"
agents_sorted = sorted(agents, key=lambda x: x.elo, reverse=True)

print("\nFinal Leaderboard across all games:")
with open(leaderboard_file, "w") as file:
    # Write title and introduction to the leaderboard file
    file.write("# Single Player ELO Leaderboard\n\n")
    file.write("This leaderboard ranks single player agents based on their ELO ratings after all game rounds.\n")
    file.write(f"Each agent participated in {game_rounds} rounds per game, with ELO scores updated after each round.\n\n")
    file.write("## Leaderboard\n\n")
    
    # Write the Markdown table header
    file.write("| Rank | Model Name       | ELO  |\n")
    file.write("|------|------------------|------|\n")
    
    # Write each agent's ranking, name, and ELO in table rows
    for i, agent in enumerate(agents_sorted, start=1):
        file.write(f"| {i} | {agent.model_name} | {agent.elo} |\n")
        print(f"{i}. {agent.model_name}: ELO {agent.elo}")