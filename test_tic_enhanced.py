""" 
Enhanced TextArena runner with comprehensive wandb logging and JSON action logging.

Requirements:
- pip install tqdm wandb
"""
import os
import argparse
import multiprocessing
import random
import math
import itertools
import json
import datetime
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
import pandas as pd
import numpy as np
import wandb

# Set API key if needed
os.environ["OPENROUTER_API_KEY"] = "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"
os.environ["WANDB_API_KEY"] = "0ff1feaaaaf719c209f24fec37d878aee51b04fb"
import textarena as ta 

# Elo parameters
K = 32
INITIAL_RATING = 1500
RESULT_RANK = {"won": 2, "tied": 1, "lost": 0}

def get_pair_result(result_i, result_j):
    """
    Given the result strings (e.g., "won", "lost", "tie") for two players,
    return a tuple (S_i, S_j) representing the head-to-head score:
      - S = 1 means win, 0 means loss, 0.5 means tie.
    If both players have the same result (e.g., both "won"), treat it as a tie.
    """
    rank_i = RESULT_RANK.get(result_i, 1)
    rank_j = RESULT_RANK.get(result_j, 1)
    if rank_i > rank_j:
        return 1, 0
    elif rank_i < rank_j:
        return 0, 1
    else:
        return 0.5, 0.5

def expected_score(rating_i, rating_j):
    """Compute the expected score for player i vs. player j."""
    return 1 / (1 + 10 ** ((rating_j - rating_i) / 400))

def determine_game_result(rewards):
    """Convert rewards to game results (won/lost/tied)"""
    if len(rewards) != 2:
        return {"0": "tied", "1": "tied"}
    
    player_0_reward = rewards[0]
    player_1_reward = rewards[1]
    
    if player_0_reward > player_1_reward:
        return {"0": "won", "1": "lost"}
    elif player_1_reward > player_0_reward:
        return {"0": "lost", "1": "won"}
    else:
        return {"0": "tied", "1": "tied"}

def process_game_elo(models_dict, game_result, ratings):
    """
    Process one game and update the Elo ratings.
    models_dict: {player_id: model_name}
    game_result: {player_id: "won"/"lost"/"tied"}
    ratings: {model_name: rating}
    Returns updated ratings.
    """
    player_ids = list(models_dict.keys())
    n = len(player_ids)
    
    # Ensure all models exist in our ratings dictionary
    for pid in player_ids:
        model = models_dict[pid]
        if model not in ratings:
            ratings[model] = INITIAL_RATING

    # For each model (player) in this game, accumulate actual/expected scores
    score_sum = {models_dict[pid]: 0 for pid in player_ids}
    expected_sum = {models_dict[pid]: 0 for pid in player_ids}
    
    # Loop over all unordered pairs of players
    for i in range(n):
        for j in range(i+1, n):
            pid_i = player_ids[i]
            pid_j = player_ids[j]
            model_i = models_dict[pid_i]
            model_j = models_dict[pid_j]
            res_i = game_result.get(pid_i, "tied")
            res_j = game_result.get(pid_j, "tied")
            
            # Determine the head-to-head result
            S_i, S_j = get_pair_result(res_i, res_j)
            
            # Compute expected scores from the current ratings
            R_i = ratings[model_i]
            R_j = ratings[model_j]
            E_i = expected_score(R_i, R_j)
            E_j = expected_score(R_j, R_i)
            
            # Accumulate results
            score_sum[model_i] += S_i
            score_sum[model_j] += S_j
            expected_sum[model_i] += E_i
            expected_sum[model_j] += E_j

    # Update each player's rating
    for pid in player_ids:
        model = models_dict[pid]
        delta = (K / (n - 1)) * (score_sum[model] - expected_sum[model]) if (n > 1) else 0
        ratings[model] += delta

    return ratings


def generate_balanced_game_list(models, games_per_pair):
    """
    Generate a balanced list of model pairs ensuring each pair plays exactly games_per_pair games.
    Returns a shuffled list of model pairs.
    """
    if len(models) < 2:
        raise ValueError("Need at least 2 models to generate games")
    
    # Generate all possible pairs of models
    all_pairs = list(itertools.combinations(models, 2))
    
    # Create games_per_pair copies of each pair
    game_list = []
    for pair in all_pairs:
        for _ in range(games_per_pair):
            # Randomly decide the order of the pair for each game to eliminate position bias
            if random.random() < 0.5:
                game_list.append(list(pair))
            else:
                game_list.append([pair[1], pair[0]])
    
    # Shuffle the complete game list to randomize the order
    random.shuffle(game_list)
    
    return game_list, len(all_pairs)


def create_run_folder(env_id, games_per_pair, model_config, prompt_template):
    """Create a folder for this run with proper naming and subfolders"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"run_{timestamp}_{env_id}_{games_per_pair}games_{model_config}_{prompt_template}"
    folder_path = Path("game_logs") / folder_name
    
    # Create main folder and subfolders
    folder_path.mkdir(parents=True, exist_ok=True)
    (folder_path / "raw").mkdir(exist_ok=True)
    (folder_path / "leaderboard").mkdir(exist_ok=True) 
    (folder_path / "analysis").mkdir(exist_ok=True)
    
    return folder_path


def save_game_json(folder_path, game_num, env_id, prompt_template, model_assignment, action_history, rewards, game_info):
    """Save a game's action history to a JSON file"""
    # Create filename with proper naming
    model1_short = model_assignment[0].split('/')[-1]
    model2_short = model_assignment[1].split('/')[-1]
    filename = f"game_{game_num:04d}_{env_id}_{model1_short}_vs_{model2_short}_{prompt_template}.json"
    filepath = folder_path / "raw" / filename
    
    # Prepare game data
    game_data = {
        "game_number": game_num,
        "environment": env_id,
        "prompt_template": prompt_template,
        "players": {
            "0": model_assignment[0],
            "1": model_assignment[1]
        },
        "rounds": action_history,
        "final_rewards": rewards,
        "game_info": game_info,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Save to JSON
    with open(filepath, 'w') as f:
        json.dump(game_data, f, indent=2)


def save_leaderboard_json(folder_path, env_id, games_per_pair, model_config, prompt_template, wandb_run_name, table_data, columns, stats):
    """Save the leaderboard data to a JSON file"""
    # Create filename for leaderboard
    filename = f"leaderboard_{env_id}_{games_per_pair}games_{model_config}_{prompt_template}.json"
    filepath = folder_path / "leaderboard" / filename
    
    # Prepare leaderboard data
    leaderboard_data = {
        "run_name": wandb_run_name,
        "environment": env_id,
        "games_per_pair": games_per_pair,
        "model_config": model_config,
        "prompt_template": prompt_template,
        "columns": columns,
        "table_data": table_data,
        "summary_stats": {
            "total_games": stats['total_games'],
            "draw_rate": stats['draw_rate'],
            "unique_pairs": len(stats['model_wins']) * (len(stats['model_wins']) - 1) // 2,
            "models": list(stats['model_wins'].keys())
        },
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Save to JSON
    with open(filepath, 'w') as f:
        json.dump(leaderboard_data, f, indent=2)


# Analysis functions from analyze_leaderboards.py
def load_leaderboard_data_from_objects(leaderboard_data_list):
    """
    Load data from leaderboard data objects (not JSON files).
    
    Returns:
        list: List of dictionaries containing run data
    """
    return leaderboard_data_list


def extract_model_data_from_runs(all_runs):
    """
    Extract model performance data from all runs.
    
    Returns:
        dict: Nested dict {model_name: {run_name: {elo: x, win_rate: y, ...}}}
    """
    model_data = defaultdict(dict)
    
    for run_data in all_runs:
        run_name = run_data['run_name']
        table_data = run_data['table_data']
        columns = run_data['columns']
        
        # Find column indices
        model_idx = columns.index('Model')
        elo_idx = columns.index('Elo')
        win_rate_idx = columns.index('Win Rate')
        
        # Extract data for each model in this run
        for row in table_data:
            model_name = row[model_idx]
            elo = float(row[elo_idx])
            win_rate = float(row[win_rate_idx])
            
            model_data[model_name][run_name] = {
                'elo': elo,
                'win_rate': win_rate,
                'run_data': row  # Store full row for reference
            }
    
    return model_data


def calculate_performance_statistics_from_data(model_data):
    """
    Calculate mean and standard deviation of Elo and win rate for each model.
    
    Returns:
        pd.DataFrame: DataFrame with performance statistics
    """
    stats_data = []
    
    for model_name, run_data in model_data.items():
        # Extract Elo and win rate values across runs
        elos = [data['elo'] for data in run_data.values()]
        win_rates = [data['win_rate'] for data in run_data.values()]
        
        # Calculate statistics
        stats_data.append({
            'Model': model_name,
            'Num_Runs': len(run_data),
            'Mean_Elo': np.mean(elos),
            'Std_Elo': np.std(elos, ddof=1) if len(elos) > 1 else 0.0,
            'Min_Elo': np.min(elos),
            'Max_Elo': np.max(elos),
            'Mean_Win_Rate': np.mean(win_rates),
            'Std_Win_Rate': np.std(win_rates, ddof=1) if len(win_rates) > 1 else 0.0,
            'Min_Win_Rate': np.min(win_rates),
            'Max_Win_Rate': np.max(win_rates)
        })
    
    # Create DataFrame and sort by mean Elo (highest to lowest)
    df = pd.DataFrame(stats_data)
    df = df.sort_values('Mean_Elo', ascending=False).reset_index(drop=True)
    
    return df


def calculate_ranking_statistics_from_data(model_data, all_runs):
    """
    Calculate ranking statistics for each model across runs.
    
    Returns:
        pd.DataFrame: DataFrame with ranking statistics
    """
    # Get all unique run names
    all_run_names = [run['run_name'] for run in all_runs]
    
    # Calculate rankings for each run
    run_rankings = {}
    
    for run_data in all_runs:
        run_name = run_data['run_name']
        table_data = run_data['table_data']
        columns = run_data['columns']
        
        model_idx = columns.index('Model')
        elo_idx = columns.index('Elo')
        
        # Extract model-elo pairs and sort by Elo (highest first)
        model_elos = []
        for row in table_data:
            model_name = row[model_idx]
            elo = float(row[elo_idx])
            model_elos.append((model_name, elo))
        
        # Sort by Elo descending and assign ranks (1-based)
        model_elos.sort(key=lambda x: x[1], reverse=True)
        rankings = {model: rank + 1 for rank, (model, elo) in enumerate(model_elos)}
        run_rankings[run_name] = rankings
    
    # Calculate ranking statistics for each model
    ranking_stats = []
    all_models = set()
    for rankings in run_rankings.values():
        all_models.update(rankings.keys())
    
    for model_name in all_models:
        # Get rankings across all runs (only for runs where this model appears)
        model_rankings = []
        model_runs = 0
        
        for run_name, rankings in run_rankings.items():
            if model_name in rankings:
                model_rankings.append(rankings[model_name])
                model_runs += 1
        
        if model_rankings:
            ranking_stats.append({
                'Model': model_name,
                'Num_Runs': model_runs,
                'Mean_Rank': np.mean(model_rankings),
                'Std_Rank': np.std(model_rankings, ddof=1) if len(model_rankings) > 1 else 0.0,
                'Best_Rank': np.min(model_rankings),
                'Worst_Rank': np.max(model_rankings),
                'Median_Rank': np.median(model_rankings)
            })
    
    # Create DataFrame and sort by mean rank (best rank first)
    df = pd.DataFrame(ranking_stats)
    df = df.sort_values('Mean_Rank', ascending=True).reset_index(drop=True)
    
    return df


def save_detailed_results_to_folder(model_data, output_folder, output_prefix):
    """
    Save detailed per-run results for each model.
    """
    detailed_data = []
    
    for model_name, run_data in model_data.items():
        for run_name, data in run_data.items():
            detailed_data.append({
                'Model': model_name,
                'Run_Name': run_name,
                'Elo': data['elo'],
                'Win_Rate': data['win_rate']
            })
    
    detailed_df = pd.DataFrame(detailed_data)
    detailed_df = detailed_df.sort_values(['Model', 'Run_Name'])
    
    detailed_file = output_folder / f"{output_prefix}_detailed_results.csv"
    detailed_df.to_csv(detailed_file, index=False, float_format='%.4f')
    
    return detailed_file


def run_cross_template_analysis(all_leaderboard_data, main_run_folder, env_id, games_per_pair, model_config):
    """
    Run cross-template analysis and save results to CSV files.
    
    Args:
        all_leaderboard_data: List of leaderboard data dictionaries from all templates
        main_run_folder: Path to main run folder 
        env_id: Environment ID
        games_per_pair: Number of games per pair
        model_config: Model configuration name
    """
    if len(all_leaderboard_data) < 2:
        print("Analysis requires at least 2 prompt templates. Skipping cross-template analysis.")
        return
    
    print(f"\nRunning cross-template analysis on {len(all_leaderboard_data)} prompt templates...")
    
    # Extract model data across runs
    model_data = extract_model_data_from_runs(all_leaderboard_data)
    
    # Calculate performance statistics
    performance_stats = calculate_performance_statistics_from_data(model_data)
    
    # Calculate ranking statistics  
    ranking_stats = calculate_ranking_statistics_from_data(model_data, all_leaderboard_data)
    
    # Create output prefix
    output_prefix = f"cross_template_{env_id}_{games_per_pair}games_{model_config}"
    analysis_folder = main_run_folder / "analysis"
    
    # Save results
    perf_file = analysis_folder / f"{output_prefix}_performance_stats.csv"
    rank_file = analysis_folder / f"{output_prefix}_ranking_stats.csv"
    
    performance_stats.to_csv(perf_file, index=False, float_format='%.4f')
    ranking_stats.to_csv(rank_file, index=False, float_format='%.4f')
    
    # Save detailed results
    detailed_file = save_detailed_results_to_folder(model_data, analysis_folder, output_prefix)
    
    print(f"Cross-template analysis complete!")
    print(f"  Performance stats saved to: {perf_file}")
    print(f"  Ranking stats saved to: {rank_file}") 
    print(f"  Detailed results saved to: {detailed_file}")
    
    # Print summary
    print(f"\nCROSS-TEMPLATE ANALYSIS SUMMARY:")
    print(f"=" * 50)
    print(f"Templates analyzed: {len(all_leaderboard_data)}")
    print(f"Models found: {len(model_data)}")
    
    print(f"\nTop 5 models by mean Elo across templates:")
    for i, row in performance_stats.head(5).iterrows():
        model = row['Model']
        mean_elo = row['Mean_Elo']
        std_elo = row['Std_Elo']
        print(f"  {i+1}. {model}: {mean_elo:.1f} ± {std_elo:.1f}")


def run_single_game_with_logging(args):
    """Run a single game and collect action history"""
    model_pair, env_id, prompt_template, game_num = args
    
    if not isinstance(model_pair, list) or len(model_pair) != 2:
        raise ValueError(f"Expected exactly 2 models, got: {model_pair}")
    
    # Initialize agents with the two models
    agents = {}
    model_assignment = {}
    for i in range(2):
        agents[i] = ta.agents.OpenRouterAgent(model_name=model_pair[i])
        model_assignment[i] = model_pair[i]

    # Initialize the environment
    env = ta.make(env_id=env_id, prompt_template=prompt_template)

    env.reset(num_players=len(agents))

    # Track action history
    action_history = []
    round_num = 0
    
    done = False
    while not done:
        player_id, observation = env.get_observation()
        
        # Get action from agent - record raw response
        response = agents[player_id](observation)
        
        # Log the round with raw response
        round_data = {
            "round": round_num,
            "player_id": player_id,
            "model": model_assignment[player_id],
            "observation": observation,
            "response": response,  # Raw response from model
            "prompt_template": prompt_template  # Log which template was supposed to be used
        }
        action_history.append(round_data)
        
        # Use the response as the action for the environment
        done, step_info = env.step(action=response)
        round_num += 1

    rewards, game_info = env.close()
    
    return rewards, game_info, model_assignment, action_history


def get_model_pair_key(model_pair):
    """Create a standardized key for a model pair (order-independent)"""
    return tuple(sorted(model_pair))


def track_progress_by_pairs(game_list, games_per_pair):
    """Create progress tracking structure by model pairs"""
    pair_progress = defaultdict(int)
    pair_total = defaultdict(int)
    
    # Count total games per pair
    for model_pair in game_list:
        pair_key = get_model_pair_key(model_pair)
        pair_total[pair_key] += 1
    
    return pair_progress, pair_total


def calculate_statistics_with_pairwise(all_results, enable_elo=False):
    """Calculate win rates, invalid move statistics, pairwise win rates, and optionally Elo ratings"""
    player_wins = {0: 0, 1: 0}
    draws = 0
    invalid_moves = {0: {'true': 0, 'false': 0}, 1: {'true': 0, 'false': 0}}
    
    # Dynamically detect models from actual game results
    all_models = set()
    for rewards, game_info, model_assignment, _ in all_results:
        all_models.update(model_assignment.values())
    
    # Initialize model tracking with detected models
    model_wins = {model: 0 for model in all_models}
    model_games = {model: 0 for model in all_models}
    model_losses = {model: 0 for model in all_models}
    model_ties = {model: 0 for model in all_models}
    
    # Initialize pairwise tracking
    pairwise_results = defaultdict(lambda: {'wins': 0, 'losses': 0, 'ties': 0, 'total': 0})
    
    # Initialize Elo ratings if enabled
    elo_ratings = {model: INITIAL_RATING for model in all_models} if enable_elo else {}
    
    total_games = len(all_results)
    
    for game_idx, (rewards, game_info, model_assignment, _) in enumerate(all_results):
        # Count games played by each model
        for player_id in [0, 1]:
            model_games[model_assignment[player_id]] += 1
        
        # Track pairwise results
        model_0 = model_assignment[0]
        model_1 = model_assignment[1]
        pair_key = (model_0, model_1)
        
        # Determine winner based on rewards and update stats
        if rewards[0] > rewards[1]:
            player_wins[0] += 1
            model_wins[model_0] += 1
            model_losses[model_1] += 1
            pairwise_results[pair_key]['wins'] += 1
            pairwise_results[(model_1, model_0)]['losses'] += 1
        elif rewards[1] > rewards[0]:
            player_wins[1] += 1
            model_wins[model_1] += 1
            model_losses[model_0] += 1
            pairwise_results[pair_key]['losses'] += 1
            pairwise_results[(model_1, model_0)]['wins'] += 1
        else:
            draws += 1
            model_ties[model_0] += 1
            model_ties[model_1] += 1
            pairwise_results[pair_key]['ties'] += 1
            pairwise_results[(model_1, model_0)]['ties'] += 1
        
        pairwise_results[pair_key]['total'] += 1
        pairwise_results[(model_1, model_0)]['total'] += 1
        
        # Update Elo ratings if enabled
        if enable_elo:
            game_result = determine_game_result(rewards)
            game_result_str = {str(k): v for k, v in game_result.items()}
            model_assignment_str = {str(k): v for k, v in model_assignment.items()}
            elo_ratings = process_game_elo(model_assignment_str, game_result_str, elo_ratings)
        
        # Count invalid moves
        for player_id in [0, 1]:
            if game_info[player_id]['invalid_move']:
                invalid_moves[player_id]['true'] += 1
            else:
                invalid_moves[player_id]['false'] += 1
    
    # Calculate win rates
    win_rate_p0 = player_wins[0] / total_games if total_games > 0 else 0
    win_rate_p1 = player_wins[1] / total_games if total_games > 0 else 0
    draw_rate = draws / total_games if total_games > 0 else 0
    
    # Calculate model win rates
    model_win_rates = {}
    for model in model_wins:
        if model_games[model] > 0:
            model_win_rates[model] = model_wins[model] / model_games[model]
        else:
            model_win_rates[model] = 0
    
    # Calculate pairwise win rates
    pairwise_win_rates = {}
    for pair, results in pairwise_results.items():
        if results['total'] > 0:
            pairwise_win_rates[pair] = results['wins'] / results['total']
    
    result = {
        'total_games': total_games,
        'player_wins': player_wins,
        'draws': draws,
        'win_rates': {0: win_rate_p0, 1: win_rate_p1},
        'draw_rate': draw_rate,
        'invalid_moves': invalid_moves,
        'model_wins': model_wins,
        'model_losses': model_losses,
        'model_ties': model_ties,
        'model_games': model_games,
        'model_win_rates': model_win_rates,
        'pairwise_results': dict(pairwise_results),
        'pairwise_win_rates': pairwise_win_rates
    }
    
    if enable_elo:
        result['elo_ratings'] = elo_ratings
    
    return result


def log_to_wandb(stats, env_id, games_per_pair, model_config, prompt_template, wandb_run_name, folder_path, game_list):
    """Log comprehensive statistics to wandb"""
    # Log summary metrics
    wandb.log({
        "summary/total_games": stats['total_games'],
        "summary/draw_rate": stats['draw_rate'],
        "summary/env_id": env_id,
        "summary/games_per_pair": games_per_pair,
        "summary/prompt_template": prompt_template,
    })
    
    # Log model performance
    for model, win_rate in stats['model_win_rates'].items():
        model_short = model.split('/')[-1]
        wandb.log({
            f"model/{model_short}/win_rate": win_rate,
            f"model/{model_short}/wins": stats['model_wins'][model],
            f"model/{model_short}/losses": stats['model_losses'][model],
            f"model/{model_short}/ties": stats['model_ties'][model],
            f"model/{model_short}/games": stats['model_games'][model],
        })
        
        if 'elo_ratings' in stats:
            wandb.log({f"model/{model_short}/elo": stats['elo_ratings'][model]})
    
    # Log pairwise results
    logged_pairs = set()
    for (model1, model2), results in stats['pairwise_results'].items():
        pair_key = tuple(sorted([model1, model2]))
        if pair_key not in logged_pairs and results['total'] > 0:
            logged_pairs.add(pair_key)
            model1_short = model1.split('/')[-1]
            model2_short = model2.split('/')[-1]
            
            # Get results from model1's perspective
            m1_results = stats['pairwise_results'][(model1, model2)]
            m1_win_rate = m1_results['wins'] / m1_results['total'] if m1_results['total'] > 0 else 0
            
            wandb.log({
                f"pairwise/{model1_short}_vs_{model2_short}/games": m1_results['total'],
                f"pairwise/{model1_short}_vs_{model2_short}/{model1_short}_win_rate": m1_win_rate,
                f"pairwise/{model1_short}_vs_{model2_short}/ties": m1_results['ties'],
            })
    
    # Create and log a summary table
    if 'elo_ratings' in stats:
        table_data = []
        columns = ["Run Name", "Model", "Elo", "Win Rate", "Wins", "Losses", "Ties", "Games"]
        
        for model in sorted(stats['model_wins'].keys(), key=lambda m: stats['elo_ratings'][m], reverse=True):
            model_short = model.split('/')[-1]
            table_data.append([
                wandb_run_name,
                model_short,
                stats['elo_ratings'][model],
                stats['model_win_rates'][model],
                stats['model_wins'][model],
                stats['model_losses'][model],
                stats['model_ties'][model],
                stats['model_games'][model]
            ])
        
        # Save leaderboard to local JSON file
        if folder_path:
            save_leaderboard_json(
                folder_path, env_id, games_per_pair, model_config, 
                prompt_template, wandb_run_name, table_data, columns, stats
            )
        
        table = wandb.Table(columns=columns, data=table_data)
        wandb.log({"leaderboard": table})
        # Also add to summary for easy access
        wandb.summary["leaderboard"] = table


def run_games_for_prompt_template(
    prompt_template, models_to_use, game_list, num_pairs, args, model_config_name
):
    """Run games for a single prompt template and return results"""
    
    # Create run name for this specific prompt template
    wandb_run_name = f"{args.env_id}_{args.games_per_pair}x_{model_config_name}_{prompt_template}"
    
    # Initialize wandb if not disabled
    if not args.disable_wandb:
        wandb.init(
            project="textarena-tournament",
            name=wandb_run_name,
            config={
                "env_id": args.env_id,
                "games_per_pair": args.games_per_pair,
                "model_config": model_config_name,
                "prompt_template": prompt_template,
                "models": models_to_use,
                "total_games": len(game_list),
                "unique_pairs": num_pairs,
                "enable_elo": True
            }
        )
    
    # Create folder for JSON logs if not disabled
    if not args.disable_json:
        run_folder = create_run_folder(args.env_id, args.games_per_pair, model_config_name, prompt_template)
        print(f"Saving game logs to: {run_folder}")
    else:
        run_folder = None
    
    # Optimize number of processes
    optimal_processes = min(args.num_processes, len(game_list))
    
    print(f"Environment: {args.env_id}")
    print(f"Prompt Template: {prompt_template}")
    print(f"Models: {', '.join(models_to_use)}")
    print(f"Unique pairs: {num_pairs}")
    print(f"Games per pair: {args.games_per_pair}")
    print(f"Total games: {len(game_list)}")
    print(f"Running with {optimal_processes} processes...")
    print("Elo rating calculations: ENABLED")
    if args.disable_wandb:
        print("Wandb logging: DISABLED")
    if args.disable_json:
        print("JSON action logging: DISABLED")
    print()
    
    # Set up progress tracking
    pair_progress, pair_total = track_progress_by_pairs(game_list, args.games_per_pair)
    
    # Prepare game arguments with additional parameters
    game_args = [(model_pair, args.env_id, prompt_template, idx+1) 
                 for idx, model_pair in enumerate(game_list)]
    
    # Run games in parallel with progress tracking
    all_results = []
    
    with multiprocessing.Pool(processes=optimal_processes) as pool:
        # Use imap_unordered for better parallel processing and real-time updates
        with tqdm(total=len(game_list), desc=f"Running games ({prompt_template})", unit="game") as pbar:
            game_count = 0
            
            # Process results as they complete
            for result in pool.imap_unordered(run_single_game_with_logging, game_args):
                rewards, game_info, model_assignment, action_history = result
                all_results.append((rewards, game_info, model_assignment, action_history))
                game_count += 1
                
                # Save to JSON if not disabled
                if not args.disable_json:
                    save_game_json(
                        run_folder, 
                        game_count, 
                        args.env_id, 
                        prompt_template,
                        model_assignment, 
                        action_history, 
                        rewards, 
                        game_info
                    )
                
                # Update pair progress tracking
                model_pair = [model_assignment[0], model_assignment[1]]
                pair_key = get_model_pair_key(model_pair)
                pair_progress[pair_key] += 1
                
                # Update progress bar
                model1_short = pair_key[0].split('/')[-1]
                model2_short = pair_key[1].split('/')[-1]
                progress = pair_progress[pair_key]
                total_for_pair = pair_total[pair_key]
                
                # Count completed pairs
                completed_pairs = sum(1 for pk in pair_total.keys() if pair_progress[pk] == pair_total[pk])
                total_pairs = len(pair_total)
                
                pbar.set_postfix({
                    'Just Completed': f"{model1_short} vs {model2_short} ({progress}/{total_for_pair})",
                    'Pairs Done': f"{completed_pairs}/{total_pairs}"
                })
                pbar.update(1)
                
                # Log intermediate results to wandb
                if not args.disable_wandb and game_count % max(1, len(game_list) // 10) == 0:
                    wandb.log({"progress/games_completed": game_count})
    
    # Calculate and display statistics
    stats = calculate_statistics_with_pairwise(all_results, enable_elo=True)
    
    # Create leaderboard data (even if JSON logging is disabled, we need it for analysis)
    table_data = []
    columns = ["Run Name", "Model", "Elo", "Win Rate", "Wins", "Losses", "Ties", "Games"]
    leaderboard_data = None
    
    if 'elo_ratings' in stats:
        for model in sorted(stats['model_wins'].keys(), key=lambda m: stats['elo_ratings'][m], reverse=True):
            model_short = model.split('/')[-1]
            table_data.append([
                wandb_run_name,
                model_short,
                stats['elo_ratings'][model],
                stats['model_win_rates'][model],
                stats['model_wins'][model],
                stats['model_losses'][model],
                stats['model_ties'][model],
                stats['model_games'][model]
            ])
        
        # Create leaderboard data object for analysis
        leaderboard_data = {
            "run_name": wandb_run_name,
            "environment": args.env_id,
            "games_per_pair": args.games_per_pair,
            "model_config": model_config_name,
            "prompt_template": prompt_template,
            "columns": columns,
            "table_data": table_data,
            "summary_stats": {
                "total_games": stats['total_games'],
                "draw_rate": stats['draw_rate'],
                "unique_pairs": len(stats['model_wins']) * (len(stats['model_wins']) - 1) // 2,
                "models": list(stats['model_wins'].keys())
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Save to JSON file if not disabled
        if not args.disable_json:
            save_leaderboard_json(
                run_folder, args.env_id, args.games_per_pair, model_config_name, 
                prompt_template, wandb_run_name, table_data, columns, stats
            )
    
    # Log to wandb if not disabled
    if not args.disable_wandb:
        # Pass folder_path if JSON logging is enabled, otherwise None
        folder_for_leaderboard = run_folder if not args.disable_json else None
        log_to_wandb(stats, args.env_id, args.games_per_pair, model_config_name, prompt_template, wandb_run_name, folder_for_leaderboard, game_list)
    
    # Print results
    print("\n" + "="*60)
    print(f"RESULTS FOR PROMPT TEMPLATE: {prompt_template}")
    print("="*60)
    print("\nMODEL PERFORMANCE STATISTICS:")
    print("-" * 50)
    
    # Sort models by Elo rating
    if 'elo_ratings' in stats:
        sorted_models = sorted(stats['model_wins'].keys(), key=lambda m: stats['elo_ratings'][m], reverse=True)
    else:
        sorted_models = sorted(stats['model_wins'].keys(), key=lambda m: stats['model_win_rates'][m], reverse=True)
    
    for model in sorted_models:
        short_name = model.split('/')[-1]
        win_rate = stats['model_win_rates'][model]
        wins = stats['model_wins'][model]
        losses = stats['model_losses'][model]
        ties = stats['model_ties'][model]
        games = stats['model_games'][model]
        
        print(f"{short_name}:")
        print(f"  Record: {wins}W-{losses}L-{ties}T ({games} games)")
        print(f"  Win Rate: {win_rate:.2%}")
        
        if 'elo_ratings' in stats:
            elo_rating = stats['elo_ratings'][model]
            print(f"  Elo Rating: {elo_rating:.1f}")
        print()
    
    if 'elo_ratings' in stats:
        print("ELO RANKINGS:")
        print("-" * 30)
        elo_sorted = sorted(stats['elo_ratings'].items(), key=lambda x: x[1], reverse=True)
        for rank, (model, rating) in enumerate(elo_sorted, 1):
            short_name = model.split('/')[-1]
            print(f"{rank}. {short_name}: {rating:.1f}")
        print()
    
    # Print pairwise results
    print("PAIRWISE WIN RATES:")
    print("-" * 40)
    logged_pairs = set()
    for (model1, model2), results in stats['pairwise_results'].items():
        pair_key = tuple(sorted([model1, model2]))
        if pair_key not in logged_pairs and results['total'] > 0:
            logged_pairs.add(pair_key)
            m1_short = model1.split('/')[-1]
            m2_short = model2.split('/')[-1]
            
            m1_results = stats['pairwise_results'][(model1, model2)]
            m2_results = stats['pairwise_results'][(model2, model1)]
            
            m1_win_rate = m1_results['wins'] / m1_results['total'] if m1_results['total'] > 0 else 0
            m2_win_rate = m2_results['wins'] / m2_results['total'] if m2_results['total'] > 0 else 0
            
            print(f"{m1_short} vs {m2_short}:")
            print(f"  {m1_short}: {m1_win_rate:.2%} win rate")
            print(f"  {m2_short}: {m2_win_rate:.2%} win rate")
            print(f"  Games: {m1_results['total']}, Ties: {m1_results['ties']}")
    
    if not args.disable_json:
        print(f"\nGame logs saved to: {run_folder}")
        print(f"  Raw game data: {run_folder / 'raw'}")
        print(f"  Leaderboard data: {run_folder / 'leaderboard'}")
        print(f"  Analysis folder: {run_folder / 'analysis'}")
    
    # Close wandb run for this template
    if not args.disable_wandb:
        wandb.finish()
    
    return stats, run_folder if not args.disable_json else None, leaderboard_data


def main():
    parser = argparse.ArgumentParser(description="Run balanced TextArena games with comprehensive logging")
    parser.add_argument("-n", "--games_per_pair", type=int, default=1, 
                       help="Number of games to play between each pair of models")
    parser.add_argument("--num_processes", type=int, default=multiprocessing.cpu_count(), 
                       help="Number of processes to use")
    parser.add_argument("--models", nargs='+', 
                       default=["openai/gpt-4o-mini", "qwen/qwen-2.5-7b-instruct"],
                       help="List of models to use in games")
    parser.add_argument("--model_config", type=str, 
                       help="Load models from a predefined config")
    parser.add_argument("--env_id", type=str, default="SimpleNegotiation-v0",
                       help="Environment ID to use (e.g., TicTacToe-v0, SimpleNegotiation-v0)")
    parser.add_argument("--prompt_template", type=str, default="basic",
                       help="Prompt template name for logging (e.g., basic, detailed, cot)")
    parser.add_argument("--prompt_template_list", nargs='+', 
                       help="List of prompt templates to run separately (mutually exclusive with --prompt_template)")
    parser.add_argument("--list_configs", action="store_true",
                       help="List all available model configurations and exit")

    parser.add_argument("--disable_wandb", action="store_true",
                       help="Disable wandb logging")
    parser.add_argument("--disable_json", action="store_true",
                       help="Disable JSON action logging")
    
    args = parser.parse_args()
    
    # Validate mutually exclusive arguments
    if args.prompt_template_list is not None and args.prompt_template != "basic":
        parser.error("--prompt_template and --prompt_template_list cannot be used together")
    
    # Handle list configurations command
    if args.list_configs:
        try:
            import model_configs
            configs = [attr for attr in dir(model_configs) if not attr.startswith('_') and attr.isupper()]
            
            print("Available Model Configurations:")
            print("=" * 60)
            
            for config_name in sorted(configs):
                models = getattr(model_configs, config_name)
                num_pairs = len(models) * (len(models) - 1) // 2
                
                print(f"\n{config_name}:")
                print(f"  Models: {len(models)}")
                print(f"  Unique pairs: {num_pairs}")
                print(f"  Sample models: {', '.join(models[:2])}{'...' if len(models) > 2 else ''}")
                
                # Show game counts for common -n values
                for n in [1, 3, 5]:
                    total = num_pairs * n
                    print(f"  With -n {n}: {total} total games")
            
            print(f"\nUsage examples:")
            print(f"  python test_tic_enhanced.py -n 3 --model_config QUICK_TEST --enable_elo")
            print(f"  python test_tic_enhanced.py -n 5 --model_config MEDIUM_BENCHMARK --env_id TicTacToe-v0")
            
        except ImportError:
            print("Error: model_configs.py not found")
        return
    
    # Handle model configuration
    models_to_use = args.models
    model_config_name = "custom"
    if args.model_config:
        try:
            import model_configs
            config_models = getattr(model_configs, args.model_config)
            models_to_use = config_models
            model_config_name = args.model_config
            print(f"Using model config: {args.model_config}")
        except ImportError:
            print("Warning: model_configs.py not found, using --models instead")
        except AttributeError:
            print(f"Warning: Config '{args.model_config}' not found in model_configs.py, using --models instead")
    
    # Determine prompt templates to run
    if args.prompt_template_list is not None:
        prompt_templates = args.prompt_template_list
        print(f"Running with multiple prompt templates: {prompt_templates}")
    else:
        prompt_templates = [args.prompt_template]
        print(f"Running with single prompt template: {args.prompt_template}")
    
    # Generate balanced game list
    try:
        game_list, num_pairs = generate_balanced_game_list(models_to_use, args.games_per_pair)
        total_games = len(game_list)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Run games for each prompt template
    all_template_results = []
    all_run_folders = []
    all_leaderboard_data = []
    main_run_folder = None
    
    # Create main run folder for multiple templates
    if len(prompt_templates) > 1:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        main_folder_name = f"multi_template_run_{timestamp}_{args.env_id}_{args.games_per_pair}games_{model_config_name}"
        main_run_folder = Path("game_logs") / main_folder_name
        main_run_folder.mkdir(parents=True, exist_ok=True)
        (main_run_folder / "analysis").mkdir(exist_ok=True)
    
    print(f"Running {len(prompt_templates)} prompt template(s) with {total_games} games each")
    print(f"Total games across all templates: {len(prompt_templates) * total_games}")
    print("="*80)
    
    for template_idx, prompt_template in enumerate(prompt_templates, 1):
        print(f"\n{'='*20} PROMPT TEMPLATE {template_idx}/{len(prompt_templates)}: {prompt_template} {'='*20}")
        
        # Run games for this prompt template
        stats, run_folder, leaderboard_data = run_games_for_prompt_template(
            prompt_template, models_to_use, game_list, num_pairs, args, model_config_name
        )
        
        # Store results for potential aggregation
        all_template_results.append((prompt_template, stats))
        if run_folder:
            all_run_folders.append(run_folder)
        if leaderboard_data:
            all_leaderboard_data.append(leaderboard_data)
    
    # Summary across all prompt templates
    if len(prompt_templates) > 1:
        print("\n" + "="*80)
        print("SUMMARY ACROSS ALL PROMPT TEMPLATES")
        print("="*80)
        
        for template_idx, (template, stats) in enumerate(all_template_results, 1):
            print(f"\n{template_idx}. PROMPT TEMPLATE: {template}")
            print("-" * 50)
            
            # Show top 3 models by Elo for this template
            if 'elo_ratings' in stats:
                elo_sorted = sorted(stats['elo_ratings'].items(), key=lambda x: x[1], reverse=True)
                print("Top 3 models by Elo:")
                for rank, (model, rating) in enumerate(elo_sorted[:3], 1):
                    short_name = model.split('/')[-1]
                    win_rate = stats['model_win_rates'][model]
                    print(f"  {rank}. {short_name}: {rating:.1f} Elo ({win_rate:.1%} win rate)")
            
            print(f"Draw rate: {stats['draw_rate']:.2%}")
            print(f"Total games: {stats['total_games']}")
        
        if all_run_folders:
            print(f"\nAll game logs saved to respective folders:")
            for folder in all_run_folders:
                print(f"  - {folder}")
        
        # Run cross-template analysis
        if main_run_folder and all_leaderboard_data:
            run_cross_template_analysis(
                all_leaderboard_data, main_run_folder, args.env_id, 
                args.games_per_pair, model_config_name
            )
            print(f"\nMain run folder with analysis: {main_run_folder}")
    else:
        # For single template, the results were already printed by run_games_for_prompt_template
        if all_run_folders:
            print(f"\nGame logs saved to: {all_run_folders[0]}")


if __name__ == "__main__":
    main()
