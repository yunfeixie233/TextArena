# Sudoku Environment Documentation

## Overview
**Sudoku** is a single-player logic-based number placement puzzle. In this implementation, players are presented with a 9×9 grid partially filled with numbers. The objective is to fill the empty cells with digits 1-9 according to the classic Sudoku rules: each row, column, and 3×3 subgrid must contain all digits from 1 to 9 without repetition. This environment generates puzzles with a guaranteed unique solution, provides validation of moves against the correct solution, and allows for configurable difficulty through the number of initial clues provided.

## Action Space

- **Format:** Actions are strings representing cell coordinates and the number to place, in the format `[row column number]`, where row and column are 1-indexed positions on the grid and number is the digit to place (1-9).
- **Examples:**
  - Place the number 7 at row 5, column 3: `[5 3 7]`
  - Place the number 4 at row 9, column 8: `[9 8 4]`
- **Notes:** Players can include additional text before and after their action command. Only valid moves that adhere to Sudoku rules are accepted.

## Observation Space

**Reset Observations**
On reset, the player receives a prompt containing the initial Sudoku grid and the game rules. For example:

```plaintext
You are Player 0. You are playing Sudoku.
Here is the current state of the Sudoku grid. Each row is numbered from 1 to 9, and each column is also numbered from 1 to 9.
Empty cells are represented by '.', and pre-filled cells contain digits from 1 to 9.

Current Sudoku Grid:
   C1 C2 C3  C4 C5 C6  C7 C8 C9
R1  5  .  . |  .  .  7 |  .  .  . 
R2  .  .  . |  1  9  5 |  .  .  . 
R3  .  9  8 |  .  .  . |  .  6  . 
   - - - - - - - - - - - - - - - -
R4  8  .  . |  .  6  . |  .  .  3 
R5  4  .  . |  8  .  3 |  .  .  1 
R6  7  .  . |  .  2  . |  .  .  6 
   - - - - - - - - - - - - - - - -
R7  .  6  . |  .  .  . |  2  8  . 
R8  .  .  . |  4  1  9 |  .  .  5 
R9  .  .  . |  .  8  . |  .  7  9 

Your objective is to fill the empty cells in the 9x9 grid with digits from 1 to 9 such that:
1. Each row contains all digits from 1 to 9 without repetition.
2. Each column contains all digits from 1 to 9 without repetition.
3. Each of the nine 3x3 subgrids contains all digits from 1 to 9 without repetition.

Rules and Instructions:
1. **Do not overwrite** the initial numbers provided in the grid.
2. **Only fill** empty cells represented by '.'.
3. You may respond in any manner you prefer, but ensure that your response includes the format of '[row column number]'.
4. **Ensure** that your move does not violate Sudoku rules. Invalid moves will result in penalties.
```

**Step Observations**
After each move, the player receives an updated view of the grid. For example:

```plaintext
[Player 0] I'll place a 2 in row A, column B since this follows the Sudoku rules. [1 4 2]
[GAME] Board state: 
   C1 C2 C3  C4 C5 C6  C7 C8 C9
R1  5  .  . |  2  .  7 |  .  .  . 
R2  .  .  . |  1  9  5 |  .  .  . 
R3  .  9  8 |  .  .  . |  .  6  . 
   - - - - - - - - - - - - - - - -
R4  8  .  . |  .  6  . |  .  .  3 
R5  4  .  . |  8  .  3 |  .  .  1 
R6  7  .  . |  .  2  . |  .  .  6 
   - - - - - - - - - - - - - - - -
R7  .  6  . |  .  .  . |  2  8  . 
R8  .  .  . |  4  1  9 |  .  .  5 
R9  .  .  . |  .  8  . |  .  7  9 
```

## Gameplay

- **Players:** 1 player (single-player game)
- **Initial Setup:** A 9×9 grid partially filled with numbers (clues)
- **Objective:** Fill all empty cells according to Sudoku rules
- **Maximum Turns:** Configurable, default is 100 turns

## Key Rules

1. **Grid Structure:**
   - The Sudoku grid consists of a 9×9 grid, which is further divided into nine 3×3 subgrids
   - Initially, some cells are already filled with digits (clues) that cannot be changed

2. **Placement Rules:**
   - Each row must contain all digits from 1 to 9 without repetition
   - Each column must contain all digits from 1 to 9 without repetition
   - Each 3×3 subgrid must contain all digits from 1 to 9 without repetition

3. **Valid Moves:**
   - Players can only place digits in empty cells
   - Players cannot overwrite pre-filled cells (clues)
   - Players must adhere to Sudoku rules when placing a digit

4. **Winning Conditions:**
   - **Win:** Successfully fill all empty cells in accordance with Sudoku rules
   - **Loss:** Fail to complete the puzzle within the maximum number of allowed turns

5. **Game Termination:**
   - The game concludes when either the entire grid is correctly filled or the maximum turn limit is reached

## Rewards

| Outcome     | Reward for Player |
|-------------|:-----------------:|
| **Win**     | `+1`              |
| **Loss**    | `-1`              |
| **Invalid** | `-1`              |

## Parameters

- `clues` (`int`, default: `30`):
  - **Description:** Number of pre-filled cells (clues) in the initial grid
  - **Impact:** Fewer clues increase difficulty by providing less initial information

- `max_turns` (`int`, default: `100`):
  - **Description:** Maximum number of turns allowed to complete the puzzle
  - **Impact:** Fewer turns increase pressure on the player to solve quickly

## Variants

| Env-id              | clues | max_turns |
|---------------------|:-----:|:---------:|
| `Sudoku-v0`         | `30`  | `100`     |
| `Sudoku-v0-medium`  | `40`  | `100`     |
| `Sudoku-v0-hard`    | `50`  | `100`     |


### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg