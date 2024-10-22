# Don't Say It Environment Documentation

## Overview

**Don't Say It** is a two-player conversational game where each player is assigned a secret word. The objective is to subtly guide the conversation to make the other player say your secret word while avoiding mentioning your own. The game encourages strategic communication and subtlety, making it both challenging and entertaining.

## Action Space

- **Format:** Actions are strings representing the player's messages.
- **Example:** `"Let's talk about something interesting."`
- **Notes:** Players can converse freely, but mentioning the opponent's secret word results in a win, while mentioning their own secret word leads to a loss.

## Observation Space

### Player Observations

Each player receives a series of messages exchanged during the game. Depending on the environment's configuration, players may have access to additional information.

**Example Observation:**
```plaintext
[Player 0]: Hi there!
[Player 1]: Hello! How are you?
[Player 0]: I'm good, thanks. What's new?
```

### Hidden Information
Players do not have access to the opponent's secret word. They only know their own secret word and the history of the conversation.

## Gameplay
- **Players**: 2
- **Turns**: Players alternate sending messages to each other.
- **Secret Words**: Each player has a unique secret word assigned at the start of the game.
- **Objective**: Make the opponent say your secret word while avoiding saying your own.
- **Turn Limit**: The game can be configured with a maximum number of turns, after which it ends in a draw if no secret words are mentioned.

## Key Rules
1. Secret Words:
    - Each player is assigned a secret word at the start.
    - Players must protect their own secret word while trying to make the opponent say theirs.

2. Valid Moves:
    - Players send messages as strings.
    - Messages can contain any text but should aim to indirectly lead the opponent to say the secret word.

3. Winning Conditions:
    - **Win**: If a player successfully makes the opponent say their secret word.
    - **Loss**: If a player accidentally says their own secret word.
    - **Draw**: If the maximum number of turns is reached without any secret word being mentioned.

4. Game Termination:
    - The game ends immediately upon a win or loss.
    - If the turn limit is reached, the game ends in a draw.

## Rewards

| Outcome          | Reward for Player | Reward for Opponent |
|------------------|--------------------|---------------------|
| **Win**          | +1                 | -1                  |
| **Lose**         | -1                 | +1                  |
| **Draw**         | 0                  | 0                   |


## Parameters

- `hardcore` (`bool`):

    - **Description**: Determines the complexity of the secret words.
    - **Impact**:
        - `True`: Uses a full English word set, including complex words.
        - `False`: Uses a simplified English word set for easier gameplay.

- `max_turns` (`int`):
    - **Description**: Specifies the maximum number of turns allowed before the game ends in a draw.
    - **Impact**: Limits the duration of the game, promoting quicker resolutions.

- `data_path` (`str`):
    - **Description**: The path to the JSON file containing the list of possible secret words.
    - **Impact**: Allows customization of the word pool used in the game.


## Variants

| Env-id                   | hardcore | max_turns | data_path |
|--------------------------|----------|-----------|-----------|
| `DontSayIt-v0`           | `False`  |    `30`   | `Default` |
| `DontSayIt-v0-hardcore`  | `True`   |    `30`   | `Default` |
| `DontSayIt-v0-unlimited` | `False`  |   `None`  | `Default` |

## Example Usage

```python
import textarena as ta

# Initialize the environment
env = ta.make(env_id="DontSayIt-v0")

# Initialize agents
agent1 = ta.default_agents.GPTAgent(model="gpt-4")
agent2 = ta.default_agents.GPTAgent(model="gpt-4")

# Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

# Reset the environment to start a new game
observations, secret_words = env.reset(seed=42)

# Game loop
done = False
while not done:
    for player_id, agent in enumerate([agent1, agent2]):
        # Get the current observation for the player
        obs = observations[player_id]

        # Agent decides on an action based on the observation
        action = agent(obs)

        # Execute the action in the environment
        observations, rewards, truncated, terminated, info = env.step(player_id, action)

        # Check if the game has ended
        done = terminated or truncated

        # Optionally render the environment to see the current state
        # env.render()

        if done:
            break
```

## Troubleshooting

- **Accidental Word Mention:**
    - **Issue:** A player accidentally mentions their own secret word.
    - **Solution:** Ensure that players are aware of their secret words and strategize to avoid mentioning them.

- **Opponent's Word Not Being Mentioned:**
    - **Issue:** Players are unable to guide the conversation towards the opponent's secret word.
    - **Solution:** Encourage creative and subtle conversational strategies to indirectly reference the opponent's word.

- **Invalid Messages:**
    - **Issue:** Players send non-string actions or invalid message formats.
    - **Solution:** Ensure that all actions are valid strings representing meaningful messages.

- **Turn Limit Reached Without Outcome:**
    - **Issue:** The game ends in a draw after reaching the maximum number of turns.
    - **Solution:** Increase the max_turns parameter to allow more conversational exchanges if desired.

## Version History
- **v0**
  - Initial release 