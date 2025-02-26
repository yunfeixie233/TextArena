# TicTacToe Environment Documentation

## Overview
**TicTacToe** (also known as Noughts and Crosses) is a classic two-player game played on a 3×3 grid. Players take turns marking cells with their symbol (X or O), with the objective of placing three of their marks in a horizontal, vertical, or diagonal row. This implementation provides a complete game environment with move validation, win detection, and draw conditions. The simplicity of TicTacToe makes it an excellent introductory game for understanding strategic thinking and perfect information games.

## Action Space

- **Format:** Actions are strings representing the row and column coordinates of the cell to mark, in the format `[row col]` or `[row, col]`, where row and col are 0-indexed positions on the 3×3 grid (0-2).
- **Examples:**
  - Mark the center cell (row 1, column 1): `[1 1]` or `[1, 1]`
  - Mark the top-right cell (row 0, column 2): `[0 2]` or `[0, 2]`
- **Notes:** Players can include additional text before and after their action command. Spaces around the coordinates are optional, and a comma between coordinates is also optional.

## Observation Space

**Reset Observations**
On reset, each player receives a prompt containing the initial game board and rules. For example:

```plaintext
You are Player 0 in Tic Tac Toe.
Your goal is to win three in a row (horizontally, vertically, or diagonally) on the board.
On your turn, you mark a row&col position on the 3x3 grid.

Rules to remember:
1. You can only place your mark in an empty cell.
2. You win by completing three of your marks in a row (horizontally, vertically, or diagonally).
3. The game ends in a draw if the board is filled with no winner.
4. To submit your move, provide [row, col] where row and col are the cell coordinates (0-2).
For example, '[1 1]' places your mark in the center cell of the board.

As Player 0, you will be 'O', while your opponent is 'X'.
Below is the current state of the board:
   |   |   
---+---+---
   |   |   
---+---+---
   |   |   
```

**Step Observations**
After each move, players receive an updated view of the board. For example:

```plaintext
[Player 1] I'll take the center position [1 1]
[GAME] Player 1 made a move at row 1, col 1.
New state of the board:
   |   |   
---+---+---
   | X |   
---+---+---
   |   |   

[Player 0] I'll mark the top-left corner [0 0]
[GAME] Player 0 made a move at row 0, col 0.
New state of the board:
 O |   |   
---+---+---
   | X |   
---+---+---
   |   |   
```

## Gameplay

- **Players:** 2 players
- **Initial Setup:** An empty 3×3 grid
- **Player Symbols:** Player 1 uses 'X', Player 0 uses 'O'
- **Turns:** Players take turns marking one empty cell per turn
- **Objective:** Form a line of three of your symbols (horizontally, vertically, or diagonally)

## Key Rules

1. **Grid Structure:**
   - The game is played on a 3×3 grid
   - Each cell can be empty or contain one player's symbol ('X' or 'O')

2. **Turn Order:**
   - Players alternate turns, with Player 1 ('X') typically going first
   - On each turn, a player marks one empty cell with their symbol

3. **Valid Moves:**
   - Players can only mark empty cells
   - Cell coordinates are specified as row and column indices (0-2)
   - Once a cell is marked, it cannot be changed

4. **Winning Conditions:**
   - **Win:** A player wins by forming a line of three of their symbols:
     - Horizontally (in any of the three rows)
     - Vertically (in any of the three columns)
     - Diagonally (either top-left to bottom-right or top-right to bottom-left)
   - **Draw:** The game ends in a draw if all nine cells are filled without a winner
   - **Loss:** A player loses if the opponent forms a line of three symbols

5. **Game Termination:**
   - The game concludes when a player wins or the board is completely filled (draw)

## Rewards

| Outcome     | Reward for Winner | Reward for Loser |
|-------------|:-----------------:|:----------------:|
| **Win**     | `+1`              | `-1`             |
| **Draw**    | `0`               | `0`              |
| **Invalid** | `-1`              | `0`              |



### Contact
If you have questions or face issues with this specific environment, please reach out directly to vincentcheng236@gmail.com