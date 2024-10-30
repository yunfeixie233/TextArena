import textarena as ta
import random

# Initialize agents with specific models and starting ELO scores
agents = [
    ta.basic_agents.GPTAgent(model_name="gpt-4o-mini"),
    ta.basic_agents.GPTAgent(model_name="gpt-3.5-turbo"),
]

# Define the single-player games to play
game_env_dict = ta.envs.registration.classify_games(filter_category="single_player")
game_env_list = list(game_env_dict.values())[0]

# ELO settings
game_rounds = 1    # Number of rounds per agent per game
k_factor = 32      # K-factor for ELO updates

# Initialize ELO scores per game for each agent
elo_scores = {agent.model_name: {game: 1500 for game in game_env_list} for agent in agents}

# Function to update ELO for a specific game
def update_single_player_elo(agent, game, reward, k=32):
    current_elo = elo_scores[agent.model_name][game]
    
    # In single-player games, assume a benchmark opponent ELO of 1500
    opponent_elo = 1500

    # Calculate expected score
    expected_score = 1 / (1 + 10 ** ((opponent_elo - current_elo) / 400))
    
    # Actual score based on the reward
    actual_score = reward

    # Calculate the ELO change
    delta_elo = k * (actual_score - expected_score)
    
    # Update ELO for this game
    elo_scores[agent.model_name][game] += int(delta_elo)

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
                obs = observations[0]
                action = agent(obs)
                observations, rewards, truncated, terminated, info = env.step(0, action)
                env.render()
                done = truncated or terminated

            # Update ELO based on game outcome
            round_reward = rewards.get(0, 0)  # Reward for single-player game
            update_single_player_elo(agent, game_env, round_reward, k=k_factor)

            # Log the round outcome for the agent
            print(f"Round {round_num} for {agent.model_name} in {game_env} completed.")
            print(f"Outcome: {'Win' if round_reward > 0 else 'Loss'}")
            print(f"New ELO rating for {agent.model_name} in {game_env}: {elo_scores[agent.model_name][game_env]}")
            print("Game logs:")
            for log_entry in env.state.logs:
                print(log_entry)

# Display final leaderboard sorted by ELO for each game
leaderboard_file = "single_player_elo_leaderboard.md"

print("\nFinal Leaderboards by Game:")
with open(leaderboard_file, "w") as file:
    # Write title and introduction to the leaderboard file
    file.write("# Single Player ELO Leaderboard\n\n")
    file.write("This leaderboard ranks single-player agents based on their ELO ratings after all game rounds.\n")
    file.write(f"Each agent participated in {game_rounds} rounds per game, with ELO scores updated after each round.\n\n")

    # Loop through each game and display a leaderboard for that game
    for game_env in game_env_list:
        file.write(f"## Leaderboard for {game_env}\n\n")
        file.write("| Rank | Model Name       | ELO  |\n")
        file.write("|------|------------------|------|\n")
        
        # Sort agents by their ELO for the current game
        agents_sorted = sorted(agents, key=lambda x: elo_scores[x.model_name][game_env], reverse=True)
        
        for i, agent in enumerate(agents_sorted, start=1):
            file.write(f"| {i} | {agent.model_name} | {elo_scores[agent.model_name][game_env]} |\n")
            print(f"{game_env} - {i}. {agent.model_name}: ELO {elo_scores[agent.model_name][game_env]}")
        
        file.write("\n")  # Add space between game leaderboards
