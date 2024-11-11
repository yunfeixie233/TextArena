import textarena as ta
import random

# Initialize agents with specific models
agents = [
    ta.basic_agents.GPTAgent(model_name="gpt-4o-mini"),
    ta.basic_agents.GPTAgent(model_name="gpt-3.5-turbo"),
]

# Define the single-player games to play
game_env_dict = ta.envs.registration.classify_games(filter_category="single_player")
game_env_list = list(game_env_dict.values())[0]

# Evaluation settings
game_rounds = 10  # Number of rounds per agent per game

# Create dictionaries to store metrics for each agent and game environment
reward_scores = {agent.model_name: {game: 0 for game in game_env_list} for agent in agents}
win_counts = {agent.model_name: {game: 0 for game in game_env_list} for agent in agents}
streak_counts = {agent.model_name: {game: {'current': 0, 'longest': 0} for game in game_env_list} for agent in agents}

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

                # Get the current observation for the player
                obs = observations[0]

                # Agent decides on an action based on the observation
                action = agent(obs)

                # Execute the action in the environment
                observations, rewards, truncated, terminated, info = env.step(0, action)

                # Check if the game has ended
                done = terminated or truncated
                if done:
                    break

            # Track and update rewards, win counts, and streaks
            round_reward = rewards.get(0, 0)  # Reward for single-player game
            reward_scores[agent.model_name][game_env] += round_reward
            
            # Update win count and streak
            if round_reward > 0:  # This means the agent won
                win_counts[agent.model_name][game_env] += 1
                streak_counts[agent.model_name][game_env]['current'] += 1
                if streak_counts[agent.model_name][game_env]['current'] > streak_counts[agent.model_name][game_env]['longest']:
                    streak_counts[agent.model_name][game_env]['longest'] = streak_counts[agent.model_name][game_env]['current']
            else:  # Loss or Draw
                streak_counts[agent.model_name][game_env]['current'] = 0

            # Log the round outcome for the agent
            ## TODO - Is this necessary?
            print(f"Round {round_num} for {agent.model_name} in {game_env} completed.")
            print(f"Outcome: {'Win' if round_reward > 0 else 'Loss/Draw'}")
            print(f"New Reward for {agent.model_name} in {game_env}: {reward_scores[agent.model_name][game_env]}")
            print("Game logs:")
            for log_entry in env.state.logs:
                print(log_entry)

# Display final leaderboard sorted by reward for each game
leaderboard_file = "eval/single_player_leaderboard.md"

print("\nFinal Leaderboards by Game:")
with open(leaderboard_file, "w") as file:
    # Write title and introduction to the leaderboard file
    file.write("# 🎮 Single Player Leaderboard\n\n")
    file.write(f"**Each agent played {game_rounds} rounds per game, earning rewards for wins, win rate percentages, and longest winning streaks.**\n\n")

    # Explanation of icons
    file.write("---\n\n### Explanation of Icons\n\n")
    file.write("- 🏅 **Reward**: Final score based on win/loss outcomes.\n")
    file.write("- 🔥 **Win Rate**: Percentage of games won.\n")
    file.write("- 📈 **Longest Streak**: Maximum consecutive wins.\n")
    
    # Leaderboard Summary Table
    file.write("---\n\n## Leaderboard Summary\n\n")
    file.write("| Game | 🏆 Top Agent | 🏅 Reward | 🔥 Win Rate | 📈 Longest Streak |\n")
    file.write("|------|--------------|----------|------------|-------------------|\n")
    
    # Collect top agent info for each game for summary table
    summary_rows = []
    for game_env in game_env_list:
        # Sort agents by reward for the current game
        agents_sorted = sorted(agents, key=lambda x: reward_scores[x.model_name][game_env], reverse=True)
        
        # Get top agent details for summary
        top_agent = agents_sorted[0]
        top_reward = reward_scores[top_agent.model_name][game_env]
        win_rate = (win_counts[top_agent.model_name][game_env] / game_rounds) * 100
        longest_streak = streak_counts[top_agent.model_name][game_env]['longest']
        
        # Add to summary table
        file.write(f"| {game_env} | {top_agent.model_name} | {top_reward:+} | {win_rate:.0f}% | {longest_streak} |\n")
    
    file.write("\n---\n\n## Detailed Leaderboards\n\n")
    
    # Loop through each game and display a leaderboard for that game
    for game_env in game_env_list:
        file.write(f"### {game_env}\n\n")
        file.write("| Rank | Model        | 🏅 Reward | 🔥 Win Rate | 📈 Longest Streak |\n")
        file.write("|------|--------------|----------|------------|-------------------|\n")
        
        # Sort agents by reward for the current game
        agents_sorted = sorted(agents, key=lambda x: reward_scores[x.model_name][game_env], reverse=True)
        
        for i, agent in enumerate(agents_sorted, start=1):
            total_games = game_rounds
            reward = reward_scores[agent.model_name][game_env]
            win_rate = (win_counts[agent.model_name][game_env] / total_games) * 100
            longest_streak = streak_counts[agent.model_name][game_env]['longest']
            file.write(f"| {i} | {agent.model_name} | {reward:+} | {win_rate:.2f}% | {longest_streak} |\n")
            print(f"{game_env} - {i}. {agent.model_name}: Reward {reward}, Win Rate {win_rate:.2f}%, Longest Win Streak {longest_streak}")
        
        file.write("\n")  # Add space between game leaderboards
    

