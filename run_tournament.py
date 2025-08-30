#!/usr/bin/env python3
"""Example script showing how to use model_configs programmatically"""

import model_configs
import subprocess
import sys

def run_tournament(config_name, games_per_pair=3, enable_elo=True):
    """Run a tournament with a specific model configuration"""
    
    # Get the model list from the config
    if not hasattr(model_configs, config_name):
        print(f"Error: Configuration '{config_name}' not found in model_configs.py")
        print(f"Available configs: {[attr for attr in dir(model_configs) if not attr.startswith('_')]}")
        return
    
    models = getattr(model_configs, config_name)
    
    # Calculate tournament size
    num_pairs = len(models) * (len(models) - 1) // 2
    total_games = num_pairs * games_per_pair
    
    print(f"Tournament: {config_name}")
    print(f"Models: {len(models)} models")
    print(f"Pairs: {num_pairs}")
    print(f"Games per pair: {games_per_pair}")
    print(f"Total games: {total_games}")
    print(f"Elo enabled: {enable_elo}")
    print("-" * 50)
    
    # Build command
    cmd = [
        "python", "test_tic.py",
        "-n", str(games_per_pair),
        "--model_config", config_name
    ]
    
    if enable_elo:
        cmd.append("--enable_elo")
    
    # Run the tournament
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Tournament '{config_name}' completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tournament '{config_name}' failed with error code {e.returncode}")
        return False

def main():
    """Run multiple tournaments"""
    
    # List available configurations
    configs = [attr for attr in dir(model_configs) if not attr.startswith('_') and attr.isupper()]
    print("Available model configurations:")
    for config in configs:
        models = getattr(model_configs, config)
        pairs = len(models) * (len(models) - 1) // 2
        print(f"  {config}: {len(models)} models, {pairs} pairs")
    print()
    
    # Run tournaments
    tournaments = [
        ("QUICK_TEST", 5),      # 5 games per pair
        ("MEDIUM_BENCHMARK", 3), # 3 games per pair  
        ("MY_FAVORITES", 10),    # 10 games per pair
    ]
    
    for config_name, games_per_pair in tournaments:
        print(f"\n{'='*60}")
        success = run_tournament(config_name, games_per_pair, enable_elo=True)
        if not success:
            print(f"Stopping due to failure in {config_name}")
            break

if __name__ == "__main__":
    main()

