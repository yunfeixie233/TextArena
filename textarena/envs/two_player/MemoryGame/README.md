# Memory Game Environment Documentation

## Overview

**Memory Game** is a two-player turn-based game designed to test players' memory and concentration. Each player takes turns flipping pairs of cards on a grid, attempting to find matching pairs. The objective is to remember the locations of previously revealed cards to maximize the number of matches and score points. The game ends when all pairs have been matched, and the player with the most matches wins. This environment supports multiple difficulty levels, with varying grid sizes that adjust the game's complexity.

## Action Space

- **Format:** Actions are strings representing the player's choices. For example:
- **Example:**
    - Reveal the cards at row 1 column 2 and row 3 column 1: [1 2 3 1]
    - Reveal the cards at row 2 column 4 and row 2 column 3: [2 4 2 3]
- **Notes:** Players can have additional texts in their replies, as long as they provide their coodinate actions in the correct format.

## Observation Space
**Reset Observation:**
On reset, each player receives a prompt containing their beginning game instructinos. For example:
```plaintext
[GAME] You are Player 0. You are playing the Memory Game (easy level).
Your goal is to match more pairs of cards on the board, than your opponent.
On your turn, select two cards to flip by entering the row and column numbers of the first and second card respectively like [0 1 1 0], where the first card is in row 0 and column 1, and the second card is in row 1 and column 0.
If the two cards match, you get a point and the cards remain face up. If they do not match, the cards are flipped back face down, e.g. '.'.
The game ends when all pairs have been matched.
Here is the initial board with all cards faced down:
  0 1 2 3
0 . . . .
1 . . . .
2 . . . .
3 . . . .
```

**Step Observation:**
After each step, the players receive the latest message from the other player. For example, here's player 1 making its move:
```plaintext
[Player 0] To begin the Memory Game, I'll select two cards to flip. Since it's the first turn, I don't have any prior information about the cards. Let's start with these two positions:

Flip the card at row 0, column 0 and the card at row 0, column 1.

[0 0 0 1]
[GAME] The cards do not match. Cards at positions [0 0] and [0 1] are A and F respectively.
[Player 1] Now it's my turn. I'll try to remember the cards that have been revealed. The cards at positions [0 0] and [0 1] are A and F respectively.

I'll flip the card at row 0, column 2 and the card at row 0, column 3.

[0 2 0 3]
```

## Gameplay

- **Players**: 2
- **Turns**: Players take turns selecting two cards to flip on the grid.
- **Board**: A grid of facedown cards is presented at the start, with pairs of matching symbols hidden.
- **Objective**: Match pairs of cards by remembering previously revealed locations and flipping pairs with matching symbols.
- **Difficulty Levels**: The game can be configured with different grid sizes based on difficulty level (easy, medium, hard).

## Key Rules

1. Card Matching:
    - Players take turns flipping two cards on the board.
    - If the selected cards match, the player earns a point (not reward), and the matched cards remain face up.
    - If the selected cards do not match, they are flipped back face down.

2. Valid Moves:
    - Players select two distinct card positions by specifying row and column coordinates.
    - Moves are invalid if a player selects the same card twice or if one or both selected cards have already been matched.

3. Winning Conditions:
    - **Win**: The player with the most points for matched pairs at the end of the game wins.
    - **Loss**: The player with fewer points for matched pairs loses.
    - **Draw**: If both players have the same number of matches when all pairs have been matched, the game ends in a draw.

4. Game Termination:
    - The game ends when all pairs have been matched.
    - If the game is tied, it ends in a draw; otherwise, the player with the most matches is declared the winner.


## Rewards

| Outcome          | Reward for Player | Reward for Opponent |
|------------------|:-----------------:|:-------------------:|
| **Win**          | `+1`              | `-1`                |
| **Lose**         | `-1`              | `+1`                |
| **Invalid**      | `-1`              | `0`                 |
| **Draw**         | `0`               | `0`                 |


## Parameters

- `difficulty` (`str`):
    - **Description**: Sets the difficulty level, adjusting the grid size.
    - **Options**:
        - `"easy"`: Creates a 4x4 grid, ideal for quick and simpler gameplay.
        - `"medium"`: Creates a 6x6 grid, offering moderate difficulty.
        - `"hard"`: Creates an 8x8 grid, challenging players’ memory with more cards.
    - **Impact**:
        - Larger grids increase the game’s difficulty by adding more card pairs, making it harder to remember card locations.


## Variants

| Env-id                  | difficulty |
|-------------------------|:----------:|
| `MemoryGame-v0-easy`    | `easy`     |
| `MemoryGame-v0-medium`  | `medium`   |
| `MemoryGame-v0-hard`    | `hard`     |


## Example Usage

```python
import textarena as ta

# Initialize the environment
env = ta.make(env_id="MemoryGame-v0-easy")

# Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

# Wrap the environment for pretty rendering
env = ta.wrappers.PrettyRenderWrapper(env=env)

# initalize agents
agents = {
    0: ta.basic_agents.OpenRouter(model_name="gpt-4o"),
    1: ta.basic_agents.OpenRouter(model_name="gpt-4o-mini")
    }

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

# Finally, print the game results
for player_id, agent in agents.items():
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")
```



## Troubleshooting

- **Unmatched Pairs Despite Multiple Attempts**:
    - **Issue**: Players are unable to find matching pairs after several turns, leading to a slower game pace.
    - **Solution**: Encourage players to pay attention to the locations of previously revealed cards and remember their symbols.

- **Invalid Move Format**:
    - **Issue**: A player selects an invalid format or repeats the same card coordinates for both selections.
    - **Solution**: Ensure moves are formatted correctly as two distinct row and column coordinates (e.g., `[0 1 1 0]`). Check the selected positions to avoid choosing the same card twice.

- **Out-of-Bounds or Matched Cards Selected**:
    - **Issue**: A player selects coordinates outside the board grid or chooses cards that have already been matched.
    - **Solution**: Double-check the board dimensions based on difficulty level and avoid selecting already matched cards. Use valid, in-bounds coordinates only.

- **Game Ending in a Draw**:
    - **Issue**: The game ends in a draw if players score equally after all pairs are matched.
    - **Solution**: Increase the difficulty level to introduce a larger grid, making it harder to match pairs and reducing the likelihood of a tie.



## Version History
- **v0**
  - Initial release 



### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg