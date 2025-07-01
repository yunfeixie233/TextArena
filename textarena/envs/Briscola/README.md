# Briscola Environment Documentation

## Overview
**Briscola** simulates the traditional Italian card game *Briscola*, a trick-taking game played with a 40-card deck. The objective is to win tricks and collect the highest number of card points. Each card has a point value and a power ranking used to determine trick winners. Trump cards beat all non-trump cards, regardless of power.

The game ends when all cards have been played. The player with the most points wins.

## Gameplay

- **Players:** 2 to 4 (supports both two-player and multi-player modes)
- **Initial Setup:** Each player is dealt 3 cards (or 2 if 4 players). A trump suit is determined by revealing the last card of the deck.
- **Objective:** Win tricks to accumulate card points. The player with the highest score at the end wins.

## Card Values

| Card       | Value  |
|------------|--------|
| Ace (A)    | 11     |
| Three (3)  | 10     |
| King (K)   | 4      |
| Queen (Q)  | 3      |
| Jack (J)   | 2      |
| 2–7        | 0      |

## Card Strength (Power)

| Card       | Strength (High → Low) |
|------------|------------------------|
| Ace (A)    | 8                      |
| 3          | 7                      |
| King (K)   | 6                      |
| Queen (Q)  | 5                      |
| Jack (J)   | 4                      |
| 7          | 3                      |
| 6          | 2                      |
| 5          | 1                      |
| 4          | 0                      |
| 2          | -1                     |

- **Trump cards** beat all non-trump cards, regardless of their power.
- Among trump cards or cards of the same suit, the higher power wins.

## Actions

Players take turns to play a single card from their hand:

```bash
[play X]
```
where `X` is the 1-based index of the card in the player's hand.

### Example
```bash
[play 2]
```
This plays the second card in your current hand.

## Game Flow

1. Trump suit is determined from the last card in the shuffled deck.
2. Players take turns playing cards into the current trick.
3. Once all players have played, the trick is resolved:
   - If any trump card is played, the highest trump wins.
   - If no trump, the highest card of the leading suit wins.
4. The winner takes the trick and gains the total point value of the cards.
5. Players draw one new card from the deck if available.
6. Repeat until the deck and player hands are empty.

## End Condition

The game ends when no cards are left to play. The player with the most total points wins.

## Rewards

| Outcome               | Reward |
|------------------------|--------|
| Win (most points)      | `+1`   |
| Lose                   | `-1`   |
| Invalid Move           | `-1`   |

## Observation Space

Each turn, players receive:

- A prompt with their current hand (including trump indicators and card values)
- The current trick state
- Score summaries
- Trump suit and number of cards left in deck

### Example Prompt
```bash
[GAME] You are playing Briscola - Player 0.
Goal: Win tricks and collect the most points (120 total points in the deck).
Card Points: A=11, 3=10, K=4, Q=3, J=2, others=0
Card Power: A > 3 > K > Q > J > 7 > 6 > 5 > 4 > 2
Trump cards beat non-trump cards regardless of power.

Action: '[play X]' where X is the position (1-3) of the card in your hand

[GAME] Briscola game started! Trump suit: ♦ (Trump card: A♦)
[GAME] Your hand:
  1. 2♥ [0 pts]
  2. K♣ [4 pts]
  3. 3♥ [10 pts]

No cards played yet this trick.

Scores: Player 0: 0 pts | Player 1: 0 pts
Trump suit: ♦ | Cards left in deck: 34

Play a card using [play X]
```


## Available Environments

| Env-id         | Mode         |
|----------------|--------------|
| `Briscola-v0`  | 2–4 players  |

## Installation

Ensure your environment has the `textarena` framework installed. Then, register and use `BriscolaEnv` in your training or evaluation code.

## Contact

For issues or feedback related to this environment, contact:

**Email:** `chengxy@i2r.a-star.edu.sg`

