#!/usr/bin/env python3
"""
Example script demonstrating how to use the enhanced TextArena runner
with wandb logging and JSON action tracking.
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and print output"""
    print(f"\nRunning: {cmd}")
    print("-" * 60)
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode

def main():
    print("="*60)
    print("TextArena Enhanced Runner - Example Usage")
    print("="*60)
    
    # Example 1: List available model configurations
    print("\n1. Listing available model configurations:")
    run_command("python test_tic_enhanced.py --list_configs")
    
    # Example 2: Quick test with minimal models
    print("\n2. Quick test with 2 models, 1 game each:")
    cmd = """python test_tic_enhanced.py \
        --models 'openai/gpt-4o-mini' 'google/gemini-2.0-flash-exp:free' \
        -n 1 \
        --env_id TicTacToe-v0 \
        --prompt_template basic \
        --disable_wandb"""
    run_command(cmd)
    
    # Example 3: Using model config
    print("\n3. Using QUICK_TEST config:")
    cmd = """python test_tic_enhanced.py \
        --model_config QUICK_TEST \
        -n 2 \
        --env_id SimpleNegotiation-v0 \
        --prompt_template cot \
        --disable_wandb"""
    run_command(cmd)
    
    # Example 4: Full tournament with wandb logging (commented out by default)
    print("\n4. Full tournament with wandb logging (example command):")
    print("""
    python test_tic_enhanced.py \\
        --model_config SMALL_BENCHMARK \\
        -n 3 \\
        --env_id UltimatumGame-v0 \\
        --prompt_template strategy \\
        --num_processes 4
    """)
    
    print("\n" + "="*60)
    print("Key Features Demonstrated:")
    print("="*60)
    print("""
    1. Wandb Logging:
       - Comprehensive game statistics
       - Model win rates and Elo ratings
       - Pairwise matchup results
       - Real-time progress tracking
       
    2. JSON Action Logging:
       - Each run creates a timestamped folder
       - Every game saved to individual JSON file
       - Complete action history with observations
       - Raw model responses tracked per round
       
    3. Environment Support:
       - TicTacToe-v0
       - SimpleNegotiation-v0
       - UltimatumGame-v0
       - And all other TextArena environments
       
    4. Model Configurations:
       - QUICK_TEST: 3 cheap models for testing
       - SMALL_BENCHMARK: 5 models
       - MEDIUM_BENCHMARK: 7 models
       - LARGE_BENCHMARK: 8+ premium models
       - Custom model lists via --models
    """)
    
    print("\nCheck the 'game_logs/' folder for detailed JSON action logs!")
    print("Use 'wandb login' first if you want to enable wandb tracking.")

if __name__ == "__main__":
    main()
