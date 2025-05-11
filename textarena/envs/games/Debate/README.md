# Debate Environment

## Overview
**Debate** is a two-player game where each player is assigned a side on a given topic—either Affirmative or Negative. Players present arguments in turns to convince a panel of simulated judges. The winner is determined by the change in judges' opinions before and after the debate.

## Action Space
- **Format:** Actions are strings representing the player's arguments.
- **Example:** 
    - `"I believe that technology improves our lives because..."`
    - `"My opponent overlooks the fact that..."`

## Observation Space

### Observations
Each player receives messages exchanged during the debate, including their assigned topic and position.

**Initial Observation:**
```plaintext
You are Player {player_id} in the Debate game.
Topic: {topic}
Your position: {'Affirmative'|'Negative'}
You will have {max_turns} turns to present your arguments.
On your turn, simply type your argument.
```

**Turn Observation:**
After each step, players receive the latest argument. For example:
```plaintext
[Player 0]: While the idea of free education for all citizens sounds appealing, it is important to consider the economic implications and potential drawbacks. Implementing a system of free education would require substantial funding, which would likely result in increased taxes or budget cuts in other critical areas such as healthcare, infrastructure, or social services. This could place a strain on the economy and potentially lead to negative consequences for citizens in other aspects of their lives. Additionally, without the financial investment from students and their families, educational institutions may face challenges in maintaining the quality of education, as they may struggle to attract and retain qualified teachers, update their facilities, and provide necessary resources. Therefore, it is crucial to weigh the economic costs and potential impacts on educational quality before embracing free education for all.
```

## Gameplay
- **Players**: 2
- **Turns**: Players alternate presenting arguments.
- **Topic Assignment**: A debate topic is randomly selected at the start.
- **Position Assignment**: One player is randomly assigned the Affirmative side; the other is assigned the Negative side.
- **Objective**: Convince the jury to change their opinions in favor of your side.
- **Jury**: A panel of simulated jurors evaluates the debate.
- **Turn Limit**: The number of back and forths before the jury makes their decision.

## Key Rules
1. Debate Structure:
    - Each player has a set number of turns to present their arguments.
    - Players alternate turns.
2. Judge Evaluation:
    - **Pre-Debate Vote:** The Jury votes based solely on the topic before the debate begins.
    - **Post-Debate Vote:** The Jury votes again after the debate concludes; this time based on the topic and debate transcript.
    - **Winner Determination:** The player whose side gains the most votes compared to the pre-debate vote wins. If the votes remain unchanged, the game ends in a draw.
3. Winning Conditions:
    - **Win:** Achieve a higher increase in jury votes for your side compared to the opponent.
    - **Draw:** If both sides gain an equal number of votes, the game ends in a draw.
4. Game Termination:
    - The game ends after all turns are completed and the judges have re-evaluated their votes.



## Rewards
| Outcome          | Reward for Player | Reward for Opponent |
|------------------|:-----------------:|:-------------------:|
| **Win**          | `+1`              | `-1`                |
| **Lose**         | `-1`              | `+1`                |
| **Draw**         | `0`               | `0`                 |

## Parameters
- `max_turns` (`int`):
    - **Description**: Number of turns per player
    - **Impact**: Determines the length of the debate

- `jury_size` (`int`):
    - **Description**: Number of simulated jurors evaluating the debate.
    - **Impact**: Affects the granularity of jury opinion changes.

- `jury_class` 
    - **Description**: The type of Jury used. By default, the `ta.envs.utils.OpenRouterJury` object is used, which utilized a random mix of different LLMs.
    - **Impact:** This will significantly impact what types of arguments work well when trying to convince the jury.

- `topics_path` (`str`)
    - **Description:** Path to the JSON file containing debate topics.
    - **Impact:** Allows customization of the topics used in the debates.

## Variants

| Env-id                   | max_turns | jury_size | jury_class       |
|--------------------------|:---------:|:----------:|:----------------:|
| `Debate-v0`              | `6`       | `7`        | `OpenRouterJury` |
| `Debate-v0-medium`       | `12`      | `9`        | `OpenRouterJury` |
| `Debate-v0-long`         | `30`      | `13`       | `OpenRouterJury` |



### Contact
If you have questions or face issues with this specific environment, please reach out directly to Guertlerlo@cfar.a-star.edu.sg
