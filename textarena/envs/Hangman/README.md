# Hangman Environment Documentation

## Description
The Hangman environment is a single-player word-guessing game where the player attempts to guess a hidden word by suggesting letters or guessing the entire word. The objective is to reveal the correct word before the player runs out of attempts. The environment supports a "hardcore" mode where a more extensive vocabulary is used, adding to the difficulty.

## Observations
At the beginning of the game, the player will receive the game prompt and initial board state as an observation:
```plaintext
[GAME] You are playing Hangman. The objective of the game is to guess the word by providing one letter guesses or the entire word.
Each column is numbered. The cells that need to be populated with letters are represented by '_'.

There are two ways you can answer. You can provide one letter guesses in the format of '[L]', or you can guess the entire word in the format of '[LIGHT]'.
If the given letter is in the word, it will be revealed in the grid.
If the given word is correct, you win.
As you play, the history of your choices will be appended below. Use the information to figure out the word and win.
You have 6 incorrect tries before the game ends.

Current Hangman Grid:
C00 C01 C02
  _   _   _ 
```

Subsequently, after every guess the Player will recieve either `[GAME] Your guess of A is in the word` or `[GAME] Your guess of P is not in the word. You have 5 lives left.`, followed by the updated board state:

```plaintext
[GAME] C00 C01 C02
  _   A   _ 
```

## Actions
At each turn, the player can submit a guess for a single letter (i.e. `[s]`) or a guess for the complete word (i.e. `[math]`).


## Reward Design
- Game completion -> Reward `1`
- Invalid move -> Reward `-1`
- Turn limit -> Reward ∝ pct. of correct letters


## Environment Parameters
- `hardcore` (`bool`) - Sets the difficulty level of the game by determining the vocabulary size from which words are chosen.

## Variants

| Env-id                    | hardcore |                Wrappers Used                     |
|---------------------------|:--------:|:-----------------------------------------------: |
| `Hangman-v0`              | `False`  |`LLMObservationWrapper`, `ActionFormattingWrapper`| 
| `Hangman-v0-hardcore`     |  `True`  |`LLMObservationWrapper`, `ActionFormattingWrapper`| 
| `Hangman-v0-raw`          | `False`  |`None`                                            | 
| `Hangman-v0-raw-hardcore` |  `True`  |`None`                                            | 


### Contact
If you have questions or face issues with this specific environment, please reach out directly to bobby_cheng@i2r.a-star.edu.sg

