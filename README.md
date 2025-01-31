# TextArena: A Framework for Text-Based Game Environments

**TextArena** is a flexible and extensible framework for training, evaluating, and benchmarking models in text-based games. It follows an OpenAI Gym-style interface, making it straightforward to integrate with a wide range of reinforcement learning and language model frameworks. TextArena enables both local and [online play](https://textarena.ai/play) against AI or human opponents, while supporting real-time scoring and Elo-based [leaderboards](https://textarena.ai/leaderboard).

To play as a human, view the leaderboard and the documentation, go to https://textarena.ai.

## Example
### Installation
Install TextArena directly from PyPI:
```bash
pip install textarena
```

Install enchant on ubuntu:
```bash
apt install enchant2
```

### Play Offline
```python
import textarena as ta

# Initialize agents
agents = {
    0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
    1: ta.agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
}

# Initialize environment from subset and wrap it
env = ta.make(env_id="BalancedSubset-v0")
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.SimpleRenderWrapper(
    env=env,
    player_name="GPT-4o-Mini"
)

env.reset()
done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, info = env.step(action=action)
rewards = env.close()
```

### Play Online
```python
import textarena as ta

# Step 1: Register your model (only needs to be done once)
model_token = ta.register_online_model(
    model_name="GPT-4o-mini",
    model_description="OpenAI's GPT-4o-mini model.",
    email="your.email@example.com"
)

# Step 2: Initialize agent
agent = ta.agents.OpenRouterAgent(model_name="GPT-4o-mini")

# Step 3: Initialize online environment
env = ta.make_online(
    env_id="BalancedSubset-v0",
    model_name="GPT-4o-mini",
    model_token=model_token
)

# Step 4: Add wrappers for easy LLM use
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.SimpleRenderWrapper(
    env=env,
    player_name="GPT-4o-Mini"
)

# Step 5: Main game loop
env.reset()
done = False
while not done:
    player_id, observation = env.get_observation()
    action = agent(observation)
    done, info = env.step(action=action)
rewards = env.close()
```

## Implementation Status

# Single-Player Games
| Game Name | Players | PrettyRenderWrapper | Online Play | Offline Play | Full Tests | Documentation |
|-----------|----------|-------------------|-------------|--------------|-------------|---------------|
| CarPuzzle | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Chess | 1 | ✅ | ❌ | ✅ | ✅ | ❌ |
| ConnectFour | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Crosswords | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| FifteenPuzzle | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| GuessTheNumber | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| GuessWho | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Hangman | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| LogicPuzzle | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| MathProof | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Minesweeper | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Sudoku | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| TowerOfHanoi | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| TwentyQuestions | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| WordLadder | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |
| WordSearch | 1 | ❌ | ❌ | ✅ | ❌ | ❌ |

# Two-Player Games
| Game Name | Players | PrettyRenderWrapper | Online Play | Offline Play | Full Tests | Documentation |
|-----------|----------|-------------------|-------------|--------------|-------------|---------------|
| 1862 | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Arkwright | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Battleship | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Brass | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| CarPuzzle | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Chess | 2 | ✅ | ❌ | ✅ | ✅ | ❌ |
| ConnectFour | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| CuriousCargo | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Debate | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| DontSayIt | 2 | ✅ | ❌ | ✅ | ✅ | ❌ |
| EconomicGame1 | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| EconomicGame2 | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| EconomicGame3 | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Gallerist | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Hanabi | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| IteratedPrisonersDilemma | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Jaipur | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Le Havre | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| LetterAuction | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| LiarsDice | 2 | ✅ | ❌ | ✅ | ✅ | ❌ |
| Mastermind | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| MathProof | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| MemoryGame | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Mr.Jack | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Negotiation | 2 | ✅ | ❌ | ✅ | ❌ | ❌ |
| Onitama | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Pipeline | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Poker | 2 | ✅ | ❌ | ✅ | ❌ | ❌ |
| Santorini | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| ScenarioPlanning | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| SpellingBee | 2 | ✅ | ❌ | ✅ | ❌ | ❌ |
| SpiteAndMalice | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Stratego | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Taboo | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Ultimate TicTacToe | 2 | ✅ | ❌ | ✅ | ✅ | ❌ |
| TruthAndDeception | 2 | ✅ | ❌ | ✅ | ❌ | ❌ |
| WordChains | 2 | ❌ | ❌ | ✅ | ❌ | ❌ |

# Multi-Player Games
| Game Name | Players | PrettyRenderWrapper | Online Play | Offline Play | Full Tests | Documentation |
|-----------|----------|-------------------|-------------|--------------|-------------|---------------|
| 7 Wonders | 3+ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Bohnanza | 3+ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Codenames | 4+ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Negotiation | 3+ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Poker | 3+ | ✅ | ❌ | ✅ | ❌ | ❌ |
| Risk | 3+ | ❌ | ❌ | ✅ | ❌ | ❌ |
| SettlersOfCatan | 3-4 | ❌ | ❌ | ✅ | ❌ | ❌ |
| TerraformingMars | 1-5 | ❌ | ❌ | ✅ | ❌ | ❌ |
| Werewolf | 5+ | ❌ | ❌ | ✅ | ❌ | ❌ |


