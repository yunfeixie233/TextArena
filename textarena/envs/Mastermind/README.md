# Mastermind Environment Documentation

## Description
Mastermind is a code-breaking puzzle game where the player attempts to guess a hidden sequence of digits. After each guess, feedback is provided in the form of "pegs" that indicate correct digits in correct positions and correct digits in wrong positions. The player must use logical deduction to identify the secret code before running out of turns. This environment offers customizable difficulty settings including the code length, number range, and whether duplicates are allowed.


## Observations
At the beginning of the game, the player will receive the game prompt and initial board state as an observation:
```plaintext
[GAME] You are playing Mastermind.
You need to find the code that is 4 digits long, each digit from 1 to 6, with no duplicates.
In your response, you can submit your guess in the following format: '[2 1 4 5]'.
After each guess, you will receive feedback in the form of black and white pegs.
A black peg indicates a correct digit in the correct position, while a white peg indicates a correct digit in the wrong position.
You have 20 turns to guess the code.
```
Subsequently, after every guess the Player will receive feedback from the environment (i.e. `[GAME] Submitted [1 2 3 4]. Feedback: 0 black peg(s), 3 white peg(s).`)

## Actions
At each turn, the player can submit a guess for the code (i.e. `[2 4 1 3]`). The lenght of the guess has to match the length of the code.


## Reward Design
- Game completion -> Reward `1`
- Invalid move -> Reward `-1`
- Turn limit -> Reward ∝ pct. of correct numbers (i.e. percentage of black pegs)


## Environment Parameters
- `code_length` (`int`, default: `4`):
  - **Description:** Sets the length of the secret code to be guessed

- `num_numbers` (`int`, default: `6`):
  - **Description:** Sets the range of digits used in the code (1 to num_numbers)

- `max_turns` (`int`, default: `20`):
  - **Description:** Sets the maximum number of guesses the player can make

- `duplicate_numbers` (`bool`, default: `False`):
  - **Description:** Determines whether the secret code can contain duplicate digits


## Variants
| Env-id                      | code_length | num_numbers | max_turns | duplicate_numbers |                Wrappers Used                     |
|-----------------------------|:-----------:|:-----------:|:---------:|:-----------------:|:-----------------------------------------------: |
| `Mastermind-v0`             | `4`         | `6`         | `20`      | `False`           |`LLMObservationWrapper`, `ActionFormattingWrapper`|
| `Mastermind-v0-hard`        | `4`         | `8`         | `30`      | `False`           |`LLMObservationWrapper`, `ActionFormattingWrapper`|
| `Mastermind-v0-extreme`     | `6`         | `12`        | `50`      | `True`            |`LLMObservationWrapper`, `ActionFormattingWrapper`|
| `Mastermind-v0-raw`         | `4`         | `6`         | `20`      | `False`           |`None`                                            |
| `Mastermind-v0-raw-hard`    | `4`         | `8`         | `30`      | `False`           |`None`                                            |
| `Mastermind-v0-raw-extreme` | `6`         | `12`        | `50`      | `True`            |`None`                                            |

### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg

