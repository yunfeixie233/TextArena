# Coup

## Rules:


[PDF](https://www.qugs.org/rules/r131357.pdf)
[Video](https://www.youtube.com/watch?v=xUNWl5fWfEY)


## keep this open WHILE you're reading:

The cheatsheet is useful to have on you while going through the code, as much is structured to match as much as possible.
https://hexagamers.com/wp-content/uploads/2016/04/Coup-Cheat-Sheet.jpg






## Environment Structure:

The `CoupEnv` class is primarily understandable by first realizing that Coup can be broken down into two game phases:

 - `PLAY`: a player plays an initial action (ex: Income, Foreign Aid, etc...)

 - `CHALLENGE`: we call on one or more players to challenge an action or call bullshit if they want (ex: Foreign Aid can be counteracted by blocking with Duke, Assassin with Contessa, etc...)

The logic for each phase is branched into two in the `step()` function, specifically by splitting the logic into either `_run_play_phase_step` or `_run_call_phase_step`. Which do pretty much what you expect.


### `_run_play_phase_step(action)`:

when a player plays an action it's either unblockable (Income or Coup), or we enter the `CHALLENGE` phase, where we prod players to counteract or calll bullshit if they so choose.

If it's a `CHALLENGE` phase coming up next, we create a `call_phase_next_players` list with these requirements: 

  - `target_player_id` is ALWAYS first. they get to first dibs on blocking.
  - `source_player_id` is ALWAYS last. once the challenge phase loops back to them, then the action is executed.

### `_run_challenge_phase_step(counteraction)`

this phase does a loop around all players, allowing each of them to either calll bullshit or pass. special exception for the target player. they get to also block the move, too.



## Actions:

In the cheatsheet above you'll notice there are actions and counteractions. Actions are things like Income, Tax, Coup, Assassinate. Counteractions are essentially blocks to actions.

In the code we don't disambiguate between them, they're all the same, just different cases in the `CoupAction` enum.

We also add `BULLSHIT` and `PASS` as actions.

### Note on Special Ambassador Logic:

Playing an Ambassador needs two LLM calls, or two `CoupAction`'s. So the way we do it is as follows:

 - Turn 1: we are in `PLAY` phase, the player does an `Exchange` action. We switch to a `CHALLENGE` phase as usual, allowing players to challenge.
 - Turn N+1: all players haven't challenged, so we are back at the source player after an `Exchange` while being in `CHALLENGE` phase. This triggers two cards to be drawn and a special NEW turn that is UNBLOCKABLE that prompts the LLM to keep two. We challenge this action `Keep`. And it's a made up concept for this turn. After the player keeps, because this is unblockable, we switch back to `PLAY` at the next player in order. 




## `env.py` file:


The file is split into five "blocks" of functions:


### Block 1: Boring boilerplate stuff

 - `__init()__`: just a stub.
 - `reset()`: initializes game state, cards and stuff. Nothing magic here.
 - `step()`: logs given string and punts off the work to other functions


### Block 2: 


### Block 3: Prompt Generation


### Block 4: Game Adjustments


### Block 5: Helper functions


# Limitations:

 - Players don't choose which card to reveal if they have more than one, we just pick the first card in their hand (arbitrarily) see: `make_player_lose_card(player_id)`
 <!-- - You can't challenge a block. This is not an easy fix, requires a backtracking and special logic I don't want to do. -->
 - In real life, people can yell bullshit at any time, including BEFORE a potentially affected player gets the chance to counteract. We disregard this
possibility and assume that the affected player gets first dibs on whether or not to counteract. Then we ask the rest of the players if they wish to challenge bullshit.


# TODO: 

  - [ ] Implement Exchange action logic
  - [ ] Maybe remove the coins_remaining state variable?
  - [ ] Test the failed challenge assassin insta-kills the player