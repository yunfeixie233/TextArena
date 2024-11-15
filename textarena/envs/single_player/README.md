# Single Player Games

Welcome to the Single Player Games module in our repository. This directory houses a collection of text-based games, each designed to serve as an evaluation environment for large language models (LLMs). These games test a variety of skills, including logical reasoning, pattern recognition, decision-making, and adaptability, making them ideal for single-player LLM assessment. Each game environment is implemented to be easily accessible and extendable.

## Games Overview

| Game                  | Description                                                                                                                                                 | Status |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| **20 Questions**      | The model attempts to guess an object by asking up to 20 yes/no questions.                                                                                  | Done   |
| **Car Puzzle**        | A text-based puzzle where players rearrange cars in a grid to achieve a specific order.                                                                     | -      |
| **Chess**             | Play chess against a bot opponent, focusing on strategy and tactical decision-making.                                                                       | -      |
| **Connect Four**      | A classic game where players try to connect four pieces in a row on a grid, adapted for single-player challenges.                                           | -      |
| **Crosswords**        | Solve text-based crossword puzzles where clues are provided, and words must fit into the grid correctly.                                                    | Done   |
| **Fifteen Puzzle**    | A sliding puzzle that consists of a frame of numbered square tiles in random order, with one tile missing.                                                 | Done   |
| **Guess the Number**  | Guess a randomly chosen number within a range, receiving hints to narrow down possibilities.                                                                | Done   |
| **Guess Who**         | Identify a hidden character by asking yes/no questions to eliminate possibilities.                                                                          | Done   |
| **Hangman**           | Guess letters to reveal a hidden word before running out of attempts.                                                                                       | Done   |
| **Logic Puzzles**     | Solve text-based logic puzzles that challenge deductive reasoning and problem-solving skills.                                                               | Done   |
| **Minesweeper**       | Uncover cells in a grid without triggering hidden mines, using numbers to deduce mine locations.                                                           | Done   |
| **Sudoku**            | Solve a 9x9 grid by filling each row, column, and subgrid with unique numbers from 1 to 9.                                                                  | Done   |
| **Tower of Hanoi**    | Move a stack of disks between rods, obeying specific rules, to achieve the correct order on the target rod.                                                 | Done   |
| **Word Ladder**       | Transform one word into another by changing one letter at a time, with each step forming a valid word.                                                      | Done   |
| **Word Search**       | Find hidden words within a grid of letters presented in text format.                                                                                        | Done   |
| **Wordle**      | Guess a hidden five-letter word within six attempts. After each guess, feedback is provided on correct letters and positions to help players narrow down possibilities. | -      |


Above is a list of single-player games currently included in this module. Each game is marked with its current development status, and aach game is organized in its own folder, containing the following components:

1. **README.md**: Provides a detailed description of the game, setup instructions, and usage examples.
2. **Game Environment Class** (`env.py`): Implements the core logic and rules of the game environment.
3. **Test Module** (`test.py`): Contains test cases to ensure the game environment functions as expected.
4. **Example Script** (`example.py`): Demonstrates how to initialize, configure, and run the game environment, allowing users to quickly get started and see a working example in action.

This structure ensures that each game environment is self-contained and easy to understand, modify, and test independently. Users can navigate to each game's folder to find everything needed to set up and explore that specific environment.


## Getting Started

This section will guide you through setting up and playing a single-player game environment using a registered game, `GuessTheNumber-v0-hardcore`, as an example.

### 1. Environment Registration

Each game environment is registered in the `init.py` script (found [here](../__init__.py)), specifying its `id`, `entry_point`, and any game-specific configurations (e.g., difficulty level, max turns). You can view or modify the list of registered environments in this script. Here’s an example registration:

```python
register(
    id="GuessTheNumber-v0-hardcore",
    entry_point="textarena.envs.single_player.GuessTheNumber.env:GuessTheNumberEnv",
    hardcore=True,
    max_turns=30,
)
```
### 2. Initialize the Environment
To start a game, initialize the environment by calling ta.make with the environment’s ID. For better handling of observations and rendering, you can wrap the environment with additional wrappers, such as LLMObservationWrapper and PrettyRenderWrapper:

```python
import textarena as ta

# Initialize the environment
env = ta.make("GuessTheNumber-v0-hardcore")

# Apply wrappers for observation handling and rendering
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.PrettyRenderWrapper(env=env)
```

### 3. Initialize Agents
Create an agent to interact with the environment. For example, you can use HFLocalAgent to run a Hugging Face model locally:
```python
# initalize agents
agents = {
    0: ta.basic_agents.OpenRouter(model_name="gpt-4o-mini")
    }
```

### 4. Start a New Game and Run the Game Loop
Reset the environment to start a new game. Implement the game loop where the agent observes, acts, and steps through the game until it's complete:
```python
# reset the environment to start a new game
observations = env.reset(seed=490)

# Game loop
done = False
while not done:

    # Get the current player
    current_player_id = env.state.get("current_player")

    # Get the current observation for the player
    obs = observations[current_player_id]

    # Agent decides on an action based on the observation
    action = agents[current_player_id](obs)

    # Execute the action in the environment
    observations, rewards, truncated, terminated, info = env.step(current_player_id, action)

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
# Finally, print the game results
for player_id, agent in agents.items():
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")
```

