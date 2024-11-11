import textarena as ta
import time
import random
import itertools

# Initialize agents with specific models
agents = [
    ta.basic_agents.GPTAgent(model_name="gpt-4o-mini"),
    ta.basic_agents.GPTAgent(model_name="gpt-3.5-turbo"),
    ta.basic_agents.GPTAgent(model_name="gpt-4o"),
]

# Define the two-player games to play
game_env_dict = ta.envs.registration.classify_games(filter_category="two_player")
game_env_list = list(game_env_dict.values())[0]

# Initialize ELO scores per agent and game environment
elo_scores = {agent.model_name: {game: 1500 for game in game_env_list} for agent in agents} ## TODO: is 1500 the best starting ELO?

# ELO settings
game_rounds = 1             # Number of rounds per game
iteration_per_round = 1     # Number of iterations per round
k_factor = 32               # K-factor for ELO updates

## Minutes:
## For the permutation, when we get big models, we are responsible for running them.
## In chess, players will play one another in the same "category" or "benchmark". Besides ELO, there's a plus 1 minus 1? 
## Rather than choosing one most close, how about sampling? That's possible. Coz all permutation will not be the effective way to choose pairs. 
## 
## For resource: Otherwise, any other way to go about it? Running models bia huggingface will be harder, as there might be limits. Might have to get grants from HF. 
## Are we ready to run them?
## Can we get submissions to see if they can beat GPT-40-mini?
## There seems to be a lot of factors that determines if we can run people's models without issues, e.g. CUDA versions, etc. 
## Could the use of an API for online evals, work? 
## 
## Games: Should we classify official and non-official games? 
## For a generalist - not letting users what game they are playing. 
## Let the commujnity determine which are the popular games, to which we can have a leaderboard.
## 
## In the submission, add the hyperparameters that will matter most. Some could be parameter size, etc. That will allow us to filter the leaderboard. 
## Also, to share their github. Incentivize those who share their model via links. 
##
## For a bigger release, can we release a dataset from players who play the games? Can we reach out to people for ideas on datasets?
## refer to Ofir Press's work (SWE-bench), or https://github.com/hendrycks/test
##
##  https://www.microsoft.com/en-us/research/project/textworld/

# Function to calculate ELO changes using a batch approach
# this ensures that the ELO changes are calculated for all the agents in a batch and then applied at the end of the round
def calculate_elo_changes(agent1, agent2, reward1, reward2, pre_game_elos, k=32):
    # Calculate expected scores based on pre-game Elo ratings
    expected_score1 = 1 / (1 + 10 ** ((pre_game_elos[agent2.model_name] - pre_game_elos[agent1.model_name]) / 400))
    expected_score2 = 1 - expected_score1

    # Calculate Elo changes for the round
    delta_elo1 = k * (reward1 - expected_score1)
    delta_elo2 = k * (reward2 - expected_score2)
    
    return {agent1.model_name: delta_elo1, agent2.model_name: delta_elo2}

# Loop through each game environment
for game_env in game_env_list:
    print(f"\nStarting game environment: {game_env}")
    env = ta.make(game_env)
    env = ta.wrappers.LLMObservationWrapper(env=env)

    # Loop through each round
    for round_num in range(1, game_rounds + 1):
        print(f"\nStarting Round {round_num} in {game_env}")
        
        # Put in all combinations of agents for the round-robin competition (e.g. A vs B and B vs A is acceptable given some games may have starting advantages)
        agent_pairs = [(agent1, agent2) for agent1 in agents for agent2 in agents if agent1 != agent2] 

        # Store initial ELO ratings for batch calculation
        pre_game_elos = {agent.model_name: elo_scores[agent.model_name][game_env] for agent in agents}
        cumulative_elo_changes = {agent.model_name: 0 for agent in agents}  # Initialize cumulative changes

        # Loop through each pair for the round-robin competition
        for agent1, agent2 in agent_pairs:
            print(f"\nMatch: {agent1.model_name} vs {agent2.model_name}")

            # Initialize total rewards for the two agents
            total_reward1 = 0
            total_reward2 = 0

            # Loop through each iteration of the round
            for _ in range(iteration_per_round):
                print(f"\nIteration {_ + 1} of {iteration_per_round} of Round {round_num} in {game_env}")
        
                # Reset the environment and retrieve initial observations for a new game between the pair
                observations = env.reset(seed=random.randint(1, 1000))
                done = False
                rewards = {0: 0, 1: 0}  # Temporary rewards storage for the two agents

                # Game loop for the two agents
                while not done:
                    for player_id, agent in enumerate([agent1, agent2]):
                        
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
                
                # Extract rewards for the two agents
                reward1 = rewards.get(0, 0)
                reward2 = rewards.get(1, 0)
                print(f"Iteration {_ + 1} rewards: {agent1.model_name} - {reward1}, {agent2.model_name} - {reward2}")

                # Accumulate rewards for the two agents
                total_reward1 += reward1
                total_reward2 += reward2

            # Calculate ELO changes but do not apply them yet
            elo_changes = calculate_elo_changes(agent1, agent2, total_reward1, total_reward2, pre_game_elos, k=k_factor)
            print(f"Elo changes: {elo_changes}")
            cumulative_elo_changes[agent1.model_name] += elo_changes[agent1.model_name]
            cumulative_elo_changes[agent2.model_name] += elo_changes[agent2.model_name]

            # Log the match outcome 
            ## TODO - can be removed?
            print(f"Match completed: {agent1.model_name} (Reward: {total_reward1}) vs {agent2.model_name} (Reward: {total_reward2})")
            print("Game logs:")
            for log_entry in env.state.logs:
                print(log_entry)

        # Apply cumulative ELO changes in batch at the end of the round
        for agent in agents:
            elo_scores[agent.model_name][game_env] += int(cumulative_elo_changes[agent.model_name])
            print(f"{agent.model_name} ELO in {game_env} after batch update: {elo_scores[agent.model_name][game_env]}")

# Display final leaderboard sorted by ELO for each game
leaderboard_file = "eval/two_player_leaderboard.md"

print("\nFinal Leaderboards by Game:")
with open(leaderboard_file, "w") as file:
    # Write title and introduction to the leaderboard file
    file.write("# 🏆 Two Player ELO Leaderboard\n\n")
    file.write("**This leaderboard ranks agents based on their ELO ratings across two-player games.**\n")
    file.write(f"*Each agent competed in {game_rounds} rounds of {iteration_per_round} iterations per game per opponent, with ELO scores updated after each round.*\n\n")
    file.write("---\n\n")

    # Explanation of icons
    file.write("### Explanation of Icons\n\n")
    file.write("- 🎖️ **Top Agent**: Agent with the highest ELO score for each game.\n")
    file.write("- 🏅 **ELO**: Rating representing skill level based on match outcomes.\n")

    # Leaderboard Summary Table
    file.write("## Leaderboard Summary\n\n")
    file.write("| Game          | 🎖️ Top Agent     | 🏅 ELO  |\n")
    file.write("|---------------|-------------------|---------|\n")

    # Collect summary information for each game
    summary_rows = []
    for game_env in game_env_list:
        # Sort agents by ELO for the current game
        agents_sorted = sorted(agents, key=lambda x: elo_scores[x.model_name][game_env], reverse=True)
        
        # Get top agent details for the summary
        top_agent = agents_sorted[0]
        top_elo = elo_scores[top_agent.model_name][game_env]
        
        # Add to summary table
        file.write(f"| {game_env} | {top_agent.model_name} | {top_elo} |\n")
    
    file.write("\n---\n\n## Detailed Leaderboards\n\n")
    
    # Detailed Leaderboard for Each Game
    for game_env in game_env_list:
        file.write(f"### {game_env}\n\n")
        file.write("| Rank | Model           | 🏅 ELO |\n")
        file.write("|------|------------------|-------|\n")
        
        # Sort agents by ELO for the current game
        agents_sorted = sorted(agents, key=lambda x: elo_scores[x.model_name][game_env], reverse=True)
        
        for i, agent in enumerate(agents_sorted, start=1):
            elo = elo_scores[agent.model_name][game_env]
            file.write(f"| {i} | {agent.model_name} | {elo} |\n")
            print(f"{game_env} - {i}. {agent.model_name}: ELO {elo}")
        
        file.write("\n")  # Add space between game leaderboards
