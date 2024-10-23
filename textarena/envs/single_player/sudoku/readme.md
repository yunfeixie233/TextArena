# Sudoku Environment Documentation

## Overview

Sudoku is a single-player puzzle game where the player fills a 9x9 grid with numbers from 1 to 9. The goal is to ensure that each number appears only once in each row, column, and 3x3 subgrid. This environment supports varying difficulty levels and allows for hint-enabled or hint-disabled gameplay.

## Action Space
- **Format**: Actions are strings in the format [row col num], where row and col are grid indices (1-9) and num is the number (1-9) the player wants to place.
- **Examples**: [5 3 7], I would like to place 7 in row 5, column 3: [5 3 7]
- **Notes**: Additional text can accompany the action, but it must include the correct format [row col num] for the action to be processed correctly.

## Observation Space

**Reset Observation:**
On reset, the observation provides the initial prompt and the state of the Sudoku grid. For example:
```plaintext
[GAME]: You are Player {player_id}. You are playing Sudoku ({difficulty}).
Here is the current state of the Sudoku grid. Each row is numbered from 1 to 9, and each column is also numbered from 1 to 9.
Empty cells are represented by '.', and pre-filled cells contain digits from 1 to 9.

Current Sudoku Grid:
   C1 C2 C3   C4 C5 C6   C7 C8 C9  
R1  .  8  9 |  1  .  . |  .  3  7
R2  2  7  1 |  9  4  3 |  6  .  8
R3  .  6  5 |  .  2  7 |  4  9  .
   - - - - - - - - - - - - - - - - 
R4  .  .  . |  7  8  . |  9  2  3
R5  .  9  2 |  .  5  6 |  .  .  4
R6  7  3  8 |  .  .  2 |  1  .  .
   - - - - - - - - - - - - - - - - 
R7  8  4  . |  .  .  9 |  5  .  .
R8  5  .  . |  6  .  8 |  3  4  9
R9  9  .  6 |  5  3  4 |  8  7  2

Your objective is to fill the empty cells in the 9x9 grid with digits from 1 to 9 such that:
1. Each row contains all digits from 1 to 9 without repetition.
2. Each column contains all digits from 1 to 9 without repetition.
3. Each of the nine 3x3 subgrids contains all digits from 1 to 9 without repetition.

Rules and Instructions:
1. **Do not overwrite** the initial numbers provided in the grid.
2. **Only fill** empty cells represented by '.'.
3. You may respond in any manner you prefer, but ensure that your response includes the format of '[row column number]'.
4. **Ensure** that your move does not violate Sudoku rules. Invalid moves will result in penalties.

Examples:
- **Valid Move**:
  - Grid Snippet Before Move:
    
  - Move: `[5 3 7]`
  - Explanation: Placing 7 at row 5, column 3 does not violate any Sudoku rules.

- **Invalid Move** (Overwriting a pre-filled cell):
  - Grid Snippet Before Move:
    
  - Move: `[1 1 9]`
  - Explanation: Cell (1,1) is already filled with 5. You cannot overwrite it.

- **Invalid Move** (Violating Sudoku rules):
  - Grid Snippet Before Move:
    
  - Move: `[1 3 5]`
  - Explanation: Placing 5 in row 1, column 3 violates the rule since 5 already exists in row 1.

The history of your moves and thoughts will be appended as you play more rounds. Use the history of your move to improve your decision-making by avoiding the moves you have tried. Good luck!

```
**Step Observation:**
After each step, the environment returns the action and the updated Sudoku grid as the observation. For example:
```plaintext

### Step 1: Identify Possible Moves

1. **Row 1** has values 3, 7, 8, 9, and 1. The missing numbers are 2, 4, 5, and 6.
   - C1 can be 2, 4, 5, or 6.
   - C5 can be 2, 4, 5, or 6.
   - C6 can be 2, 4, 5, or 6.
   
2. **Row 2** has values 1, 2, 3, 4, 6, 7, 8, and 9. The missing number is 5.
   - C8 must be 5.

3. **Row 3** has values 2, 4, 5, 6, 7, and 9. The missing numbers are 1, 3, and 8.
   - C1 can be 1, 3, or 8.
   - C4 can be 1, 3, or 8.
   - C9 can be 1, 3, or 8.

4. **Row 4** has values 2, 3, 7, 8, and 9. The missing numbers are 1, 4, 5, and 6.
   - C1, C2, C3 can take 1, 4, 5, or 6.

5. **Row 5** has values 2, 4, 5, 6, and 9. The missing numbers are 1, 3, 7, and 8.
   - C1, C7, and C8 can take 1, 3, 7, or 8.

6. **Row 6** has values 1, 2, 3, 7, and 8. The missing numbers are 4, 5, 6, and 9.
   - C4, C5, and C6 can take 4, 5, 6, or 9.

7. **Row 7** has values 4, 5, 8, and 9. The missing numbers are 1, 2, 3, 6, and 7.
   - C3 can be 1, 2, 3, 6, or 7.

8. **Row 8** has values 3, 4, 5, 6, 8, and 9. The missing numbers are 1, 2, and 7.
   - C2 can be 1, 2, or 7.
   - C3 can be 1, 2, or 7.

9. **Row 9** has values 2, 3, 4, 6, 7, 8, and 9. The missing numbers are 1 and 5.
   - C2 can be 1 or 5.

### Step 2: Making a Move

Let's fill in a confirmed move:

- **Move:** Place 5 in Row 2, Column 8.

This satisfies all Sudoku rules and completes Row 2.

**Move Format:** `[2 8 5]`

Now, let me make that move.

```

By default, the environment returns observations in the following format:
```python
{
  player_id: int : [
    (sender_id: int, message: str),
    ...
  ]
}
```
where each step can product zero, one or many message tuples.

## Gameplay
- **Grid Size**: Fixed at 9x9.
- **Turns**: The player fills empty cells with numbers from 1 to 9.
- **Number Placement**: A number can only be placed in an empty cell, ensuring it doesn’t violate Sudoku rules (no repetition in rows, columns, or 3x3 subgrids).
- **Winning Condition**: The game is won when all cells are filled correctly according to Sudoku rules.
- **Restart Condition**: The player can restart if they make an error and wish to try again.

## Key Rules
- **Valid Moves**:

    - The player must enter a valid row, column, and number (1-9) in the [row col num] format.
    - The move must not overwrite a pre-filled cell or violate Sudoku rules.

- **Invalid Moves**:
 
    - Entering an invalid row, column, or number (outside the 1-9 range).
    - Overwriting a pre-filled cell or placing a number that violates - Sudoku rules (duplicates in the same row, column, or 3x3 subgrid) will result in a penalty.


## Rewards
| Outcome          | Reward for Player  |
|------------------|:------------------:|
| **Win**          |       `+1`         |
| **Lose**         |       `-1`         |
| **Invalid Move** |       `-1`         |

## Parameters

- `difficulty` (`str`):
    - **Description:** Determines how many clues the player has to begin with.
    - **Impact:**
        - **Easy:** Player is provided with 50 pre-filled positions. It has to only guess 31 values.
        - **Medium**: Player is provided with 40 pre-filled positions. It has to only guess 41 values.
        - **Hard**: Player is provided with 30 pre-filled positions. It has to only guess 51 values.

- `max_turns` (`int`):
    - **Description:** Determines how many turns the player has to make its decisions.
    - **Impact:** This affects the number of tries it can make to complete the game. 


## Variants

| Env-id              | difficulty | max_turns |
|---------------------|:----------:|:---------:|
| `Sudoku-v0-easy`    |   `easy`   | `31`      |
| `Sudoku-v0-medium`  |   `medium` | `41`      |
| `Sudoku-v0-hard`    |   `hard`   | `51`      |

## Example Usage

```python
import textarena as ta

## initializa the environment
env = ta.make("Sudoku-v0-easy")

## Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

## Wrap the environment for pretty rendering
env = ta.wrappers.PrettyRenderWrapper(env=env)

## initalize agents
agent0  = ta.default_agents.GPTAgent(model="gpt-4o-mini")
s game
observations = env.reset(seed=490)

## Write the game loop
done = False
while not done:
    for player_id, agent in enumerate([agent0]):
        ## get the current observation for the player
        obs = observations[player_id]

        ## Get the agent to use the observation and make an action
        action = agent(obs) 

        ## use the action and execute in the environment
        observation, rewards, truncated, terminated, info = env.step(player_id, action)

        ## render the environment
        env.render()

        ## check if the game has ended
        done = truncated or terminated

## Finally, print the game results
for player_id, agent in enumerate([agent0]):
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")
```

## Troubleshooting

**TODO**


## Version History
- **v0**
  - Initial release 


### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg