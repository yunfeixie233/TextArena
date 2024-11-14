# Scenario Planning Environment

## Overview
**Scenario Planning** is a two-player strategic game where each player is presented with the same survival scenario. Players independently propose strategies for survival, and a panel of simulated judges evaluates these strategies based on their effectiveness and feasibility. The player whose strategy is deemed more effective by the judges wins the game.

## Action Space
- **Format:** Actions are strings representing the player's proposed survival strategies.
- **Examples:** 
    - `"Build a shelter using available materials and secure a water source. [...]"`
    - `"Establish a communication system to call for rescue. [...]"`

## Observation Space

### Observations
**Reset Observation:**

On reset, each player receives a prompt containing the scenario and game instructions. For example:
```plaintext
[GAME]: You are Player 0 in the Scenario Planning game.
Scenario: You are stranded on a deserted island with limited resources.
Your goal is to propose a strategy for survival in this scenario.
After both players submit their strategies, a panel of judges will evaluate them.
On your turn, simply type your strategy.
```

**Step Observation:**
The game provides no step-based observations. This is to make sure that neither player has an unfair advantage. 

## Gameplay
- **Players**: 2
- **Turns**: Each player has a single turn to propose their survival strategy.
- **Scenario Assignment**: A random survival scenario is selected at the start of the game.
- **Objective**: Submit the most effective and feasible survival strategy as evaluated by the judges.
- **Judges**: A panel of simulated judges evaluates the submitted strategies to determine the winner.

## Key Rules
1. Strategy Submission:
    - Each player submits a single strategy.
2. Strategy Evaluation:
    - After both players have submitted their strategies, judges evaluate them based on effectiveness and feasibility. Each judge has to vote for one of the two strategies.
3. Winning Conditions:
    - **Win:** The player whose strategy receives more votes by the judges wins the game.
    - **Draw:** If both strategies receive an equal number of votes, the game ends in a draw.
4. Game Termination:
    - The game concludes after both players have submitted their strategies and the judges have evaluated them.

## Rewards
| Outcome          | Reward for Player | Reward for Opponent |
|------------------|:-----------------:|:-------------------:|
| **Win**          | `+1`              | `-1`                |
| **Lose**         | `-1`              | `+1`                |
| **Draw**         | `0`               | `0`                 |

## Parameters
- `num_judges` (`int`):
    - **Description**: Number of simulated judges evaluating the strategies.
    - **Impact**: Affects the granularity and reliability of the evaluation.

- `judge_class` (`ta.JudgeVote`)
    - **Description**: The type of judges used. By default, the `ta.game_makers.GPTJudgeVote` object is used, which utilized a random mix of different openai models.
    - **Impact:** This will significantly impact what types of arguments work well when trying to convince the judges.

- `scenarios_path` (`str`)
    - **Description:** Path to the JSON file containing survival scenarios.
    - **Impact:** Allows customization of the scenarios used in the game.

## Variants

| Env-id                   | num_judges | judge_class    |
|--------------------------|:----------:|:--------------:|
| `ScenarioPlanning-v0`    |    `11`    | `GPTJudgeVote` |


## Example Usage

```python
import textarena as ta

# Initialize the environment
env = ta.make(env_id="ScenarioPlanning-v0")

# Wrap the environment for easier observation handling
env = ta.wrappers.LLMObservationWrapper(env=env)

# Initialize agents
agent0 = ta.default_agents.OpenRouter(model="gpt-4o")
agent1 = ta.default_agents.OpenRouter(model="gpt-4o-mini")


# Reset the environment to start a new game
observations = env.reset()

# Game loop
done = False
while not done:
    for player_id, agent in enumerate([agent0, agent1]):
        # Get the current observation for the player
        obs = observations[player_id]

        # Agent decides on an action based on the observation
        action = agent(obs)

        # Execute the action in the environment
        (
          observations, 
          rewards, 
          truncated, 
          terminated, 
          info
        ) = env.step(player_id, action)

        # Check if the game has ended
        done = terminated or truncated

        # Optionally render the environment
        # env.render()

        if done:
            break

# print the game results
for player_id, agent in enumerate([agent0, agent1]):
    print(f"{agent.agent_identifier}: {rewards[player_id]}")
print(f"Reason: {info['reason']}")
```

## Troubleshooting
- **Invalid Strategy Submission:**
    - **Issue:** A player submits a non-string strategy or an empty string.
    - **Solution:** Ensure that all strategies are valid, non-empty strings representing actionable survival plans.

- **Missing Scenarios File:**
    - **Issue:** The scenarios JSON file is not found at the specified path.
    - **Solution:** Verify the `scenarios_path` parameter and ensure the file exists and is properly formatted.

- **Judge Evaluation Failures:**
    - **Issue:** Judges fail to evaluate strategies.
    - **Solution:** Ensure that you have set your OPEN-AI API key as an envrionment variable (i.e.`export OPENAI_API_KEY="YOUR_API_KEY"`).


## Version History
- **v0**
  - Initial release 



### Contact
If you have questions or face issues with this specific environment, please reach out directly to Guertlerlo@cfar.a-star.edu.sg
