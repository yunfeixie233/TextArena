# Iterated Prisoner's Dilemma Environment Documentation

## Overview

**Iterated Prisoner's Dilemma** is a strategic two-player game based on the classic game theory scenario. Players must choose to either "cooperate" or "defect" in each round, with their combined choices determining the payoff according to a predefined matrix. This implementation enhances the traditional game by allowing multiple communication turns before players make their final decisions, enabling richer negotiation and strategy development.

The environment is registered as `IteratedPrisonersDilemma-v0` with a fixed number of rounds and customizable reward parameters.

## Action Space

- **Format:** During communication turns, players can send messages to their opponent. On decision turns, players must choose either "cooperate" or "defect."
- **Communication Actions:**
  - Players send text messages to their opponent during communication turns
  - Example: `"I suggest we both cooperate for mutual benefit."`

- **Decision Actions:**
  - Players submit either "cooperate" or "defect" as their final decision
  - Example: `"cooperate"` or `"defect"`

## Observation Space

**Reset Observations**

On reset, each player receives instructions about the game structure and payoff matrix:
```plaintext
[GAME] You are Player 0 in the Iterated Prisoner's Dilemma.
On each turn, you may either "cooperate" or "defect".
Payoff matrix:
  - Both cooperate: 3 points each
  - You cooperate, opponent defects: 0 points for you, 5 for them
  - You defect, opponent cooperates: 5 points for you, 0 for them
  - Both defect: 1 point each
Before making your decision, you will have 3 turns to communicate with your opponent.
```

**Step Observations**

During communication turns, players receive messages from their opponent:
```plaintext
[Player 1] I think we should both cooperate to maximize our collective score.
```

After decision turns, players receive:
1. The actions taken by both players
2. The points awarded for the round
3. Current total scores

Example:
```plaintext
Round result: (cooperate, defect). Scores updated to {Player 0: 0, Player 1: 5}.
```

## Gameplay

- **Players**: 2
- **Rounds**: 10 rounds (fixed)
- **Turn Structure**: 
  1. Each round begins with 3 communication turns where players can exchange messages
  2. After communication, each player submits their action (cooperate/defect)
  3. Actions are revealed simultaneously
  4. Points are awarded according to the payoff matrix
  5. Players receive feedback and prepare for the next round

- **Objective**: Maximize individual score across all 10 rounds of play

## Key Rules

1. **Action Selection**:
   - Each player must submit exactly one action per decision turn
   - Valid actions are only "cooperate" or "defect"
   - During communication turns, players can send any message

2. **Payoff Matrix**:
   | Player 0 | Player 1 | Player 0 Score | Player 1 Score |
   |----------|----------|----------------|----------------|
   | Cooperate| Cooperate| 3              | 3              |
   | Cooperate| Defect   | 0              | 5              |
   | Defect   | Cooperate| 5              | 0              |
   | Defect   | Defect   | 1              | 1              |

3. **Game Duration**:
   - Exactly 10 rounds are played
   - Each round includes 3 communication turns followed by a decision

4. **Invalid Moves**:
   - During decision turns, only "cooperate" or "defect" are valid actions
   - Invalid moves may count as defection or be penalized (implementation-specific)

5. **Winning Conditions**:
   - The player with the highest total score at the end of all rounds wins
   - Ties are possible if both players have equal scores

## Strategic Elements

1. **Communication**: Players can use the 3 communication turns to build trust, negotiate, or mislead
2. **Trust Building**: Players may establish trust through consistent cooperation
3. **Retaliation**: Players may punish defection with subsequent defection
4. **Forgiveness**: Players may return to cooperation after punishment periods
5. **End-game Strategy**: Knowledge of the final round can influence decisions

## Rewards

The reward structure follows the classic Prisoner's Dilemma payoff matrix with the following parameters:

| Parameter              | Value |
|------------------------|:-----:|
| `cooperate_reward`     | 3     |
| `defect_reward`        | 5     |
| `sucker_reward`        | 0     |
| `mutual_defect_reward` | 1     |

| Outcome                       | Player 0 Reward | Player 1 Reward |
|-------------------------------|:---------------:|:---------------:|
| **Both Cooperate**            | +3              | +3              |
| **Player 0 Cooperates, Player 1 Defects** | +0  | +5              |
| **Player 0 Defects, Player 1 Cooperates** | +5  | +0              |
| **Both Defect**               | +1              | +1              |

## Parameters

- `num_rounds` (`int`):
    - **Description**: Number of rounds for the game
    - **Default**: 10
    - **Impact**: Determines how many opportunities players have to build trust or defect

- `communication_turns` (`int`):
    - **Description**: Number of message exchanges allowed before decisions
    - **Default**: 3
    - **Impact**: Affects how much negotiation can happen before each decision

- `cooperate_reward` (`int`):
    - **Description**: Reward when both players cooperate
    - **Default**: 3

- `defect_reward` (`int`):
    - **Description**: Reward for defecting when the opponent cooperates
    - **Default**: 5

- `sucker_reward` (`int`):
    - **Description**: Reward for cooperating when the opponent defects
    - **Default**: 0

- `mutual_defect_reward` (`int`):
    - **Description**: Reward when both players defect
    - **Default**: 1

## Variants

| Env-id                      | Rounds | Communication Turns | Cooperate Reward | Defect Reward | Sucker Reward | Mutual Defect Reward |
|-----------------------------|:------:|:------------------:|:----------------:|:-------------:|:-------------:|:--------------------:|
| `IteratedPrisonersDilemma-v0` | 10     | 3                  | 3                | 5             | 0             | 1                    |



### Contact
If you have questions or face issues with this specific environment, please reach out directly to guertlerlo@cfar.a-star.edu.sg