# Crosswords Environment Documentation

## Overview
Crosswords is a single-player puzzle game where the player fills in a crossword grid with words based on provided clues. The player’s objective is to correctly guess all the words using the hints given, ensuring that the letters align correctly in the grid. The environment supports a standard and a hardcore mode, influencing the difficulty of the words provided.

## Action Space
- **Format**: Actions are strings in the format [row col letter], where:
    - row and col are grid indices (starting from 0) indicating the cell position.
    - letter is the character the player wants to place in the specified cell.

- **Examples**:
    - To place the letter 'A' in row 4, column 7: [4 7 A]

- **Notes**: Players can provide multiple guesses at once in the format [row col letter]. Additional text may accompany the action, but it must contain the correct format for the action to be processed. Incorrectly formatted actions or wrong guesses will be marked as invalid.

## Observation Space

**Reset Observation:**
On reset, the observation provides the initial prompt and the state of the Crosswords grid. For example:

```plaintext
You are playing Crosswords.
Here is the current state of the Crosswords grid. Each row and column are numbered.
The cells that need to be populated with letters are represented by '_', and those that do not need words are represented by '.'.

Current Crosswords Grid:
   C00 C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C11
R00  _   _   .   .   .   .   .   .   .   .   .   .  
R01  _   _   .   .   .   .   .   .   .   .   .   .  
R02  _   _   .   .   .   .   _   .   .   .   .   .  
R03  _   _   .   .   .   .   _   .   .   .   .   .  
R04  _   .   .   .   .   .   _   .   .   .   .   .  
R05  .   .   .   .   .   .   _   .   .   .   .   .  
R06  .   .   .   .   .   .   _   .   .   .   .   .  
R07  .   .   .   .   .   .   _   .   .   .   .   .  
R08  .   .   .   .   .   .   _   .   .   .   .   .  
R09  .   .   .   .   .   .   _   .   .   .   .   .  
R10  .   .   .   .   .   .   .   .   .   .   .   .  
R11  .   .   .   .   .   .   .   .   .   .   .   .  

Here are the clues for the words you need to find:
1. The belief system that guides moral and ethical behavior. (8 letters)  : (2, 6, 'down')
2. A trusty companion for cowboys on the range. (5 letters)  : (0, 0, 'down')
3. To indicate or demonstrate something clearly. (4 letters)  : (0, 1, 'down')

You can only provide one response per turn. Hence, plan your approach and risk appetite. Only guesses in the format of [row column letter] will be fetched from your response, e.g. [0 0 d], [1 2 G].
As you play, the history of your choices will be appended below. Use the information to complete the game.

```

**Step Observation:**
After each step, the environment returns the action and the updated Crosswords grid as the observation. For example:

```plaintext
Let's start by focusing on the clues and the grid positioning provided. I will begin with the five-letter word at (0, 0, 'down').

Given the clue: "A trusty companion for cowboys on the range," the word is likely "HORSE". We would begin by filling in the first letter:

[0 0 H]

Board state: 
   C00 C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C11
R00  H   _   .   .   .   .   .   .   .   .   .   .  
R01  _   _   .   .   .   .   .   .   .   .   .   .  
R02  _   _   .   .   .   .   _   .   .   .   .   .  
R03  _   _   .   .   .   .   _   .   .   .   .   .  
R04  _   .   .   .   .   .   _   .   .   .   .   .  
R05  .   .   .   .   .   .   _   .   .   .   .   .  
R06  .   .   .   .   .   .   _   .   .   .   .   .  
R07  .   .   .   .   .   .   _   .   .   .   .   .  
R08  .   .   .   .   .   .   _   .   .   .   .   .  
R09  .   .   .   .   .   .   _   .   .   .   .   .  
R10  .   .   .   .   .   .   .   .   .   .   .   .  
R11  .   .   .   .   .   .   .   .   .   .   .   .  

```

## Gameplay
- **Grid Size**: The grid size is variable and dynamically generated based on the longest word and the number of words included.
- **Turns**: The player fills empty cells ('_') with letters to match the words in the clues.
- **Word Placement**: Words are placed either horizontally ("across") or vertically ("down") based on the clues. Players must fill in the letters one by one, ensuring they match the word locations and directions.
- **Winning Condition**: The game is won when all cells with letters are filled correctly based on the crossword solution.


## Key Rules

1. **Valid Moves**: The player must enter a valid row, column, and letter in the [row col letter] format. The move must not overwrite a filled cell or place a letter that doesn’t match the crossword solution.


## Rewards
| Outcome          |             Reward for Player              |
|------------------|:-------------------------------------------:|
| **Win**          |                    `+1`                    |
| **Lose**         |    `self._get_percentage_completion()`     |
| **Invalid Move** |    `self._get_percentage_completion()`     |

## Parameters

- `hardcore` (`bool`):
    - **Description:** Determines how the difficulty of the words used.
    - **Impact:**
        - **Normal:** Player has 30 turns to guess 3 non-hardcore words.
        - **Hardcore**: Player has 30 turns to guess 3 hardcore words.

- `max_turns` (`int`):
    - **Description:** Determines how many turns the player has to make its decisions.
    - **Impact:** This affects the number of tries it can make to complete the game. 

- `num_words` (`int`):
    - **Description:** Determines how many words the player has to guess.
    - **Impact:** More words means the player has to factor in more overlapping words. 

## Variants

| Env-id                    | hardcore | max_turns | num_words |
|---------------------------|:--------:|:---------:|:---------:|
| `Crosswords-v0`           | `False`  |  `30`     |  `3`      |
| `Crosswords-v0-hardcore`  | `True`   |  `30`     |  `3`      |



### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg