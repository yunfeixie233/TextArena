# Bandit Environment Documentation

## Overview
The task in the Bandit environment is Best-Arm Identification. The agent pushes buttons and observes rewards for a fixed number of turns. Afterward, the player tries to deduce the button with the highest average return. The game encourages strategic exploration. 

## Action Space
- **Format:** Actions must be valid buttons of the form `[Button]`. 
- **Example:**
    - Available buttons: red, blue, green, yellow, purple. Next action: [blue]

## Observation Space
**Reset Observation:**
```plaintext
[GAME] You are in a room with 5 buttons: red, blue, green, yellow, purple. Each button is associated with a Bernoulli distribution with a fixed but unknown mean; the means for the buttons could be different.
For each button, when you press it, you will get a reward that is sampled from associated distribution.
You have 20 time steps and, on each time step, you can choose any button and receive the reward.
Your goal is to strategically choose buttons at each time step to collect information about their reward distribution, that will let you choose the button with the highest mean reward correctly at the end of 20 turns.
```

**Step Observation:**
After pushing a button the player receives a reward sample as the observation:
```plaintext
You pressed the red button and received a reward of 1.
```
When the maximum number of steps is reached, the agent is prompted to deduce the final action:
```plaintext
You have exhausted your budget for trying out different choices and observe their rewards. Now make a deduction about what the best choice is.
```