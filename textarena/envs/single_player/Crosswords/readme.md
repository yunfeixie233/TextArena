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
On reset, the observation provides the initial prompt and the state of the Sudoku grid. For example:

```plaintext
"You are Player 0. You are playing Crosswords (False).
Here is the current state of the Crosswords grid. Each row is numbered, and each column is also numbered.
The cells that need to be populated with letters are represented by '_', and those that do not need words are represented by '.'.

Current Crosswords Grid:
   C00 C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C11 C12 C13 C14 C15
R00  _   _   .   .   .   .   .   .   .   .   .   .   .   .   .   .  
R01  _   _   .   .   .   .   .   .   .   .   .   .   .   .   .   .  
R02  _   _   .   .   .   .   .   .   _   _   _   .   .   .   .   .  
R03  _   _   .   .   .   .   .   .   _   .   .   .   .   .   .   .  
R04  _   .   .   .   .   .   .   .   _   .   .   .   .   .   .   .  
R05  _   .   .   .   .   .   .   .   _   .   .   .   .   .   .   .  
R06  _   .   .   .   .   .   _   .   _   .   .   .   .   .   .   .  
R07  _   .   .   .   .   .   _   .   _   .   .   .   .   .   .   .  
R08  _   .   .   .   _   _   _   _   _   .   .   .   .   .   .   .  
R09  .   .   .   .   _   .   _   _   _   .   .   .   .   .   .   .  
R10  .   .   .   .   _   .   .   _   _   .   .   .   .   .   .   .  
R11  .   .   .   .   .   .   .   _   _   .   .   .   .   .   .   .  
R12  .   .   .   .   .   .   .   .   _   .   .   .   .   .   .   .  
R13  .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .  
R14  .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .  
R15  .   .   .   .   .   .   .   .   .   .   .   .   .   .   .   .  

Here are the clues for the words you need to find:
1. An area of study focused on social or economic progress (10 letters).  : (2, 8, 'down')
2. Having knowledge of one's own existence. (9 letters)  : (0, 0, 'down')
3. A knife's edge is often described as this. (5 letters)  : (8, 4, 'across')
4. What you might find on a house to shield it from rain. (4 letters)  : (8, 7, 'down')
5. This term often describes a route or highway. (4 letters)  : (6, 6, 'down')
6. The act of controlling or managing a situation or group. (4 letters)  : (0, 1, 'down')
7. To look at closely or examine. (3 letters): (8, 4, 'down')
8. This four-legged animal is known for barking and wagging its tail. (3 letters)  : (2, 8, 'across')

You may provide your response in any manner. However, note that any wrong guesses will result in you losing. Hence, plan your approach and risk appetite. Only guesses in the format of [row column letter] will be fetched from your response.
As you play, the history of your choices will be appended below. Use the information to complete the game."
```

**Step Observation:**
After each step, the environment returns the action and the updated Sudoku grid as the observation. For example:

```plaintext
To solve the crossword clues, I'll start by analyzing the clues and their positions.

1. **Clue:** An area of study focused on social or economic progress (10 letters).  
   **Position:** (2, 8) down  
   **Answer:** "development"

2. **Clue:** Having knowledge of one's own existence (9 letters).  
   **Position:** (0, 0) down  
   **Answer:** "self-aware"

3. **Clue:** A knife's edge is often described as this (5 letters).  
   **Position:** (8, 4) across  
   **Answer:** "sharp"

4. **Clue:** What you might find on a house to shield it from rain (4 letters).  
   **Position:** (8, 7) down  
   **Answer:** "roof"

5. **Clue:** This term often describes a route or highway (4 letters).  
   **Position:** (6, 6) down  
   **Answer:** "road"

6. **Clue:** The act of controlling or managing a situation or group (4 letters).  
   **Position:** (0, 1) down  
   **Answer:** "lead"

7. **Clue:** To look at closely or examine (3 letters).  
   **Position:** (8, 4) down  
   **Answer:** "see"

8. **Clue:** This four-legged animal is known for barking and wagging its tail (3 letters).  
   **Position:** (2, 8) across  
   **Answer:** "dog"

Now, I'll start filling in the answers based on their respective positions.

1. For the word "development" at (2, 8) down:
   - [2, 8, 'd']
   - [3, 8, 'e']
   - [4, 8, 'v']
   - [5, 8, 'e']
   - [6, 8, 'l']
   - [7, 8, 'o']
   - [8, 8, 'p']
   - [9, 8, 'm']
   - [10, 8, 'e']
   - [11, 8, 'n']
   - [12, 8, 't']

2. For the word "self-aware" at (0, 0) down:
   - [0, 0, 's']
   - [1, 0, 'e']
   - [2, 0, 'l']
   - [3, 0, 'f']
   - [4, 0, '-']
   - [5, 0, 'a']
   - [6, 0, 'w']
   - [7, 0, 'a']
   - [8, 0, 'r']
   - [9, 0, 'e']

3. For the word "sharp" at (8, 4) across:
   - [8, 4, 's']
   - [8, 5, 'h']
   - [8, 6, 'a']
   - [8, 7, 'r']
   - [8, 8, 'p']

4. For the word "roof" at (8, 7) down:
   - [8, 7, 'r']
   - [9, 7, 'o']
   - [10, 7, 'o']
   - [11, 7, 'f']

5. For the word "road" at (6, 6) down:
   - [6, 6, 'r']
   - [7, 6, 'o']
   - [8, 6, 'a']
   - [9, 6, 'd']

6. For the word "lead" at (0, 1) down:
   - [0, 1, 'l']
   - [1, 1, 'e']
   - [2, 1, 'a']
   - [3, 1, 'd']

7. For the word "see" at (8, 4) down:
   - [8, 4, 's']
   - [9, 4, 'e']
   - [10, 4, 'e']

8. For the word "dog" at (2, 8) across:
   - [2, 8, 'd']
   - [2, 9, 'o']
   - [2, 10, 'g']

Now, I'll go ahead and fill in the answers based on these clues. 

Given the complexity, I will proceed with each guess in the format specified.

Here are my guesses for the crossword:

1. [2, 8, 'd']
2. [3, 8, 'e']
3. [4, 8, 'v']
4. [5, 8, 'e']
5. [6, 8, 'l']
6. [7, 8, 'o']
7. [8, 8, 'p']
8. [9, 8, 'm']
9. [10, 8, 'e']
10. [11, 8, 'n']
11. [12, 8, 't']
12. [0, 0, 's']
13. [1, 0, 'e']
14. [2, 0, 'l']
15. [3, 0, 'f']
16. [4, 0, '-']
17. [5, 0, 'a']
18. [6, 0, 'w']
19. [7, 0, 'a']
20. [8, 0, 'r']
21. [9, 0, 'e']
22. [8, 4, 's']
23. [8, 5, 'h']
24. [8, 6, 'a']
25. [8, 7, 'r']
26. [8, 8, 'p']
27. [8, 7, 'r']
28. [9, 7, 'o']
29. [10, 7, 'o']
30. [11, 7, 'f']
31. [6, 6, 'r']
32. [7, 6, 'o']
33. [8, 6, 'a']
34. [9, 6, 'd']
35. [0, 1, 'l']
36. [1, 1, 'e']
37. [2, 1, 'a']
38. [3, 1, 'd']
39. [8, 4, 's']
40. [9, 4, 'e']
41. [10, 4, 'e']
42. [2, 8, 'd']
43. [2, 9, 'o']
44. [2, 10, 'g']

However, I will submit only the key guesses that fill in the grid based on their clues:

1. [2, 8, 'd']
2. [3, 8, 'e']
3. [4, 8, 'v']
4. [5, 8, 'e']
5. [6, 8, 'l']
6. [7, 8, 'o']
7. [8, 8, 'p']
8. [9, 8, 'm']
9. [10, 8, 'e']
10. [11, 8, 'n']
11. [12, 8, 't']
12. [0, 0, 's']
13. [1, 0, 'e']
14. [2, 0, 'l']
15. [3, 0, 'f']
16. [4, 0, '-']
17. [5, 0, 'a']
18. [6, 0, 'w']
19. [7, 0, 'a']
20. [8, 0, 'r']
21. [9, 0, 'e']
22. [8, 4, 's']
23. [8, 5, 'h']
24. [8, 6, 'a']
25. [8, 7, 'r']
26. [8, 8, 'p']
27. [8, 7, 'r']
28. [9, 7, 'o']
29. [10, 7, 'o']
30. [11, 7, 'f']
31. [6, 6, 'r']
32. [7, 6, 'o']
33. [8, 6, 'a']
34. [9, 6, 'd']
35. [0, 1, 'l']
36. [1, 1, 'e']
37. [2, 1, 'a']
38. [3, 1, 'd']
39. [8, 4, 's']
40. [9, 4, 'e']
41. [10, 4, 'e']
42. [2, 8, 'd']
43. [2, 9, 'o']
44. [2, 10, 'g'] 

Now I will submit the first guesses for the clues that have positions ready. 

I will start with:

1. [0, 0, 's']
2. [1, 0, 'e']
3. [2, 0, 'l']
4. [3, 0, 'f']
5. [2, 8, 'd']
6. [3, 8, 'e']
7. [4, 8, 'v']
8. [5, 8, 'e']
9. [6, 8, 'l']
10. [7, 8, 'o']
11. [8, 8, 'p']
12. [9, 8, 'm']
13. [10, 8, 'e']
14. [11, 8, 'n']
15. [12, 8, 't']
16. [8, 4, 's']
17. [8, 5, 'h']
18. [8, 6, 'a']
19. [8, 7, 'r']
20. [8, 8, 'p']
21. [8, 7, 'r']
22. [9, 7, 'o']
23. [10, 7, 'o']
24. [11, 7, 'f']
25. [6, 6, 'r']
26. [7, 6, 'o']
27. [8, 6, 'a']
28. [9, 6, 'd']
29. [0, 1, 'l']
30. [1, 1, 'e']
31. [2, 1, 'a']
32. [3, 1, 'd']
33. [8, 4, 's']
34. [9, 4, 'e']
35. [10, 4, 'e']
36. [2, 8, 'd']
37. [2, 9, 'o']
38. [2, 10, 'g']

This is a comprehensive approach. Now, let’s see how many of these guesses are correct!
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

## Gameplay
- **Grid Size**: The grid size is variable and dynamically generated based on the longest word and the number of words included.
- **Turns**: The player fills empty cells ('_') with letters to match the words in the clues.
- **Word Placement**: Words are placed either horizontally ("across") or vertically ("down") based on the clues. Players must fill in the letters one by one, ensuring they match the word locations and directions.
- **Winning Condition**: The game is won when all cells with letters are filled correctly based on the crossword solution.
- **Restart Condition**: The player can restart if they choose or when all allowed turns are exhausted without solving the crossword.

## Key Rules
- **Valid Moves**:

    - The player must enter a valid row, column, and letter in the [row col letter] format.
    - The move must not overwrite a filled cell or place a letter that doesn’t match the crossword solution.

- **Invalid Moves**:

    - Entering a row, column, or letter outside the grid bounds.
    - Overwriting an already filled cell.
    - Placing a letter that doesn’t align with the correct solution will result in the move being marked as invalid.

## Rewards
| Outcome          | Reward for Player  |
|------------------|:------------------:|
| **Win**          |       `+1`         |
| **Lose**         |       `-1`         |
| **Invalid Move** |       `-1`         |

## Parameters

- `hardcore` (`bool`):
    - **Description:** Determines how many clues the player has to begin with.
    - **Impact:**
        - **Easy:** Player is provided with 50 pre-filled positions. It has to only guess 31 values.
        - **Medium**: Player is provided with 40 pre-filled positions. It has to only guess 41 values.
        - **Hard**: Player is provided with 30 pre-filled positions. It has to only guess 51 values.

- `max_turns` (`int`):
    - **Description:** Determines how many turns the player has to make its decisions.
    - **Impact:** This affects the number of tries it can make to complete the game. 

- `num_words` (`int`):
    - **Description:** Determines how many words the player has to guess.
    - **Impact:** More words means the player has to factor in more overlapping words. 

## Variants

| Env-id                    | hardcore | max_turns | num_words |
|---------------------------|:--------:|:---------:|:---------:|
| `Crosswords-v0`           | `easy`   |  `30`     |  `8`      |
| `Crosswords-v0-hardcore`  | `medium` |  `30`     |  `8`      |

## Example Usage
```python
import textarena as ta

## initializa the environment
env = ta.make("Crosswords-v0")

## Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

## Wrap the environment for pretty rendering
env = ta.wrappers.PrettyRenderWrapper(env=env)

## initalize agents
agent0  = ta.default_agents.GPTAgent(model="gpt-4o-mini")

## reset the environment to start a new game
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