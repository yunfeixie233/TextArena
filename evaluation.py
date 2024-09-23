import os
import random
import wandb
from textarena.llm_wrappers.gpt_agent_wrapper import GPTAgent
from textarena.llm_wrappers.huggingface_agent_wrapper import HuggingFaceAgent
from textarena.game_wrappers.two_player_base_wrapper import TwoPlayerBaseWrapper

def elo_evaluation(agents, game_name, total_games, num_rounds_per_game=1, K=32, verbose=False):
    # Initialize Elo ratings
    elo_ratings = {agent.unique_identifier: 1000 for agent in agents}
    
    # Initialize history for plotting
    elo_history = {agent.unique_identifier: [] for agent in agents}
    game_numbers = []

    # Initialize wandb
    wandb.init(
        project="TextArena", 
        name=f"{game_name}-eval",
        config={
            "game_name": game_name,
            "total_games": total_games,
            "num_rounds_per_game": num_rounds_per_game,
            "K": K
        })

    # Prepare game kwargs
    game_kwargs = {
        "max_turns": 10,
        "render": False
    }

    # For each game
    for game_number in range(1, total_games + 1):
        # Select a pair of agents
        agent_pair = random.sample(agents, 2)
        agent_1, agent_2 = agent_pair

        if verbose:
            print(f"Game {game_number}: Agent {agent_1.unique_identifier} vs Agent {agent_2.unique_identifier}")

        # Initialize game
        wrapped_game = TwoPlayerBaseWrapper(
            game_name=game_name,
            num_rounds=num_rounds_per_game,
            verbose=verbose,
            agent_1=agent_1,
            agent_2=agent_2,
            game_kwargs=game_kwargs
        )

        # Play game
        agent_logs = wrapped_game.play_game()

        # Extract scores
        agent_1_score = agent_logs[agent_1.unique_identifier]["scores"]
        agent_2_score = agent_logs[agent_2.unique_identifier]["scores"]

        # Determine game result
        if agent_1_score > agent_2_score:
            S_A, S_B = 1, 0  # Agent 1 wins
            result = f"Agent {agent_1.unique_identifier} wins"
        elif agent_1_score < agent_2_score:
            S_A, S_B = 0, 1  # Agent 2 wins
            result = f"Agent {agent_2.unique_identifier} wins"
        else:
            S_A, S_B = 0.5, 0.5  # Draw
            result = "Draw"

        # Calculate expected scores
        R_A = elo_ratings[agent_1.unique_identifier]
        R_B = elo_ratings[agent_2.unique_identifier]
        E_A = 1 / (1 + 10 ** ((R_B - R_A) / 400))
        E_B = 1 / (1 + 10 ** ((R_A - R_B) / 400))

        # Update Elo ratings
        elo_ratings[agent_1.unique_identifier] += K * (S_A - E_A)
        elo_ratings[agent_2.unique_identifier] += K * (S_B - E_B)

        # Append current Elo ratings to history
        for agent in agents:
            elo_history[agent.unique_identifier].append(elo_ratings[agent.unique_identifier])
        game_numbers.append(game_number)

        if verbose:
            print(f"Result: {result}")
            print(f"Updated Elo ratings:")
            for agent in agents:
                print(f"Agent {agent.unique_identifier}: {elo_ratings[agent.unique_identifier]:.2f}")
            print("-" * 20)

        # After all games, log the Elo history plot
        elo_plot = wandb.plot.line_series(
            xs=game_numbers,
            ys=[elo_history[agent.unique_identifier] for agent in agents],
            keys=[f"Agent {agent.unique_identifier}" for agent in agents],
            title="Elo Ratings Over Games",
            xname="Game Number"
        )
        wandb.log({"Elo_Ratings": elo_plot})

    # # Optionally, log a summary table
    final_elo = {f"Agent {agent}": elo for agent, elo in elo_ratings.items()}
    wandb.log({"Final_Elo_Ratings": final_elo})

    # Finish wandb run
    wandb.finish()

    return elo_ratings

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    # Create agents with unique identifiers and different models
    agents = [
        GPTAgent(unique_identifier="GPT 4o mini", api_key=api_key, max_tokens=1000, model_name="gpt-4o-mini"),
        GPTAgent(unique_identifier="GPT 3.5 Turbo", api_key=api_key, max_tokens=1000, model_name="gpt-3.5-turbo"),
        GPTAgent(unique_identifier="GPT 4o", api_key=api_key, max_tokens=1000, model_name="gpt-4o"),
        HuggingFaceAgent(unique_identifier="gpt-2", model_name="gpt2", max_tokens=1000, device="cuda"),
        #HuggingFaceAgent(unique_identifier="MobiLlama", model_name="MBZUAI/MobiLlama-05B", max_tokens=1000, device="cuda"),
    ]

    # Run the Elo evaluation
    elo_ratings = elo_evaluation(
        agents=agents,
        game_name="dont_say_it",
        total_games=100,  # Increased number of games for better Elo distribution
        num_rounds_per_game=4,
        K=32,
        verbose=True
    )

    # Print final Elo ratings
    print("Final Elo Ratings:")
    for agent_id, elo in elo_ratings.items():
        print(f"Agent {agent_id}: {elo:.2f}")

if __name__ == "__main__":
    main()
