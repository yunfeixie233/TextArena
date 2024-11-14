# Two-Player Games

This directory contains two-player games designed for competitive or collaborative interactions between agents. Each game allows language models (LLMs) to showcase their reasoning, strategy, and decision-making skills. The games listed below are organized with their current development status and a brief description.

## Games Overview

| Game                                  | Description                                                                                                                                                        | Status              |
|---------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------|
| **Battleship**                        | Players take turns guessing the location of their opponent’s ships on a grid, aiming to "sink" all ships first.                                                   | Done                |
| **Car Puzzle**                        | A competitive puzzle where players arrange cars in a grid according to specific rules.                                                                            | Buggy, not done     |
| **Chess**                             | Classic chess game where each player aims to checkmate their opponent.                                                                                            | Done, not tested    |
| **Code Creation**                     | Players collaboratively or competitively generate code to solve specific tasks or challenges.                                                                     | -                   |
| **Connect Four**                      | A classic game where players try to connect four pieces in a row on a grid.                                                                                       | Done, not tested    |
| **Debate**                            | Players debate a topic, aiming to present stronger arguments than their opponent.                                                                                 | Done, not tested    |
| **Don't Say It**                      | A word-guessing game where players must communicate without using certain restricted words.                                                                       | Done, not tested    |
| **Iterated Prisoner's Dilemma with Chat** | Classic iterated Prisoner's Dilemma game where players can communicate before each round to establish trust or deception strategies.                       | Done                |
| **Liar's Dice**                       | Players bluff and bid on the dice values each one possesses, aiming to outwit the opponent.                                                                      | Done, not tested    |
| **Letter Auction**                    | Players "bid" on letters to form the highest-scoring word. Each player has limited points to bid, aiming to create the most valuable word.                       | Done                |
| **Mastermind**                        | One player sets a code, and the other tries to guess it with feedback on each attempt.                                                                           | Done                |
| **Math Proof**                        | Players take turns to solve math problems or present proofs, competing to answer correctly and efficiently.                                                       | -                   |
| **Memory Game**                       | Players try to match pairs of cards, testing their memory skills.                                                                                                 | Done                |
| **Negotiation**                       | Players negotiate to reach mutually beneficial outcomes or agreements based on set rules.                                                                         | Done, not tested    |
| **Poker**                             | Players compete in a simplified poker game, aiming to win by forming the highest-value hand.                                                                      | Buggy, not done     |
| **Scenario Planning**                 | Players propose and discuss future scenarios based on a given prompt or context.                                                                                  | Done, not tested    |
| **Spelling Bee**                      | Players compete to spell increasingly complex words correctly.                                                                                                    | Done, not tested    |
| **Spite and Malice**                  | A card game where players aim to play their cards in sequence, aiming to finish their deck before the opponent.                                                  | Done                |
| **Taboo**                             | Players must describe a word without using a list of restricted terms.                                                                                            | Done, not tested    |
| **Truth or Deception**                | One player provides information, and the other must determine if it’s true or deceptive. Facts may need to be verified.                                           | Done, not tested / Fact-check needed |
| **Word Chains**                       | Players take turns saying words that start with the last letter of the previous word.                                                                             | Done, not tested    |

Above is a list of two-player games currently included in this module. Each game is marked with its current development status, and each game is organized in its own folder, containing the following components:

1. **README.md**: Provides a detailed description of the game, setup instructions, and usage examples.
2. **Game Environment Class** (`env.py`): Implements the core logic and rules of the game environment.
3. **Test Module** (`test.py`): Contains test cases to ensure the game environment functions as expected.
4. **Example Script** (`example.py`): Demonstrates how to initialize, configure, and run the game environment, allowing users to quickly get started and see a working example in action.

This structure ensures that each game environment is self-contained and easy to understand, modify, and test independently. Users can navigate to each game's folder to find everything needed to set up and explore that specific environment.

## Getting Started

For most two-player games, a Standard Turn-Based Cycle is used. In this approach, players alternate turns in a straightforward, predictable manner: after Agent0 completes one action in the environment, it becomes Agent1's turn to act.

However, some two-player games follow a more flexible Dynamic Turn-Based Cycle. In this cycle, Agent0 can take multiple actions consecutively, with each action generating a new observation state that informs the next action. Once Agent0 completes its entire sequence of actions, Agent1 then follows the same pattern.

To support these varying turn-based structures, we’ve designed a `State` class that efficiently manages these mechanics, ensuring a consistent interface across different games. This allows the game loop code to remain uniform and intuitive, regardless of whether a game uses a Standard or Dynamic Turn-Based Cycle.

This section will guide you through setting up and playing a two-player game environment using a registered game, `Battleship-v0-easy`, as an example.

### 1. Environment Registration

Each game environment is registered in the `init.py` script (found [here](../__init__.py)), specifying its `id`, `entry_point`, and any game-specific configurations (e.g., difficulty level, max turns). You can view or modify the list of registered environments in this script. Here’s an example registration:

```python
register(
    "Battleship-v0-easy",
    entry_point="textarena.envs.two_player.Battleship.env:BattleshipEnv",
    difficulty="easy",
)
```
### 2. Initialize the Environment
To start a game, initialize the environment by calling ta.make with the environment’s ID. For better handling of observations and rendering, you can wrap the environment with additional wrappers, such as LLMObservationWrapper and PrettyRenderWrapper:

```python
import textarena as ta

# Initialize the environment
env = ta.make("Battleship-v0-easy")

# Apply wrappers for observation handling and rendering
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.PrettyRenderWrapper(env=env)
```

### 3. Initialize Agents
Create an agent to interact with the environment. For example, you can use HFLocalAgent to run a Hugging Face model locally:
```python
# Initialize two agents
agent0 = ta.basic_agents.OpenRouter(model_name="gpt-4o")
agent1 = ta.basic_agents.OpenRouter(model_name="gpt-4o-mini")
```

### 4. Start a New Game and Run the Game Loop
Reset the environment to start a new game. Implement the game loop where the agent observes, acts, and steps through the game until it's complete:
```python
# Reset the environment
observations = env.reset(seed=490) # optional seed to initialize the game

# Game loop
done = False
while not done:

    # Get the current player
    player_id = env.state.current_player

    # Get the current agent
    agent = agent0 if player_id == 0 else agent1

    # Get the current observation for the player
    obs = observations[player_id]

    # Agent decides on an action based on the observation
    action = agent(obs)

    # Execute the action in the environment
    observations, rewards, truncated, terminated, info = env.step(player_id, action)

    # Check if the game has ended
    done = terminated or truncated

    # Optionally render the environment to see the current state
    env.render()

    if done:
        break
```

### 5. View Game Results
Once the game loop ends, print the results to see the final score or other outcome details:
```python
# Print game results
for player_id, agent in enumerate([agent0, agent1]):
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")
```

