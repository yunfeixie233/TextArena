# Mastermind Environment Documentation

## Overview
**Mastermind** is a code-breaking puzzle game where the player attempts to guess a hidden sequence of digits. After each guess, feedback is provided in the form of "pegs" that indicate correct digits in correct positions and correct digits in wrong positions. The player must use logical deduction to identify the secret code before running out of turns. This environment offers customizable difficulty settings including the code length, number range, and whether duplicates are allowed.

## Action Space

- **Format:** Actions are strings representing the player's guess in the format `[X X X X]`, where X is a digit between 1 and the maximum allowed number.
- **Examples:**
  - Guess a code with digits 1, 2, 3, 4: `[1 2 3 4]`
  - Guess a code with digits 5, 2, 6, 4: `[5 2 6 4]`
- **Notes:** Players can include additional text in their replies, but must provide their final guess in the correct format with square brackets.

## Observation Space

**Reset Observations**
On reset, the player receives a prompt containing the game instructions. For example:

```plaintext
You are Player 0. You are playing Mastermind.
... that is 4 digits long, each digit from 1 to 6, with no duplicates.
In your response, you can mention any code or previously submitted code in the format of 1 2 3 4. Only when you have decided to make your guess, then you must strictly enter the code in square brackets like [2 1 4 5]. This is to avoid submitting a wrong code to the game environment.
Hence, if you are quoting a recent guess, you must mention the numbers without the square brackets.
After each guess, you will receive feedback in the form of black and white pegs.
A black peg indicates a correct digit in the correct position, while a white peg indicates a correct digit in the wrong position.
You have only 20 turns to guess the code.
```

**Step Observations**
After each guess, the player receives feedback about their guess. For example:

```plaintext
[Player 0] I'll start with a systematic approach by guessing [1 2 3 4].
[GAME] Player 0 submitted [1 2 3 4]. Feedback: 1 black peg(s), 2 white peg(s).
[Player 0] Based on the feedback, I know one digit is in the correct position and two digits are in the code but in wrong positions. I'll try a different arrangement with [1 3 5 2].
[GAME] Player 0 submitted [1 3 5 2]. Feedback: 2 black peg(s), 1 white peg(s).
```

## Gameplay

- **Players:** 1 player (single-player game)
- **Initial Setup:** The system randomly generates a secret code of specified length
- **Turns:** The player takes turns making guesses about the secret code
- **Objective:** Deduce the secret code within the allowed number of attempts
- **Maximum Turns:** Configurable, default is 20 turns

## Key Rules

1. **Code Generation:**
   - The secret code consists of digits between 1 and a specified maximum (default: 6)
   - Code length is configurable (default: 4)
   - Depending on configuration, the code may or may not contain duplicate digits

2. **Guessing:**
   - Player submits a guess in the format `[X X X X]` (space-separated digits in square brackets)
   - The guess must have the same length as the secret code
   - All digits must be within the allowed range
   - If duplicates are not allowed in the code, the guess also cannot contain duplicates

3. **Feedback System:**
   - After each guess, the player receives feedback in the form of black and white pegs
   - Black peg: correct digit in the correct position
   - White peg: correct digit in the wrong position
   - The total number of pegs can range from 0 to the code length

4. **Winning Conditions:**
   - **Win:** The player correctly guesses the entire secret code (receives a number of black pegs equal to the code length)
   - **Loss:** The player fails to guess the code within the maximum allowed turns

5. **Game Termination:**
   - The game concludes when either the player correctly guesses the code or exhausts all available turns

## Rewards

| Outcome     | Reward for Player |
|-------------|:-----------------:|
| **Win**     | `+1`              |
| **Lose**    | `-1`              |
| **Invalid** | `-1`              |

## Parameters

- `code_length` (`int`, default: `4`):
  - **Description:** Sets the length of the secret code to be guessed
  - **Impact:** Longer codes increase difficulty by expanding the solution space

- `num_numbers` (`int`, default: `6`):
  - **Description:** Sets the range of digits used in the code (1 to num_numbers)
  - **Impact:** Higher values increase difficulty by expanding the potential digits in each position

- `max_turns` (`int`, default: `20`):
  - **Description:** Sets the maximum number of guesses the player can make
  - **Impact:** Fewer turns make the game more challenging by limiting attempts

- `duplicate_numbers` (`bool`, default: `False`):
  - **Description:** Determines whether the secret code can contain duplicate digits
  - **Impact:** Allowing duplicates significantly increases difficulty by expanding the solution space

## Variants

| Env-id                  | code_length | num_numbers | max_turns | duplicate_numbers |
|-------------------------|:-----------:|:-----------:|:---------:|:-----------------:|
| `Mastermind-v0`         | `4`         | `6`         | `20`      | `False`           |
| `Mastermind-v0-hard`    | `4`         | `8`         | `30`      | `False`           |
| `Mastermind-v0-extreme` | `6`         | `12`        | `50`      | `True`            |



### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg