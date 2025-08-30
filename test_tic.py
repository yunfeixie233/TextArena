""" 
A minimal script showing how to run textarena locally with progress tracking.

Requirements:
- pip install tqdm (for progress bars)
"""
import os
import argparse
import multiprocessing
import random
import math
import itertools
from tqdm import tqdm
from collections import defaultdict
os.environ["OPENROUTER_API_KEY"] = "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"
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


def run_single_game(model_pair):
    """Run a single game between a specific pair of models and return rewards, game_info, and model assignment"""
    if not isinstance(model_pair, list) or len(model_pair) != 2:
        raise ValueError(f"Expected exactly 2 models, got: {model_pair}")
    
    # Initialize agents with the two models
    agents = {}
    model_assignment = {}
    for i in range(2):
        agents[i] = ta.agents.OpenRouterAgent(model_name=model_pair[i])
        model_assignment[i] = model_pair[i]

    # Initialize the environment
    # env = ta.make(env_id="UltimatumGame-v0")
    env = ta.make(env_id="SimpleNegotiation-v0")
    # wrap it for additional visualizations
    # env = ta.wrappers.SimpleRenderWrapper(env=env) 

    env.reset(num_players=len(agents))

    done = False
    while not done:
        player_id, observation = env.get_observation()
        action = agents[player_id](observation)
        done, step_info = env.step(action=action)

    rewards, game_info = env.close()
    return rewards, game_info, model_assignment


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


def calculate_statistics(all_results, enable_elo=False):
    """Calculate win rates, invalid move statistics, and optionally Elo ratings from all game results"""
    player_wins = {0: 0, 1: 0}
    draws = 0
    invalid_moves = {0: {'true': 0, 'false': 0}, 1: {'true': 0, 'false': 0}}
    
    # Dynamically detect models from actual game results
    all_models = set()
    for _, _, model_assignment in all_results:
        all_models.update(model_assignment.values())
    
    # Initialize model tracking with detected models
    model_wins = {model: 0 for model in all_models}
    model_games = {model: 0 for model in all_models}
    model_losses = {model: 0 for model in all_models}
    model_ties = {model: 0 for model in all_models}
    
    # Initialize Elo ratings if enabled
    elo_ratings = {model: INITIAL_RATING for model in all_models} if enable_elo else {}
    
    total_games = len(all_results)
    
    for game_idx, (rewards, game_info, model_assignment) in enumerate(all_results):
        # Count games played by each model
        for player_id in [0, 1]:
            model_games[model_assignment[player_id]] += 1
        
        # Determine winner based on rewards and update model stats
        if rewards[0] > rewards[1]:
            player_wins[0] += 1
            model_wins[model_assignment[0]] += 1
            model_losses[model_assignment[1]] += 1
        elif rewards[1] > rewards[0]:
            player_wins[1] += 1
            model_wins[model_assignment[1]] += 1
            model_losses[model_assignment[0]] += 1
        else:
            draws += 1
            model_ties[model_assignment[0]] += 1
            model_ties[model_assignment[1]] += 1
        
        # Update Elo ratings if enabled
        if enable_elo:
            game_result = determine_game_result(rewards)
            # Convert player_id keys to strings for consistency
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
        'model_win_rates': model_win_rates
    }
    
    if enable_elo:
        result['elo_ratings'] = elo_ratings
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Run balanced TextArena games with Elo analysis")
    parser.add_argument("-n", "--games_per_pair", type=int, default=1, 
                       help="Number of games to play between each pair of models (ensures balanced tournament)")
    parser.add_argument("--num_processes", type=int, default=multiprocessing.cpu_count(), 
                       help="Number of processes to use")
    parser.add_argument("--models", nargs='+', 
                       default=["google/gemini-2.5-pro", "qwen/qwen-2.5-7b-instruct"],  # <-- Change this line
                       help="List of models to use in games (space-separated). Example: --models 'model1' 'model2' 'model3'")
    parser.add_argument("--model_config", type=str, 
                       help="Load models from a predefined config (e.g., 'QUICK_TEST', 'MEDIUM_BENCHMARK')")
    parser.add_argument("--list_configs", action="store_true",
                       help="List all available model configurations and exit")
    parser.add_argument("--enable_elo", action="store_true", 
                       help="Enable Elo rating calculations and tracking")
    
    args = parser.parse_args()
    
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
            print(f"  python test_tic.py -n 3 --model_config QUICK_TEST --enable_elo")
            print(f"  python test_tic.py -n 5 --model_config MEDIUM_BENCHMARK --enable_elo")
            
        except ImportError:
            print("Error: model_configs.py not found")
        return
    
    # Handle model configuration
    models_to_use = args.models
    if args.model_config:
        try:
            import model_configs
            config_models = getattr(model_configs, args.model_config)
            models_to_use = config_models
            print(f"Using model config: {args.model_config}")
        except ImportError:
            print("Warning: model_configs.py not found, using --models instead")
        except AttributeError:
            print(f"Warning: Config '{args.model_config}' not found in model_configs.py, using --models instead")
    
    # Generate balanced game list
    try:
        game_list, num_pairs = generate_balanced_game_list(models_to_use, args.games_per_pair)
        total_games = len(game_list)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Optimize number of processes: don't use more processes than games
    optimal_processes = min(args.num_processes, total_games)
    
    print(f"Models: {', '.join(models_to_use)}")
    print(f"Unique pairs: {num_pairs}")
    print(f"Games per pair: {args.games_per_pair}")
    print(f"Total games: {total_games}")
    print(f"Running with {optimal_processes} processes...")
    if args.enable_elo:
        print("Elo rating calculations: ENABLED")
    if optimal_processes < args.num_processes:
        print(f"Note: Reduced processes from {args.num_processes} to {optimal_processes} (no need for more processes than games)")
    print()
    
    # Set up progress tracking
    pair_progress, pair_total = track_progress_by_pairs(game_list, args.games_per_pair)
    
    print("Initial model pairs setup:")
    print("=" * 60)
    for pair_key, total in sorted(pair_total.items()):
        model1_short = pair_key[0].split('/')[-1]
        model2_short = pair_key[1].split('/')[-1]
        print(f"  ○ {model1_short:15} vs {model2_short:15} [░░░░░░░░░░░░░░░░░░░░]  0/{total} (  0.0%)")
    print("=" * 60)
    print(f"Total: {len(pair_total)} unique pairs, {total_games} total games")
    print()
    
    # Run games in parallel with progress tracking
    all_results = []
    
    with multiprocessing.Pool(processes=optimal_processes) as pool:
        # Use imap_unordered for better parallel processing and real-time updates
        with tqdm(total=total_games, desc="Running games", unit="game") as pbar:
            game_count = 0
            
            # Process results as they complete (unordered for better parallelism)
            for result in pool.imap_unordered(run_single_game, game_list):
                all_results.append(result)
                game_count += 1
                
                # Update pair progress tracking
                _, _, model_assignment = result
                model_pair = [model_assignment[0], model_assignment[1]]
                pair_key = get_model_pair_key(model_pair)
                pair_progress[pair_key] += 1
                
                # Update progress bar with current pair info and overall summary
                model1_short = pair_key[0].split('/')[-1]
                model2_short = pair_key[1].split('/')[-1]
                progress = pair_progress[pair_key]
                total_for_pair = pair_total[pair_key]
                
                # Count completed pairs for summary
                completed_pairs = sum(1 for pk in pair_total.keys() if pair_progress[pk] == pair_total[pk])
                total_pairs = len(pair_total)
                
                # Update the progress bar with detailed info
                pbar.set_postfix({
                    'Just Completed': f"{model1_short} vs {model2_short} ({progress}/{total_for_pair})",
                    'Pairs Done': f"{completed_pairs}/{total_pairs}"
                })
                pbar.update(1)
                
                # Print periodic detailed updates
                if game_count % max(1, total_games // 10) == 0 or game_count == total_games:
                    pbar.write(f"\n--- Progress Update (Game {game_count}/{total_games}) ---")
                    for pk in sorted(pair_total.keys()):
                        m1_short = pk[0].split('/')[-1][:12]
                        m2_short = pk[1].split('/')[-1][:12] 
                        curr = pair_progress[pk]
                        tot = pair_total[pk]
                        status = "✓" if curr == tot else f"{curr}/{tot}"
                        pbar.write(f"  {m1_short} vs {m2_short}: {status}")
                    pbar.write("") # Empty line for spacing
    
    # Show final progress summary
    print("\nFinal progress summary:")
    for pair_key, total in sorted(pair_total.items()):
        model1_short = pair_key[0].split('/')[-1]
        model2_short = pair_key[1].split('/')[-1]
        completed = pair_progress[pair_key]
        print(f"  {model1_short} vs {model2_short}: {completed}/{total} games ✓")
    
    # Calculate and display statistics
    stats = calculate_statistics(all_results, enable_elo=args.enable_elo)
    
    print("\n" + "="*60)
    print("BALANCED TOURNAMENT RESULTS")
    print("="*60)
    print(f"Total Games: {stats['total_games']} ({args.games_per_pair} per pair)")
    print(f"Unique Pairs: {num_pairs}")
    print(f"Player 0 Wins: {stats['player_wins'][0]} (Win Rate: {stats['win_rates'][0]:.2%})")
    print(f"Player 1 Wins: {stats['player_wins'][1]} (Win Rate: {stats['win_rates'][1]:.2%})")
    print(f"Draws: {stats['draws']} (Draw Rate: {stats['draw_rate']:.2%})")
    
    print("\nMODEL PERFORMANCE STATISTICS:")
    print("-" * 50)
    
    # Sort models by win rate for better display (or by Elo if available)
    if args.enable_elo and 'elo_ratings' in stats:
        sorted_models = sorted(stats['model_wins'].keys(), key=lambda m: stats['elo_ratings'][m], reverse=True)
    else:
        sorted_models = sorted(stats['model_wins'].keys(), key=lambda m: stats['model_win_rates'][m], reverse=True)
    
    for model in sorted_models:
        short_name = model.split('/')[-1]  # Get just the model name without provider
        win_rate = stats['model_win_rates'][model]
        wins = stats['model_wins'][model]
        losses = stats['model_losses'][model]
        ties = stats['model_ties'][model]
        games = stats['model_games'][model]
        
        print(f"{short_name}:")
        print(f"  Record: {wins}W-{losses}L-{ties}T ({games} games)")
        print(f"  Win Rate: {win_rate:.2%}")
        
        if args.enable_elo and 'elo_ratings' in stats:
            elo_rating = stats['elo_ratings'][model]
            print(f"  Elo Rating: {elo_rating:.1f}")
        print()
    
    if args.enable_elo and 'elo_ratings' in stats:
        print("ELO RANKINGS:")
        print("-" * 30)
        elo_sorted = sorted(stats['elo_ratings'].items(), key=lambda x: x[1], reverse=True)
        for rank, (model, rating) in enumerate(elo_sorted, 1):
            short_name = model.split('/')[-1]
            print(f"{rank}. {short_name}: {rating:.1f}")
        print()
    
    print("\nINVALID MOVE STATISTICS:")
    print("-" * 25)
    for player_id in [0, 1]:
        print(f"Player {player_id}:")
        print(f"  Invalid moves (True): {stats['invalid_moves'][player_id]['true']}")
        print(f"  Valid moves (False): {stats['invalid_moves'][player_id]['false']}")
    
    # Print sample of individual game results
    print(f"\nSAMPLE RESULTS (first 3 games):")
    print("-" * 35)
    for i, (rewards, game_info, model_assignment) in enumerate(all_results[:3]):
        model_0_short = model_assignment[0].split('/')[-1]
        model_1_short = model_assignment[1].split('/')[-1]
        print(f"Game {i+1}: {model_0_short} vs {model_1_short}")
        print(f"  Rewards: {rewards}")
        
        # Determine winner for display
        if rewards[0] > rewards[1]:
            winner = model_0_short
        elif rewards[1] > rewards[0]:
            winner = model_1_short
        else:
            winner = "Draw"
        print(f"  Winner: {winner}")
        print(f"  Game Info: {game_info}")
        print()


if __name__ == "__main__":
    main()