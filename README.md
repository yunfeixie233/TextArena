# TextArena
A Collection of Competitive Text-Based Games for Language Model Evaluation and Reinforcement Learning




## General TODO
- there should be a dict of standardized game settings (setting i.e. max_turns, hardcore, etc. etc.)
- create an elo script
- update the required package list as necessary
- create minimal example training script
- create SFT dataset
- create loader (and agent wrapper for HuggingFace models)
- add overleaf link to this repo until the write-up is done

## Notes
- the current codenamesmain.py can be better designed with a variable that inits it.; seems rigid to have to call codenamesmain.py. 
- we'd want to add in a 5th result from the env.step() method: obs, rewards, truncated, terminated, info
- explore the use of .wrapper.framestack (or something similar) to capture the historical observations of the game in the current round of game
- action wrappers will be useful. some examples where it can be used are clipping the response from the agent
- rewards wrapper may not be useful in light of us using engineered LLMs
- we have not yet thought about how the community may 'register' new games, e.g.openai gymnasium allows for the registering of games.
- for the games folder structure, we'll categorise them by N-player games. Genre would be fluid, so preferably by N-player.