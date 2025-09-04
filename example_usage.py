#!/usr/bin/env python3
"""
Example usage of the analyze_leaderboards.py script.
This creates a mock second leaderboard file to demonstrate cross-run analysis.
"""

import json
import tempfile
import subprocess
import os
from pathlib import Path

def create_mock_leaderboard(run_name, output_file):
    """Create a mock leaderboard JSON file for testing"""
    # Create mock data with different Elo ratings and win rates
    mock_data = {
        "run_name": run_name,
        "environment": "SimpleNegotiation-v0",
        "games_per_pair": 10,
        "model_config": "CHEAP_MODELS",
        "prompt_template": "basic",
        "columns": [
            "Run Name",
            "Model", 
            "Elo",
            "Win Rate",
            "Wins",
            "Losses", 
            "Ties",
            "Games"
        ],
        "table_data": [
            [run_name, "deepseek-r1-0528", 1680.5, 0.75, 45, 12, 3, 60],
            [run_name, "grok-3-mini", 1590.2, 0.65, 39, 18, 3, 60],
            [run_name, "gpt-4o-mini", 1420.8, 0.35, 21, 35, 4, 60],
            [run_name, "qwen3-235b-a22b-2507", 1480.3, 0.30, 18, 24, 18, 60],
            [run_name, "kimi-k2", 1450.1, 0.40, 24, 28, 8, 60],
            [run_name, "llama-4-maverick", 1470.9, 0.42, 25, 27, 8, 60],
            [run_name, "gemini-2.5-flash", 1390.2, 0.20, 12, 30, 18, 60]
        ],
        "summary_stats": {
            "total_games": 210,
            "draw_rate": 0.19,
            "unique_pairs": 21,
            "models": [
                "deepseek/deepseek-r1-0528",
                "x-ai/grok-3-mini", 
                "openai/gpt-4o-mini",
                "qwen/qwen3-235b-a22b-2507",
                "moonshotai/kimi-k2",
                "meta-llama/llama-4-maverick",
                "google/gemini-2.5-flash"
            ]
        },
        "timestamp": "2025-08-30T21:00:00.000000"
    }
    
    with open(output_file, 'w') as f:
        json.dump(mock_data, f, indent=2)
    
    print(f"Created mock leaderboard: {output_file}")

def main():
    # Create temporary directory for demo
    temp_dir = Path("temp_demo")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Create a second mock leaderboard file to demonstrate cross-run analysis
        mock_file = temp_dir / "leaderboard_basic.json"
        create_mock_leaderboard("SimpleNegotiation-v0_10x_CHEAP_MODELS_basic", mock_file)
        
        # Find the existing leaderboard file
        existing_files = list(Path("game_logs").glob("*/leaderboard*.json"))
        
        if not existing_files:
            print("No existing leaderboard files found. Please run a tournament first.")
            return
        
        # Use the first existing file and our mock file
        files_to_analyze = [str(existing_files[0]), str(mock_file)]
        
        print(f"\nAnalyzing files:")
        for f in files_to_analyze:
            print(f"  - {f}")
        
        # Run the analysis
        cmd = ["python", "analyze_leaderboards.py", "--output", "demo_results"] + files_to_analyze
        
        print(f"\nRunning command: {' '.join(cmd)}")
        print("=" * 60)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Show generated files
        output_files = [
            "demo_results_performance_stats.csv",
            "demo_results_ranking_stats.csv", 
            "demo_results_detailed_results.csv"
        ]
        
        print("\nGenerated files:")
        for output_file in output_files:
            if os.path.exists(output_file):
                print(f"✓ {output_file}")
                # Show first few lines
                with open(output_file, 'r') as f:
                    lines = f.readlines()[:5]
                    print("  Preview:")
                    for line in lines:
                        print(f"    {line.strip()}")
                    if len(lines) >= 5:
                        print("    ...")
                    print()
            else:
                print(f"✗ {output_file} (not created)")
    
    finally:
        # Clean up temporary files
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
