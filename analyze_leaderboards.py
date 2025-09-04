#!/usr/bin/env python3
"""
Analyze multiple TextArena leaderboard JSON files to compute cross-run statistics.

This script reads multiple leaderboard JSON files from tournament runs and computes:
1. Mean and standard deviation of Elo ratings and win rates for each model
2. Mean and standard deviation of rankings for each model across runs

Usage:
    python analyze_leaderboards.py file1.json file2.json file3.json ...
    python analyze_leaderboards.py game_logs/*/leaderboard*.json
"""

import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict
import sys


def load_leaderboard_data(json_files):
    """
    Load data from multiple leaderboard JSON files.
    
    Returns:
        list: List of dictionaries containing run data
    """
    all_runs = []
    
    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)
        all_runs.append(data)
    
    return all_runs


def extract_model_data(all_runs):
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


def calculate_performance_statistics(model_data):
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


def calculate_ranking_statistics(model_data, all_runs):
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


def save_detailed_results(model_data, output_prefix):
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
    
    detailed_file = f"{output_prefix}_detailed_results.csv"
    detailed_df.to_csv(detailed_file, index=False, float_format='%.4f')


def main():
    parser = argparse.ArgumentParser(
        description="Analyze multiple TextArena leaderboard JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python analyze_leaderboards.py game_logs/run_*/leaderboard*.json
    python analyze_leaderboards.py file1.json file2.json file3.json
    python analyze_leaderboards.py --output results game_logs/*/leaderboard*.json
        """
    )
    
    parser.add_argument('json_files', nargs='+', 
                       help='Path to leaderboard JSON files')
    parser.add_argument('--output', '-o', default='leaderboard_analysis',
                       help='Output prefix for CSV files (default: leaderboard_analysis)')
    parser.add_argument('--min_runs', type=int, default=1,
                       help='Minimum number of runs required for a model to be included')
    
    args = parser.parse_args()
    
    # Load all leaderboard data
    all_runs = load_leaderboard_data(args.json_files)
    
    # Extract model data across runs
    model_data = extract_model_data(all_runs)
    
    # Filter models by minimum runs requirement
    filtered_model_data = {
        model: runs for model, runs in model_data.items() 
        if len(runs) >= args.min_runs
    }
    
    # Calculate performance statistics
    performance_stats = calculate_performance_statistics(filtered_model_data)
    
    # Calculate ranking statistics
    ranking_stats = calculate_ranking_statistics(filtered_model_data, all_runs)
    
    # Save results
    perf_file = f"{args.output}_performance_stats.csv"
    rank_file = f"{args.output}_ranking_stats.csv"
    
    performance_stats.to_csv(perf_file, index=False, float_format='%.4f')
    ranking_stats.to_csv(rank_file, index=False, float_format='%.4f')
    
    # Save detailed per-run results
    save_detailed_results(filtered_model_data, args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
