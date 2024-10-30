import textarena as ta
import time
import random

# Initialize agents with specific models and starting ELO scores
agents = [
    ta.basic_agents.GPTAgent(model_name="gpt-4o-mini"),
    ta.basic_agents.GPTAgent(model_name="gpt-3.5-turbo"),
]

# Define the two-player games to play
game_env_dict = ta.envs.registration.classify_games(filter_category="two_player")
game_env_list = list(game_env_dict.values())[0]

# ELO settings
game_rounds = 1    # Number of rounds per game
k_factor = 32      # K-factor for ELO updates

# Function to calculate ELO updates using average opponent ELO
def calculate_average_opponent_elo_update(agents, rewards, k=32):
    # Store original ELO ratings to avoid sequential dependency
    pre_game_elos = {agent.model_name: agent.elo for agent in agents}

    # Update ELO for each player based on average opponent ELO
    for i, agent in enumerate(agents):
        # Calculate average ELO of opponents
        opponent_elos = [pre_game_elos[a.model_name] for j, a in enumerate(agents) if j != i]
        average_opponent_elo = sum(opponent_elos) / len(opponent_elos)

        # Calculate expected score for the agent
        expected_score = 1 / (1 + 10 ** ((average_opponent_elo - pre_game_elos[agent.model_name]) / 400))

        # Actual score from the game outcome
        actual_score = rewards.get(i, 0)

        # Calculate and apply the ELO update
        delta_elo = k * (actual_score - expected_score)
        agent.elo += int(delta_elo)

# Loop through each game environment
for game_env in game_env_list:
    print(f"\nStarting game environment: {game_env}")
    env = ta.make(game_env)
    env = ta.wrappers.LLMObservationWrapper(env=env)

    # Loop through each round
    for round_num in range(1, game_rounds + 1):
        print(f"\nStarting Round {round_num} in {game_env}")
        # Reset the environment and retrieve initial observations
        observations = env.reset(seed=random.randint(1, 1000))
        done = False

        # Game loop for two players
        while not done:
            for player_id, agent in enumerate(agents):
                # Get the current observation for the player
                obs = observations[player_id]

                # Agent decides on an action based on the observation
                action = agent(obs)

                # Execute the action in the environment
                observations, rewards, truncated, terminated, info = env.step(player_id, action)

                # Check if the game has ended
                done = terminated or truncated
                if done:
                    break

        # Perform ELO updates using average opponent ELO
        calculate_average_opponent_elo_update(agents, rewards, k=k_factor)

        # Log the round outcome
        print(f"Round {round_num} completed in {game_env}.")
        for i, agent in enumerate(agents):
            print(f"{agent.model_name} ELO: {agent.elo}, Reward: {rewards.get(i, 0)}")
        print("Game logs:")
        for log_entry in env.state.logs:
            print(log_entry)

# Display final leaderboard after all games
print("\nFinal Leaderboard across all two-player games:")
agents_sorted = sorted(agents, key=lambda x: x.elo, reverse=True)
for i, agent in enumerate(agents_sorted, start=1):
    print(f"{i}. {agent.model_name}: ELO {agent.elo}")
