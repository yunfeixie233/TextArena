# Word Ladder Environment Documentation

## Overview

Word Ladder is a single-player puzzle game where the player aims to transform a starting word into a target word by changing one letter at a time. Each step must yield a valid word that differs by exactly one letter from the previous word, forming a chain from the start word to the target. The environment provides both a standard and a hardcore mode, impacting the word list difficulty. Players are guided by a prompt detailing the rules and gameplay, and their move history is displayed to track progress.

## Action Space
- **Format**: Actions are strings in the format [word], where:
- **Examples**:
    - To say that the next word after "sain" is "main": [main]
- **Notes**: Additional text may accompany the action, but it must contain the correct format for the action to be processed. Incorrectly formatted actions will be marked as invalid.

## Observation Space
**Reset Observation:**
On reset, the observation provides the initial prompt and the starting words and target words. For example:
```plaintext
[GAME] You are Player 0. You are playing Word Ladder (Hardcore).
The objective of the game is to convert the start word to the target word by changing one letter at a time.
The start word is: sain
The target word is: teal
To submit your word, you must wrap it in square brackets, e.g. [word].
As you play, the history of your choices will be appended below. Use the information to win the game.
```

** Step Observation: **
After each step, the environment returns the action and the updated Word Ladder text as the observation. For example:
```plaintext
[Player 0] To start, I'll change one letter in "sain" to get closer to "teal." 

I'll change the first letter 's' to 't' to form "tain."

My move: [tain]
[GAME] You've selected a valid word.
('Word Ladder History: sain -> tain. Target Word: teal\n',)
```

By default, the environment returns observations in the following format:
```python
{
  player_id: int : [
    (sender_id: int, message: str),
    (sender_id: int, message: str),
    ...
  ]
}
```

## Gameplay
**Word Length:** The length of the words is customizable, with a default setting of four-letter words. Both the starting and target words are of this length, with other words in the chain matching this requirement.

**Turns:** The player enters words by typing them in the format [word], where each word differs from the previous one by exactly one letter. Players continue to submit words in this format until they reach the target word or exhaust their turns. The game defaults to a maximum of 10 turns.

**Word Graph:** All words of the specified length are represented as nodes in a graph, with edges connecting words that differ by one letter. The start and target words are selected to ensure a valid path exists between them.

**Winning Condition: **The game is won when the player reaches the target word within the allowed number of turns, transforming the start word into the target word through a chain of valid single-letter changes.

## Key Rules
- **Valid Moves**:
    - The player must enter a word that:
        - Is exactly one letter different from the current word.
        - Exists within the game's word list and matches the length of the target word.

- **Invalid Moves**:
    - Entering a word that is not in the list of valid words.
    - Entering a word that does not match the target word length.

- **Incorrect Tries:**
    - Entering a word that differs by more than one letter from the current word.

## Rewards
| Outcome          | Reward for Player  |
|------------------|:------------------:|
| **Win**          |       `+1`         |
| **Draw**         |       `0`          |
| **Invalid Move** |       `-1`         |

## Parameters

- `hardcore` (`bool`):
    - **Description:** Determines the type of words to spot
    - **Impact:**
        - **False:** Hidden words follow basic english.
        - **True**: Hidden words would be uncommon and challenging words.

- `word_len` (`int`):
    - **Description:** Determines the length of the words used in the word graph.
    - **Impact:** Longer words are typically more challenging. 

## Variants

| Env-id                      | hardcore | word_len |
|-----------------------------|:--------:|:--------:|
| `WordSearch-v0-hardcore`    | `True`   | `5`      |
| `WordSearch-v0-hardcore-10` | `True`   | `10`     |

## Example Usage
```python
import textarena as ta

## initializa the environment
env = ta.make("WordLadder-v0-hardcore")

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

## Troubleshooting

**TODO**


## Version History
- **v0**
  - Initial release 


### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg