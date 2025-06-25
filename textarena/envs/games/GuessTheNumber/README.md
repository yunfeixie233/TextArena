# Guess The Number Environment Documentation

## Overview

Guess The Number is a single-player game where the player attempts to guess a randomly chosen number within a specified range. The environment supports two modes: Basic (numbers between 1 and 20) and Hardcore (numbers between 1 and 100). The player receives hints ("higher" or "lower") after each guess until they find the correct number or run out of turns.

## Action Space

- **Format**: Actions are strings containing a guess in the format [number], where number is the player's guess within the range specified for the game mode.
- **Examples**:
    [7]: Player guesses the number 7.
    [25]: Player guesses the number 25 (only valid in Hardcore mode).
- **Notes**: Additional text may accompany the action, but it must include the correct format [number] for the guess to be processed. For example, "I think the number is [10]" would be valid as long as the number is within the allowed range.

## Observation Space
**Reset Observation:**
On reset, the observation provides the initial prompt and the state of the Sudoku grid. For example:
```plaintext
[GAME] You are Player 0. You are playing Guess The Number (Basic).
You have to guess the number between 1 and 20.
As you enter your guess, the game will provide you with hints such as 'higher' or 'lower'.
You may provide your response in any manner. Only the number that is wrapped in square brackets will be considered as your guess. For example, [5].
As you play, the history of your guesses will be appended below. Use the information to complete the game before you run out of guesses.
Enter your guess.
```

**Step Observation:**
After each step, the environment returns the action and the updated Sudoku grid as the observation. For example:
```plaintext
[Player 0] Let's start the game. I'll make my first guess.

[50]
[GAME] Your guess of 50 is lower.
```

## Gameplay

- **Number Range**:
    - Basic Mode: 1 to 20.
    - Hardcore Mode: 1 to 50.
- **Turns**: The player has a maximum of 10 turns to guess the correct number.
- *Hints*: After each guess, the player receives a hint indicating whether the target number is "higher" or "lower" than their guess.
- **Winning Condition**: The player wins the game when they correctly guess the target number within the allowed turns.

## Key Rules

1. **Valid Moves**: The player must enter a valid positive number within the specified range for the chosen mode in the [number] format.


## Rewards
| Outcome          |             Reward for Player              |
|------------------|:------------------------------------------:|
| **Win**          |                    `+1`                    |
| **Lose**         |    `self._get_percentage_completion()`     |
| **Invalid Move** |    `self._get_percentage_completion()`     |

## Parameters

- `min_number` (`int`):
    - **Description**: The lower bound for the random number generation.
- `max_number` (`int`):
    - **Description**: The upper bound for the random number generation.
- `max_turns` (`int`):
    - **Description**: The maximum number of turns before the game ends in a loss.

## Variants

| Env-id                       | min_number  | max_number  | max_turns   |
|------------------------------|:-----------:|:-----------:|:-----------:|
| `GuessTheNumber-v0`          |   `1`       |   `20`      |  `10`       |
| `GuessTheNumber-v0-hardcore` |   `1`       |   `50`      |  `10`        |


### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg