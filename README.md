# TextArena: A Framework for Text-Based Game Environments

**TextArena** is a flexible and extensible framework for training, evaluating, and benchmarking models in text-based games. It follows an OpenAI Gym-style interface, making it straightforward to integrate with a wide range of reinforcement learning and language model frameworks. TextArena enables both local and [online play](https://textarena.ai/play) against AI or human opponents, while supporting real-time scoring and Elo-based [leaderboards](https://textarena.ai/leaderboard).

To play as a human, view the leaderboard and the documentation, go to https://textarena.ai.  
To talk to us, leave an issue or join [discord](https://discord.gg/zXPdeu7SqD)

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
| Game Name       | Offline Play | PrettyRenderWrapper | Online Play | Full Tests | Documentation |
|-----------------|--------------|---------------------|-------------|------------|---------------|
| CarPuzzle       | ❌           | ❌                  | ❌          | ❌         |             |
| Chess           | ❌           | ❌                  | ❌          | ❌         |             |
| ConnectFour     | ❌           | ❌                  | ❌          | ❌         |             |
| Crosswords      | ❌           | ❌                  | ❌          | ❌         |             |
| FifteenPuzzle   | ❌           | ❌                  | ❌          | ❌         |             |
| GuessTheNumber  | ❌           | ❌                  | ❌          | ❌         |             |
| GuessWho        | ❌           | ❌                  | ❌          | ❌         |             |
| Hangman         | ❌           | ❌                  | ❌          | ❌         |             |
| LogicPuzzle     | ❌           | ❌                  | ❌          | ❌         |             |
| MathProof       | ❌           | ❌                  | ❌          | ❌         |             |
| Minesweeper     | ❌           | ❌                  | ❌          | ❌         |             |
| Sudoku          | ❌           | ❌                  | ❌          | ❌         |             |
| TowerOfHanoi    | ❌           | ❌                  | ❌          | ❌         |             |
| TwentyQuestions | ❌           | ❌                  | ❌          | ❌         |             |
| WordLadder      | ❌           | ❌                  | ❌          | ❌         |             |
| WordSearch      | ❌           | ❌                  | ❌          | ❌         |             |

# Two-Player Games
| Game Name                | Offline Play | PrettyRenderWrapper | Online Play | Full Tests | Documentation |
|--------------------------|--------------|---------------------|-------------|------------|---------------|
| 1862                     | ❌           | ❌                  | ❌          | ❌         |             |
| Arkwright                | ❌           | ❌                  | ❌          | ❌         |             |
| Battleship               | ❌           | ❌                  | ❌          | ❌         |             |
| Brass                    | ❌           | ❌                  | ❌          | ❌         |             |
| CarPuzzle                | ❌           | ❌                  | ❌          | ❌         |             |
| Chess                    | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/chess)|
| ConnectFour              | ❌           | ❌                  | ❌          | ❌         |             |
| CuriousCargo             | ❌           | ❌                  | ❌          | ❌         |             |
| Debate                   | ❌           | ❌                  | ❌          | ❌         |             |
| DontSayIt                | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/dont-say-it)|
| EconomicGame1            | ❌           | ❌                  | ❌          | ❌         |             |
| EconomicGame2            | ❌           | ❌                  | ❌          | ❌         |             |
| EconomicGame3            | ❌           | ❌                  | ❌          | ❌         |             |
| Gallerist                | ❌           | ❌                  | ❌          | ❌         |             |
| Hanabi                   | ❌           | ❌                  | ❌          | ❌         |             |
| IteratedPrisonersDilemma | ✅           | ❌                  | ❌          | ✅         |             |
| Jaipur                   | ❌           | ❌                  | ❌          | ❌         |             |
| Le Havre                 | ❌           | ❌                  | ❌          | ❌         |             |
| LetterAuction            | ❌           | ❌                  | ❌          | ❌         |             |
| LiarsDice                | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/liars-dice)|
| Mastermind               | ❌           | ❌                  | ❌          | ❌         |             |
| MathProof                | ❌           | ❌                  | ❌          | ❌         |             |
| MemoryGame               | ❌           | ❌                  | ❌          | ❌         |             |
| Mr.Jack                  | ❌           | ❌                  | ❌          | ❌         |             |
| Negotiation              | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/negotiation)|
| Onitama                  | ❌           | ❌                  | ❌          | ❌         |             |
| Pipeline                 | ❌           | ❌                  | ❌          | ❌         |             |
| Poker                    | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/poker)|
| Santorini                | ❌           | ❌                  | ❌          | ❌         |             |
| ScenarioPlanning         | ❌           | ❌                  | ❌          | ❌         |             |
| SpellingBee              | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/spelling-bee)|
| SpiteAndMalice           | ❌           | ❌                  | ❌          | ❌         |             |
| Stratego                 | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/stratego)|
| Taboo                    | ❌           | ❌                  | ❌          | ❌         |             |
| Tak                      | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/tak)|
| UltimateTicTacToe        | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/ultimate-tic-tac-toe)|
| TruthAndDeception        | ✅           | ✅                  | ✅          | ✅         |[link](https://textarena.ai/environments/two-player/truth-and-deception)|
| WordChains               | ❌           | ❌                  | ❌          | ❌         |             |

# Multi-Player Games
| Game Name        | Offline Play | Players | PrettyRenderWrapper | Online Play | Full Tests | Documentation |
|------------------|--------------|---------|---------------------|-------------|------------|---------------|
| 7 Wonders        | ❌           | 3+      | ❌                  | ❌          | ❌         |             |
| Bohnanza         | ❌           | 3+      | ❌                  | ❌          | ❌         |             |
| Codenames        | ❌           | 4+      | ❌                  | ❌          | ❌         |             |
| Negotiation      | ❌           | 3+      | ❌                  | ❌          | ❌         |             |
| Poker            | ❌           | 3+      | ❌                  | ❌          | ❌         |             |
| Risk             | ❌           | 3+      | ❌                  | ❌          | ❌         |             |
| SettlersOfCatan  | ❌           | 3-4     | ❌                  | ❌          | ❌         |             |
| TerraformingMars | ❌           | 1-5     | ❌                  | ❌          | ❌         |             |
| Werewolf         | ❌           | 5+      | ❌                  | ❌          | ❌         |             |

