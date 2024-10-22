# Connect Four Environment Documentation

## Overview

Connect Four is a two-player connection game where players alternately drop discs into a vertical grid. The objective is to connect four of one's own discs in a row—vertically, horizontally, or diagonally—before the opponent does. This text-based environment allows customization of grid size and supports both Open and Closed game modes.

## Action Space

- **Format:** Actions are strings in the format `[col x]`, where `x` is a valid column number (0 to `num_cols - 1`).
- **Examples:** `[col 3]`, `I will drop the disc into column 3: [col 3]` 
- **Notes:** Additional context or comments can be included in the action string, but it must contain the column in the correct format.

## Observation Space

### Open Mode (`is_open=True`)

**Reset Observation:**
On reset, the player-wise observation in open mode contain the game prompt and initial board state. For example:
```plaintext
[GAME]: You are Player {player_id} in Connect Four.
Your disc symbol: {'X'|'O'}.
The game board has {num_rows} rows and {num_cols} columns.
Players take turns dropping their disc into one of the columns (0 to {num_cols - 1}).
First to connect four discs vertically, horizontally, or diagonally wins.
On your turn, enter the column number in squared brackets to make your move.
For example: '[col 4]' or '[col 1]'.
The game board is visible to both players.
Current Board:
0 1 2 3 4 5 6
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
```

**Step Observation:**
After each step, the environment in open mode will return the action and board state as the observation. For example:
```plaintext
[Player 0]: I'll drop the disc in the thrid column [col 3].
[GAME]: 
Current Board:
0 1 2 3 4 5 6
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . . . . .
. . . X . . .
```

### Closed Mode (`is_open=False`)
**Reset Observation:**
On reset, the closed mode environment will return the game prompt to each player.For example:
```plaintext
[GAME]: You are Player {player_id} in Connect Four.
Your disc symbol: {'X'|'O'}.
The game board has {num_rows} rows and {num_cols} columns.
Players take turns dropping their disc into one of the columns (0 to {num_cols - 1}).
First to connect four discs vertically, horizontally, or diagonally wins.
On your turn, enter the column number in squared brackets to make your move.
For example: '[col 4]' or '[col 1]'.
The game board is not visible to players.
```

**Step Observation:**
After each step, the environment in closed mode will return the action to each player. For example:
For example:
```plaintext
[Player 0]: I'll drop the disc in the thrid column [col 3].
```


Please note that the above example observations are the output of an environment wrapped in the `LLMObservationWrapper`. By default the environment will return an observation of the following format
```python
{
  player_0_id: int : [
    (sender_id: int, message: str),
    (sender_id: int, message: str),
    (sender_id: int, message: str),
    ...
  ],
  player_1_id: int : [
    (sender_id: int, message: str),
    (sender_id: int, message: str),
    (sender_id: int, message: str),
    ...
  ]
}
```
where each step can produce zero, one or many message tuples.


## Gameplay

- **Grid Size:** Customizable (`num_rows` x `num_cols`).
- **Turns:** Players alternate dropping discs into columns.
- **Disc Placement:** A disc falls to the lowest available space within the chosen column.
- **Winning Condition:** Connect four discs vertically, horizontally, or diagonally.
- **Draw Condition:** The game ends in a draw if the board is full without any player connecting four discs.

## Key Rules

- **Valid Moves:**
  - Players must enter a valid column number (`0` to `num_cols - 1`) on their turn.
  - The action must follow the `[col x]` format.

- **Invalid Moves:**
  - Entering an invalid column number or selecting a full column ends the game.

- **Game Modes:**
  - **Open Mode (`is_open=True`):** Game board is visible to both players.
  - **Closed Mode (`is_open=False`):** Game board is hidden from players.

## Rewards

| Outcome          | Reward for Player  | Reward for Opponent |
|------------------|:------------------:|:-------------------:|
| **Win**          |       `+1`         |        `-1`         |
| **Lose**         |       `-1`         |        `+1`         |
| **Draw**         |        `0`         |         `0`         |
| **Invalid Move** |       `-1`         |         `0`         |

## Parameters

- `is_open` (`bool`): 
  - **Description:** Determines whether the game board is visible to both players.
  - **Impact:** 
    - **True:** Players can see the current state of the board.
    - **False:** Players receive only textual updates without seeing the board.

- `num_rows` (`int`): 
  - **Description:** Specifies the number of rows in the game board.
  - **Impact:** Affects the vertical size of the grid, influencing how discs stack.

- `num_cols` (`int`): 
  - **Description:** Specifies the number of columns in the game board.
  - **Impact:** Determines the horizontal size of the grid and available columns for disc placement.

## Variants

| Env-id                   | is_open | num_rows | num_cols |
|--------------------------|:-------:|:--------:|:--------:|
| `ConnectFour-v0`         | `True`  | `6`      | `7`      |
| `ConnectFour-v0-blind`   | `False` | `6`      | `7`      |
| `ConnectFour-v0-large`   | `True`  | `12`     | `15`     |

## Example Usage

```python
import textarena as ta

# Initialize the environment
env = ta.make(env_id="ConnectFour-v0")

# Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

# Initialize agents
agent0 = ta.default_agents.GPTAgent(model="gpt-4o")
agent1 = ta.default_agents.GPTAgent(model="gpt-4o-mini")


# Reset the environment to start a new game
observations = env.reset()

# Game loop
done = False
while not done:
    for player_id, agent in enumerate([agent0, agent1]):
        # Get the current observation for the player
        obs = observations[player_id]

        # Agent decides on an action based on the observation
        action = agent(obs)

        # Execute the action in the environment
        (
          observations, 
          rewards, 
          truncated, 
          terminated, 
          info
        ) = env.step(player_id, action)

        # Check if the game has ended
        done = terminated or truncated

        # Optionally render the environment
        # env.render()

        if done:
            break

# print the game results
for player_id, agent in enumerate([agent0, agent1]):
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")
```

## Troubleshooting

- **Invalid Action Format:**
  - **Issue:** Player sends an action that doesn't match the `[col x]` format.
  - **Solution:** Ensure that actions are strings formatted exactly as `[col x]`, where `x` is a valid column number.

- **Column Full:**
  - **Issue:** Player attempts to drop a disc into a full column.
  - **Solution:** Choose a different column that is not full.

- **Out of Bounds Column Number:**
  - **Issue:** Player selects a column number outside the valid range (0 to `num_cols - 1`).
  - **Solution:** Verify the number of columns and select a valid column number within the range.


## Version History
- **v0**
  - Initial release 



### Contact
If you have questions or there are issues with this specific environment, please reach out directly to Guertlerlo@cfar.a-star.edu.sg