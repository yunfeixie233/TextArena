# Liar's Dice Environment Documentation

## Overview
**Liar's Dice** is a multi-player bluffing game where each player starts with a set of dice. Players take turns making increasingly higher bids about what dice values are showing among all players' dice. On a player's turn, they can either make a higher bid or challenge the previous player's bid by calling. The game continues until only one player has dice remaining. This environment supports multiple players (2-15) and includes features for bidding, calling bluffs, and tracking dice counts across players.

## Action Space

- **Format:** Actions are strings representing the player's choice:
  - **Bidding:** Players can bid by specifying a quantity and face value in the format `[Bid: X, Y]`, where X is the quantity and Y is the face value.
  - **Calling:** Players can challenge the previous bid by typing `[Call]`.

- **Examples:**
  - Bid 3 dice with face value 4: `[Bid: 3, 4]`
  - Challenge previous bid: `[Call]`

- **Notes:** Players can include additional text in their replies as long as they provide their action in the correct format.

## Observation Space

**Reset Observations**
On reset, each player receives a prompt containing their game instructions and dice information. For example:

```plaintext
You are Player 0 in an N-player Liar's Dice game.
You have 5 dice: 3, 1, 5, 2, 6.
Player 1 has 5 dice.
Player 2 has 5 dice.

Rules:
- On your turn, you may either:
  [1] Make a new bid with a higher quantity or higher face (or both),
  [2] Call the last bid by typing '[Call]'.

If you call:
  - If the actual count of that face value among all dice is less than the bid, the last bidder loses one die.
  - Otherwise, the caller loses one die.
A player who reaches 0 dice is eliminated. The last remaining player wins.

Current bid: Quantity = 0, Face Value = 0
Your action? (e.g. '[Bid: 3, 4]' or '[Call]')
```

**Step Observations**
After each step, players receive updates about actions taken and their consequences. For example:

```plaintext
[Player 1] I'll bid 3 dice with face value 4. [Bid: 3, 4]
[GAME] Player 1 bids 3 of face 4.
[Player 2] That seems like a reasonable bid, but I want to push it further. [Bid: 4, 4]
[GAME] Player 2 bids 4 of face 4.
[Player 0] I think that's too high. [Call]
[GAME] Player 0 calls! The actual count of face 4 is 3, which is LESS than 4.
Player 2 (the last bidder) loses one die.
[GAME] Your new dice are: 2, 4, 3, 6, 1
Remaining dice:
Player 0: 5
Player 1: 5
Player 2: 4
```

## Gameplay

- **Players:** 2-15 players (configurable)
- **Initial Setup:** Each player starts with a set number of dice (default: 5)
- **Turns:** Players take turns either making a higher bid about dice across all players or calling the previous player's bluff
- **Dice:** All dice have 6 faces (1-6)
- **Objective:** Be the last player with dice remaining

## Key Rules

1. **Bidding:**
   - A bid consists of a quantity and a face value (e.g., "4 dice showing face value 3")
   - New bids must increase either the quantity, the face value, or both
   - The first bid can be any valid quantity and face value

2. **Calling:**
   - When a player calls, all dice are revealed to count the actual number of the specified face value
   - If the actual count is less than the bid, the last bidder loses a die
   - If the actual count is equal to or greater than the bid, the caller loses a die

3. **Dice Loss and Elimination:**
   - When a player loses a die, it's removed from their pool
   - A player with zero dice is eliminated from the game
   - After a player loses a die, all remaining players roll new dice for the next round

4. **Winning Conditions:**
   - The last player with dice remaining wins the game

5. **Game Termination:**
   - The game concludes when only one player has dice remaining

## Rewards

| Outcome     | Reward for Winner | Reward for Others |
|-------------|:-----------------:|:-----------------:|
| **Win**     | `+1`              | `-1`              |
| **Lose**    | `-1`              | `0` or `+1`       |
| **Invalid** | `-1`              | `0`               |

## Parameters

- `num_dice` (`int`, default: `5`):
  - **Description:** Sets the initial number of dice each player starts with
  - **Impact:** More dice increase game length and complexity of probability calculations

## Variants

| Env-id                    | num_dice |
|---------------------------|:--------:|
| `LiarsDice-v0`            | `5`      |
| `LiarsDice-v0-larg`       | `12`     |

### Contact
If you have questions or face issues with this specific environment, please reach out directly to guertlerlo@cfar.a-star.edu.sg