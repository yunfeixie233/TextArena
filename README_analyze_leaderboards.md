# Leaderboard Analysis Tool

This tool analyzes multiple TextArena leaderboard JSON files to compute comprehensive statistics across different tournament runs.

## Features

1. **Performance Statistics**: Calculate mean and standard deviation of Elo ratings and win rates for each model across runs
2. **Ranking Statistics**: Calculate mean and standard deviation of model rankings across runs
3. **Detailed Results**: Export all per-run data for further analysis
4. **CSV Export**: All results exported in CSV format for easy analysis

## Usage

### Basic Usage
```bash
# Analyze specific files
python analyze_leaderboards.py file1.json file2.json file3.json

# Analyze all leaderboard files in game_logs directories
python analyze_leaderboards.py game_logs/*/leaderboard*.json

# Specify custom output prefix
python analyze_leaderboards.py --output my_analysis game_logs/*/leaderboard*.json

# Only include models that appear in at least 3 runs
python analyze_leaderboards.py --min_runs 3 game_logs/*/leaderboard*.json
```

### Example with Real Data
```bash
# First, run some tournaments with different prompt templates
python test_tic_enhanced.py -n 10 --model_config CHEAP_MODELS --prompt_template basic --env_id SimpleNegotiation-v0
python test_tic_enhanced.py -n 10 --model_config CHEAP_MODELS --prompt_template chain_of_thought --env_id SimpleNegotiation-v0
python test_tic_enhanced.py -n 10 --model_config CHEAP_MODELS --prompt_template tree_of_thoughts --env_id SimpleNegotiation-v0

# Then analyze all results
python analyze_leaderboards.py game_logs/*/leaderboard*.json
```

## Output Files

The script generates three CSV files:

### 1. Performance Statistics (`*_performance_stats.csv`)
Contains aggregated performance metrics for each model:
- `Model`: Model name
- `Num_Runs`: Number of runs the model participated in
- `Mean_Elo`: Average Elo rating across runs
- `Std_Elo`: Standard deviation of Elo ratings
- `Min_Elo`/`Max_Elo`: Range of Elo ratings
- `Mean_Win_Rate`: Average win rate across runs
- `Std_Win_Rate`: Standard deviation of win rates
- `Min_Win_Rate`/`Max_Win_Rate`: Range of win rates

**Sorted by**: Mean Elo (highest to lowest)

### 2. Ranking Statistics (`*_ranking_stats.csv`)
Contains ranking analysis for each model:
- `Model`: Model name
- `Num_Runs`: Number of runs the model participated in
- `Mean_Rank`: Average rank across runs (1 = best)
- `Std_Rank`: Standard deviation of rankings
- `Best_Rank`: Best rank achieved
- `Worst_Rank`: Worst rank achieved
- `Median_Rank`: Median rank across runs

**Sorted by**: Mean rank (best rank first)

### 3. Detailed Results (`*_detailed_results.csv`)
Contains raw per-run data for each model:
- `Model`: Model name
- `Run_Name`: Tournament run identifier
- `Elo`: Elo rating for this specific run
- `Win_Rate`: Win rate for this specific run

## Requirements

```bash
pip install pandas numpy
```

## Input Format

The script expects JSON files in the format produced by `test_tic_enhanced.py`:

```json
{
  "run_name": "SimpleNegotiation-v0_10x_CHEAP_MODELS_basic",
  "environment": "SimpleNegotiation-v0",
  "columns": ["Run Name", "Model", "Elo", "Win Rate", "Wins", "Losses", "Ties", "Games"],
  "table_data": [
    ["run_name", "model_name", elo_rating, win_rate, wins, losses, ties, games],
    ...
  ]
}
```

## Example Output

### Performance Statistics
```
Model,Num_Runs,Mean_Elo,Std_Elo,Mean_Win_Rate,Std_Win_Rate
deepseek-r1-0528,3,1692.8,15.2,0.7533,0.0289
grok-3-mini,3,1603.1,22.4,0.6167,0.0408
...
```

### Ranking Statistics
```
Model,Num_Runs,Mean_Rank,Std_Rank,Best_Rank,Worst_Rank
deepseek-r1-0528,3,1.0,0.0,1,1
grok-3-mini,3,2.0,0.0,2,2
...
```

## Use Cases

1. **Compare Prompt Templates**: Analyze how different prompting strategies affect model performance
2. **Model Benchmarking**: Identify consistently high-performing models across different configurations
3. **Stability Analysis**: Find models with low variance in performance across runs
4. **Statistical Significance**: Use standard deviations to assess confidence in performance differences

## Demo

Run the example script to see the tool in action:

```bash
python example_usage.py
```

This creates a mock dataset and demonstrates the analysis workflow.
