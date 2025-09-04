# TextArena Tournament Runner - Enhancements

This enhanced version of the TextArena tournament runner adds comprehensive logging capabilities for tracking model performance and game actions.

## Key Features

### 1. Comprehensive Wandb Logging
- **Elo Ratings**: Track model performance with Elo rating system
- **Win Rates**: Overall and pairwise win rates between models
- **Real-time Progress**: Monitor tournament progress in wandb dashboard
- **Leaderboard**: Automatic ranking table with all statistics

### 2. JSON Action Logging
- **Structured Folders**: Each run creates a timestamped folder with run parameters
- **Individual Game Files**: Every game saved to its own JSON file
- **Complete History**: Full observation and action history for each round
- **Raw Model Responses**: Track exactly what each model responded without processing

### 3. Enhanced Configuration
- **Environment Selection**: Support any TextArena environment via `--env_id`
- **Model Configs**: Predefined model sets for easy benchmarking
- **Parallel Processing**: Optimized multiprocessing for faster execution

## Installation

```bash
# Install required dependencies
pip install tqdm wandb textarena

# Set up API keys
export OPENROUTER_API_KEY="your-key-here"

# Optional: Login to wandb for cloud logging
wandb login
```

## Usage Examples

### Basic Usage
```bash
# Run a simple tournament with 2 models
python test_tic_enhanced.py \
    --models 'openai/gpt-4o-mini' 'google/gemini-2.0-flash-exp:free' \
    -n 3 \
    --env_id TicTacToe-v0 \
    --enable_elo
```

### Using Model Configurations
```bash
# Run with predefined model config
python test_tic_enhanced.py \
    --model_config SMALL_BENCHMARK \
    -n 5 \
    --env_id SimpleNegotiation-v0 \
    --enable_elo
```

### List Available Configurations
```bash
python test_tic_enhanced.py --list_configs
```

### Disable Logging (for testing)
```bash
python test_tic_enhanced.py \
    --model_config QUICK_TEST \
    -n 1 \
    --disable_wandb \
    --disable_json
```

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-n, --games_per_pair` | Number of games between each pair | 1 |
| `--num_processes` | Number of parallel processes | CPU count |
| `--models` | List of models to use | See script |
| `--model_config` | Predefined model configuration | None |
| `--env_id` | TextArena environment ID | SimpleNegotiation-v0 |
| `--enable_elo` | Enable Elo rating calculations | False |
| `--disable_wandb` | Disable wandb logging | False |
| `--disable_json` | Disable JSON action logging | False |
| `--list_configs` | List available model configs | False |

## Output Structure

### Wandb Metrics
```
summary/
  - total_games
  - draw_rate
  - env_id
  - games_per_pair

model/{model_name}/
  - win_rate
  - wins
  - losses
  - ties
  - games
  - elo (if enabled)

pairwise/{model1}_vs_{model2}/
  - games
  - {model1}_win_rate
  - ties

leaderboard (table with all statistics)
```

### JSON File Structure
```json
{
  "game_number": 1,
  "environment": "TicTacToe-v0",
  "players": {
    "0": "openai/gpt-4o-mini",
    "1": "google/gemini-2.0-flash-exp:free"
  },
  "rounds": [
    {
      "round": 0,
      "player_id": 0,
      "model": "openai/gpt-4o-mini",
      "observation": "...",
      "response": "..."
    }
  ],
  "final_rewards": [1, -1],
  "game_info": {...},
  "timestamp": "2024-01-01T12:00:00"
}
```

### Folder Structure
```
game_logs/
├── run_20240101_120000_TicTacToe-v0_3games_QUICK_TEST/
│   ├── game_0001_TicTacToe-v0_gpt-4o-mini_vs_gemini-2.0-flash-exp.json
│   ├── game_0002_TicTacToe-v0_qwen-2.5-7b_vs_gpt-4o-mini.json
│   └── ...
```

## Model Configurations

### QUICK_TEST
3 cheap models for rapid testing

### SMALL_BENCHMARK
5 models for small-scale benchmarks

### MEDIUM_BENCHMARK
7 models including various sizes

### LARGE_BENCHMARK
8+ premium models for comprehensive testing

### CHEAP_MODELS
Budget-friendly models only

### PREMIUM_MODELS
Top-tier models comparison

### OPENSOURCE_MODELS
Open source models only

## Performance Tips

1. **Parallel Processing**: Use `--num_processes` to control parallelism
2. **Model Selection**: Start with QUICK_TEST for debugging
3. **Wandb Offline**: Use `wandb offline` for local-only logging
4. **Batch Size**: Higher `-n` values give more reliable statistics

## Troubleshooting

### API Rate Limits
- Reduce `--num_processes` if hitting rate limits
- Use CHEAP_MODELS config for high-volume testing

### Memory Issues
- Disable JSON logging with `--disable_json` for very long tournaments
- Reduce number of parallel processes

### Wandb Issues
- Run `wandb login` first
- Use `--disable_wandb` for offline testing

## Example Analysis Script

```python
import json
from pathlib import Path

# Load all games from a run
run_folder = Path("game_logs/run_20240101_120000_...")
games = []

for json_file in run_folder.glob("*.json"):
    with open(json_file) as f:
        games.append(json.load(f))

# Analyze game lengths
game_lengths = [len(g['rounds']) for g in games]
print(f"Average game length: {sum(game_lengths)/len(game_lengths):.1f} rounds")

# Extract all actions by model
model_actions = {}
for game in games:
    for round_data in game['rounds']:
        model = round_data['model']
        if model not in model_actions:
            model_actions[model] = []
        model_actions[model].append(round_data['action'])

# Further analysis...
```

## Future Enhancements

Potential improvements for future versions:
- [ ] Multi-environment tournaments
- [ ] Custom agent wrappers beyond OpenRouter
- [ ] Advanced statistical analysis
- [ ] Automated hyperparameter tuning for templates
- [ ] Tournament bracketing system
- [ ] Real-time game visualization
- [ ] Model response caching for efficiency
- [ ] Automated report generation
