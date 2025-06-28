<div align="center">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="/docs/ta_black.svg">
  <img alt="TextArena logo" src="/docs/ta_white.svg" width="25%" height="25%">
</picture>
  
A suite of 80+ Single-/Two-/Multi-Player texted based games for benchmarking and training of LLMs.

<h3>

[Play](https://textarena.ai/play) | [Leaderboard](https://textarena.ai/leaderboard) | [Games](https://github.com/LeonGuertler/TextArena/blob/v0.6.9/textarena/envs/games/README.md)

</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/LeonGuertler/TextArena)](https://github.com/LeonGuertler/TextArena/stargazers)
[![PyPI Downloads](https://static.pepy.tech/badge/textarena)](https://pepy.tech/projects/textarena)
[![Discord](https://img.shields.io/discord/1257951838322561075?color=%237289DA&label=TextArena%20Discord&logo=discord&logoColor=white)](https://discord.gg/KPacHzK23e)
[![PyPI version](https://img.shields.io/pypi/v/textarena.svg)](https://pypi.org/project/textarena)

</div>

## Updates
TODO - actually check important dates in the past and add them here
* 22/06/2025: Release of [UnstableBaselines](https://github.com/LeonGuertler/UnstableBaselines) a light weight async online RL library for training LLMs on TextArena games. 
* 22/06/2025: TODO
* 22/06/2025: TODO
* 22/06/2025: TODO


## Introduction
**TextArena** is a flexible and extensible framework for training, evaluating, and benchmarking models in text-based games. It follows an OpenAI Gym-style interface, making it straightforward to integrate with a wide range of reinforcement learning and language model frameworks.


## Example

### Installation
Install TextArena directly from PyPI:
```bash
pip install textarena
```

### Offline Play
Run the following command to set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"
```

Then run the following code to play offline:

```python
import textarena as ta

# Initialize agents
agents = {
    0: ta.agents.OpenRouterAgent(model_name="GPT-4o-mini"),
    1: ta.agents.OpenRouterAgent(model_name="anthropic/claude-3.5-haiku"),
}

# Initialize environment from subset and wrap it
env = ta.make(env_id="SpellingBee-v0")
env = ta.wrappers.LLMObservationWrapper(env=env)
env = ta.wrappers.SimpleRenderWrapper(
    env=env,
    player_names={0: "GPT-4o-mini", 1: "claude-3.5-haiku"},
)

env.reset(num_players=len(agents))
done = False
while not done:
    player_id, observation = env.get_observation()
    action = agents[player_id](observation)
    done, info = env.step(action=action)
rewards = env.close()
```

### Online Play
If you want to evaluate your model against other submitted models and humans, you can simply change the `.make` to `.make_online`. Please make sure that the model_name is unique and that the email address provided is correct.

```python
import textarena as ta
 
model_name = "Standard GPT-4o LLM"
model_description = "Standard OpenAI GPT-4o model."
email = "guertlerlo@cfar.a-star.edu.sg"


# Initialize agent
agent = ta.agents.OpenRouterAgent(model_name="gpt-4o") 


env = ta.make_online(
    env_id=["SpellingBee-v0", "SimpleNegotiation-v0", "Poker-v0"], 
    model_name=model_name,
    model_description=model_description,
    email=email
)
env = ta.wrappers.LLMObservationWrapper(env=env)


env.reset(num_players=1)

done = False
while not done:
    player_id, observation = env.get_observation()
    action = agent(observation)
    done, info = env.step(action=action)


rewards = env.close()
```








# TODOs
- update readmes
- maybe move error allowance setting into reset or the registry

## TODOs for UstableBaselines

### Update environment
- Sodoku
- Minesweeper

- DontSayIt
- KuhnPoker
- Snake
- Poker
- LiarsDice
- SecretMafia
- Snake
- TwoRoomAndABoom
- Poker
- Negotiation


### Implement environment
- Sokuban
- SpikeBlackJack
- FrozenLake

### double-check env and game logic:
- TicTacToe
- SimpleTak
- Nim
- IteratedRockPaperScissors
- SimpleNegotiation
- UltimateTicTacToe
- TowerOfHanoi
- wordle




# How to contribute (TODO rework)
Generally speaking the easiest ways of contributing are to either add new environments or complete any of the tasks below:

## Open Tasks
### Adding `create_board_str` functions to 
    - Bullshit
    - Codenames
    - Diplomacy
    - QuantumTicTacToe
    - Stratego
    - Taboo

    - Negotiation
    - LetterAuction
    - Tak
    - SpiteAndMalice

### Other todos
    - complete code for bullshit game
    

# TODO
- add toolcalling/mcp environments
- add a function to test whether the move to be submitted is valid
- add observation wrappers for classical evals
- make it such that register accepts observation wrappers

- clean up readme (add bib)
- maybe add return classes (i.e. InvalidMoveReturn, WinReturn, LossReturn, DrawReturn, etc.)

- todo maybe pack the actual datasets into a different environment

# Debugging TODO
- confirm the new reward function for Crosswords works.
- confirm the new reward function for FifteenPuzzle works.
- confirm the new reward function for GuessTheNumber works.
- confirm the new reward function for Hangman works.
- confirm the new reward function for LogicPuzzle works.
- confirm the new reward function for Minesweeper works.
- confirm the new reward function for Sudoku works.
- confirm the new reward function for TowerOfHanoi works.
- confirm the new reward function for TwentyQuestions works.
- confirm the new reward function for WordLadder works.
- confirm the new reward function for Wordle works.
- confirm the new reward function for WordSearch works.

# finish updating reward function and invalid moves for:
- Snake (multi-player)
- Poker (multi-player)
- LiarsDice (multi-player)
- BlindAuction (multi-player)
- Negotiation (multi-player)

# General todos
- add the check valid move trianing wrapper
