#!/usr/bin/env python
"""
Test script for the updated draw_jitter.py

This demonstrates how to use the updated drawing code with detailed results CSV files.
"""

import subprocess
import os

# Example usage with different CSV files
examples = [
    {
        "csv": "game_logs/multi_template_run_20250910_224914_KuhnPoker-v0-short_1games_FINAL_MODELS/analysis/cross_template_KuhnPoker-v0-short_1games_FINAL_MODELS_detailed_results.csv",
        "output": "kuhn_poker_jitter.png",
        "description": "Kuhn Poker results with multiple templates"
    }
]

def run_example(csv_path, output_path, description):
    """Run draw_jitter.py with the given parameters"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Input CSV: {csv_path}")
    print(f"Output PNG: {output_path}")
    print(f"{'='*60}")
    
    # Check if CSV exists
    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found: {csv_path}")
        return
    
    # Run the drawing script
    cmd = ["python", "utils/draw_jitter.py", csv_path, "--output", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("SUCCESS! Plot generated successfully.")
        print("\nOutput:")
        print(result.stdout)
    else:
        print("ERROR! Failed to generate plot.")
        print("\nError output:")
        print(result.stderr)

if __name__ == "__main__":
    print("Testing updated draw_jitter.py script")
    print("=====================================")
    
    # Change to TextArena directory
    os.chdir("/teamspace/studios/this_studio/TextArena")
    
    for example in examples:
        run_example(example["csv"], example["output"], example["description"])
    
    print("\n\nAll tests completed!")
    print("\nThe updated draw_jitter.py script accepts:")
    print("  - A detailed results CSV file with columns: Model, Run_Name, Elo, Win_Rate")
    print("  - An optional --output parameter for the output filename")
    print("\nIt will:")
    print("  - Calculate mean and std deviation from the actual data")
    print("  - Plot individual data points with jitter")
    print("  - Show error bars based on actual standard deviation")
    print("  - Handle unknown models gracefully with default colors/icons")
