# Iterated Stag Hunt Environment Documentation

## Overview
**Iterated Stag Hunt** is a strategic two-player game that presents a conflict between risk and social cooperation [1]. In each round, players have the option to either hunt "stags" or "hares". The outcome of the hunt depends on the players' cooperation: stags can only be hunted successfully if both players commit, while hares can be caught at all times.

This implementation of the game is based on the ``IteratedPrisonersDilemma`` environment that is included in ``TextArena``'s game collection. Just like the ``IteratedPrisonersDilemma``, this version of ``IteratedStagHunt`` allows for multiple communication turns before the players make their final decisions. 

## Action Space
- **Format:** During communication turns, players can send messages to their opponent. On decision turns, players must choose either hunt stags or hares.
- **Communication Actions:**
  - Players send text messages to their opponent during communication turns
  - Example: "I suggest we both cooperate for mutual benefit."
- **Decision Actions:**
  - Players submit either "stag" or "hare" as their final decision, surrounded by square brackets. The game is case-insensitive.
  - Example: ``[Stag]`` or ``[Hare]``.

## Observation Space
**Reset Observations**

On reset, each player receives instructions about the game structure and payoff matrix:

```plaintext
Current observations: 
[GAME] You are Player 0 in an Iterated Stag Hunt game.

Game Structure:
- The game consists of 2 decision rounds
- Before each decision, you have 2 turns to communicate
- After communication, both players simultaneously choose to hunt a Stag or Hare

Rewards:
- The rewards associated with hunting stags and hares may differ between rounds
- The rewards are presented at the start of each round

How to Play:
- During communication: Simply type your message
- During decision phase: Use [Stag] or [Hare]
You can include additional text before or after these tokens.

Starting Round 1
Payoff Matrix:
- Both hunt a Stag: Both get 10 points
- Both hunt a Hare: Both get 5 points
- One hunts a Hare, One hunts a Stag: The hunter of the Hare gets 8 points, the hunter of the Stag gets 1 point

Please enter the action: 

```

**Step Observations**

During communication turns, players receive messages from their opponent:

```plaintext
[Player 0] Let's hunt stags togehter to maximize our score.
```

During decision turns, players may submit their decision:

```plaintext
[GAME] Communication phase complete. Round 1: Please make your decisions.
Please enter the action: 
```

After decision turns, players receive:
1. The actions taken by both players
2. The points awarded for the round
3. The current total scores

```plaintext
[GAME] Round 1 Results:
Both players hunted a stag
Player 0 scored 10, total: 10
Player 1 scored 10, total: 10
```

## Gameplay
- **Players:** 2 (fixed).
- **Rounds:** $n$
- **Turn Structure:**
  - Each round begins with $m$ communication turns where players can exchange messages
  - After communication, each player submits their action (hunt stags or hares)
  - Actions are revealed simultaneously
  - Points are awarded according to the payoff matrix
  - Players receive feedback and prepare for the next round
- **Objective:** Maximize individual score across all $n$ rounds of play

The exact gameplay depends on the registration of the game, see [Registration](#Registration). 

## Key Rules
1. **Action Selection:**
   - Each player must submit exactly one action per decision turn
   - Valid actions are only ``[Stag]`` or ``[Hare]``
   - During communication turns, players can send any message
2. **Payoff Matrix:**

<div style="margin-left: auto;
            margin-right: auto;
            width: 30%">

|      | Stag   | Hare   |
|------|--------|--------|
| Stag | (a, a) | (c, b) | 
| Hare | (b, c) | (d, d) |

</div>

 where a > b ≥ d > c. If a random seed is provided, a new payoff matrix is generated at the start of each round. The payoff matrix is drawn from a uniform distribution, satisfying a > b ≥ d > c. 

3. **Game Duration:**
- Exactly $n$ rounds are played
- Each round includes $m$ communication turns followed by a decision

4. **Invalid Moves:**
- During decision turns, only ``[Stag]`` or ``[Hare]`` are valid actions
- Invalid moves may count as defection or be penalized (implementation-specific)

5. **Winning Conditions:**
- The player with the highest total score at the end of all rounds wins
- Ties are possible if both players have equal scores

## Strategic elements
1. **Communication:** Players can use the $m$ communication turns to build trust, negotiate, or mislead
2. **Trust Building:** Players may establish trust through consistent cooperation
3. **Retaliation:** Players may punish defection with subsequent defection
4. **Forgiveness:** Players may return to cooperation after punishment periods
5. **End-game Strategy:** Knowledge of the final round can influence decisions

## Parameters

- `num_rounds` (`int`):
    - **Description**: Number of rounds for the game
    - **Default**: 10
    - **Impact**: Determines how many opportunities players have to build trust or defect

- `communication_turns` (`int`):
    - **Description**: Number of message exchanges allowed before decisions
    - **Default**: 2
    - **Impact**: Affects how much negotiation can happen before each decision

- `cooperate_reward` (`int`):
    - **Description**: Reward when both players hunt stags
    - **Default**: 10

- `defect_reward` (`int`):
    - **Description**: Reward for hunting hares when the opponent hunts for stags
    - **Default**: 8

- `sucker_reward` (`int`):
    - **Description**: Reward for hunting stags when the opponent hunts for hares
    - **Default**: 1

- `mutual_defect_reward` (`int`):
    - **Description**: Reward when both players hunt for hares
    - **Default**: 5
- `random_seed` (`int`):
    - **Description**: The random seed to use when generating payoff matrices for each round. If `None`, each round has the same payoff matrix. 
    - **Default**: None. 

## References
[1] Miller, Jean-Jacques Rousseau; translated by Donald A. Cress; introduced by James (1992). _Discourse on the origin of inequality._ Indianapolis: Hackett Pub.Co. ISBN 9780872201507.