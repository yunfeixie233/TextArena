# Blackjack Environment Documentation

## Description
The Blackjack environment is a single-player card game where the player competes against a dealer to score as close to 21 as possible without going over. The player chooses between `[Hit]` to draw a card or `[Stand]` to end their turn. Aces count as either 1 or 11, whichever is more favorable. The game proceeds over multiple hands, and the player’s final reward is based on their win rate. The environment supports both short and extended variants with configurable hand counts, making it suitable for evaluating decision-making under uncertainty and probabilistic reasoning.

## Game-flow
At the beginning of the game, the player will receive the game prompt and initial board state as an observation:
```plaintext
[GAME] You are playing Blackjack against the dealer.
Your goal is to get as close to 21 as possible without going over.
On your turn, choose '[Hit]' to draw another card or '[Stand]' to hold.
J/Q/K = 10 points; A = 11 or 1, whichever is better.

[GAME] Hand 1/5
Your hand: 4♣, 10♠ (Score: 14)
Dealer shows: K♣
```

Subsequently, after the player can chose to `[hit]` or `[stand]`. After every hit, the player will see their new card and total current score:
```plaintext
[GAME] Hand 2/5
Your hand: 2♣, A♦, 3♠ (Score: 16)
```
When going bust or standing, the round outcome is revealed:
```plaintext
Hand 2: you bust. Your final 23, Dealer 9.
```


## Reward Design
- Invalid move -> Reward `-1`
- Otherwise -> Reward ∝ pct. of hands won


## Environment Parameters
- `num_hands` (`int`)
- Description: The number of hands to be played.

## Variants

| Env-id                      | num_hands |                Wrappers Used                     |
|-----------------------------|:---------:|:-----------------------------------------------: |
| `Blackjack-v0`              | `5`       |`LLMObservationWrapper`, `ActionFormattingWrapper`| 
| `Blackjack-v0-long`         | `15`      |`LLMObservationWrapper`, `ActionFormattingWrapper`| 
| `Blackjack-v0-raw`          | `5`       |`None`                                            | 
| `Blackjack-v0-raw-long`     | `15`      |`None`                                            | 


### Contact
If you have questions or face issues with this specific environment, please reach out directly to guertlerlo@cfar.a-star.edu.sg

