# TextArena: A Framework for Text-Based Game Environments (**Work in Progress**)

Welcome to **TextArena**, a flexible framework for creating and interacting with text-based game environments. This framework allows developers and researchers to build, customize, and extend environments for language model agents, reinforcement learning, and interactive storytelling.

# TODO
- in the render_wrappers/PrettyRenderWrapper, make the max_log_lines dynamic
- might be worth having a mode where the players only see the game-state (to prevent the other play from just focusing on confusing this player)

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
- [Core Components](#core-components)
  - [Environment Interface](#environment-interface)
  - [Wrapper Classes](#wrapper-classes)
  - [Don't Say It Game](#dont-say-it-game)
- [Creating a New Environment](#creating-a-new-environment)
  - [Step-by-Step Guide](#step-by-step-guide)
- [Extending the Framework](#extending-the-framework)
  - [Custom Observation Wrappers](#custom-observation-wrappers)
  - [Custom Action Wrappers](#custom-action-wrappers)
  - [Custom Render Wrappers](#custom-render-wrappers)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Introduction

**TextArena** provides an abstraction layer for text-based environments, making it easier to develop games and simulations that can interact with language models or other agents. It defines a standard interface for environments and includes wrapper classes for modifying observations, actions, and rendering.

This framework is inspired by OpenAI's Gym interface but tailored for text-based interactions, making it suitable for tasks like conversational AI, text-based games, and multi-agent simulations.

## Getting Started

### Installation

To install TextArena, clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/textarena.git
cd textarena
pip install -r requirements.txt
```

Ensure you have NLTK installed along with the necessary datasets:
```bash
pip install nltk
python -m nltk.downloader words
```

### Basic Usage
Here's a simple example of how to use the **Don't Say It** game environment:
```python
import textarena as ta

# Initialize the environment
env = ta.DontSayItEnv()

# Reset the environment
observations, info = env.reset()

# Play the game
done = False
while not done:
    # Get action from player 0
    action_p0 = input("Player 0: ")
    observations, reward, truncated, terminated, info = env.step(0, action_p0)
    env.render()
    if terminated or truncated:
        break

    # Get action from player 1
    action_p1 = input("Player 1: ")
    observations, reward, truncated, terminated, info = env.step(1, action_p1)
    env.render()
    if terminated or truncated:
        break
```

## Core Components
### Environment Interface
The **Env** class is an abstract base class that defines the standard interface for all environments:
- **reset**: Resets the environment to an initial state.
- **step**: Advances the environment by one step.
- **render**: Renders the current state of the environment.

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

class Env(ABC):
    @abstractmethod
    def reset(self, observations: Optional[Dict[int, str]] = None, seed: Optional[int] = None):
        pass

    @abstractmethod
    def step(self, player_id: int, action: str):
        pass

    @abstractmethod
    def render(self):
        pass

```

### Wrapper Classes
Wrappers allow you to modify the behavior of environments without altering their underlying code. TextArena provides three types of wrappers:
- **ObservationWrapper**: Modifies observations returned by the environment.
- **ActionWrapper**: Transformers actions before passing them to the environment.
- **RenderWrapper**: Enhances or modifies the rendering of the environment.
Each wrapper class inherits from the **Wrapper** base class, which itself inherits from **Env**.

## Creating a New Environment
Creating a new environment involves subcalssing the **Env** class and implementing the required methods. Below is a step-by-step guide to help you create and register a new environment.

### Step-by-Step Guide
1. Import Necessary Modules
```python
from textarena.core import Env
from typing import Any, Dict, Optional, Tuple
```
2. Define Your Environment Class
Subclass the **Env** class.
```python
class MyCustomEnv(Env):
    def __init__(self, your_parameters):
        pass
```
3. Implement the **reset** Method
The **reset** method should initialize the environment and return the initial observations.
```python
def reset(self, seed: Optional[int] = None):
    # Initialize your environment state
    # Return initial observations and info
    return observations, info
```
4. Implement the **step** Method
The **step** method processes an action and returns the result.
```python
def step(self, player_id: int, action: str):
    # Process the action
    # Update the environment state
    # Return observations, reward, truncated, terminated, and info
    return observations, rewards, truncated, terminated, info
```
5. Implement the **render** Method
Optionally, provide a method to render the environment's current state.
```python
def render(self):
    # Output the current state
    pass
```
6. Register Your Environment (Optional)
If you have an environment registry, you can register your new environment for easy access.
```python
from textarena.envs import register_env

register_env('MyCustomEnv-v0', lambda: MyCustomEnv(your_parameters))
```
7. Example
Here's a simple example of a custom environment:
```python
class EchoEnv(Env):
    def reset(self, seed: Optional[int] = None):
        self.state = ""
        return {0: "Start typing to echo your messages."}, {}

    def step(self, player_id: int, action: str):
        self.state += f"Player {player_id}: {action}\n"
        observations = {0: self.state}
        return observations, None, False, False, {}

    def render(self):
        print(self.state)
```

## Extending the Framework
You can create custom wrappers to modify the environment's behavior further.
### Custom Observation Wrappers
Subclass the **ObservationWrapper** to create a custom observation transformation.
```python
from textarena.core import ObservationWrapper

class MyObservationWrapper(ObservationWrapper):
    def observation(self, observations: Optional[Dict[int, str]]):
        # Modify the observations
        return modified_observations
```
### Custom Action Wrappers
Subclass the **ActionWrapper** to transform actions before they reach the environment.
```python
from textarena.core import ActionWrapper

class MyActionWrapper(ActionWrapper):
    def action(self, action: str):
        # Transform the action
        return transformed_action
```
### Custom Render Wrappers
Subclass the **RenderWrapper** to enhance or change the rendering.
```python
from textarena.core import RenderWrapper

class MyRenderWrapper(RenderWrapper):
    def render(self):
        # Custom rendering logic
        pass
```

## Examples
Here are some examples of how to use the provided wrappers and environment.
### Using the LLMObservationWrapper
This wrapper accumulates the full conversation history for language model agents.
```python
from textarena.envs import DontSayItEnv
from textarena.wrappers import LLMObservationWrapper

env = DontSayItEnv()
env = LLMObservationWrapper(env)

observations, info = env.reset()
```

### Limiting Action Length with ClipWordsActionWrapper
```python
from textarena.envs import DontSayItEnv
from textarena.wrappers import ClipWordsActionWrapper

env = DontSayItEnv()
env = ClipWordsActionWrapper(env, max_num_words=50)
```

### Enhancing Rendering with PrettyRenderWrapper
```python
from textarena.envs import DontSayItEnv
from textarena.wrappers import PrettyRenderWrapper

env = DontSayItEnv()
env = PrettyRenderWrapper(env, agent_identifiers={0: 'Alice', 1: 'Bob'})

env.render()
```


## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss changes or additions. This project is part of the Super Tiny Language Models (STLM) research. If you have any questions or concerns, please feel free to join the discord: https://discord.gg/gkrveGUB



# Tutorial: Understanding the Code and Creating a New Environment
This short tutorial will walk you through the structure of the TextArena framework and guide you in creeating and registering a new environment.

## Understanding the Code
### The Environment Interface
At the core of TextArea is the **Env** abstract base class, which defines the standard interface for environments.
- **reset**: Prepares the environment for a new episode
- **step**: Processes an action and updates the environment state.
- **render**: Displays the current state of the environment.
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

class Env(ABC):
    @abstractmethod
    def reset(self, observations: Optional[Dict[int, str]] = None, seed: Optional[int] = None):
        pass

    @abstractmethod
    def step(self, player_id: int, action: str):
        pass

    @abstractmethod
    def render(self):
        pass
```

### Wrapper Classes
Wrappers are powerful tools that allow you to modify or extend the functionality of environments without changing their core logic.
- **ObservationWrapper**: Alters the observations returned by the environment.
- **ActionWrapper**: Modifies actions before they are passed to the environment.
- **RenderWrapper**: Changes how the environment is rendered.
Each wrapper class inherits from the **Wrapper** base class and overrides specific methods to alter behavior.

## Creating a Simple Quiz Game
Here's an example of a simple quiz environment:
```python
import random
from textarena.core import Env
from typing import Any, Dict, Optional, Tuple

class QuizEnv(Env):
    def __init__(self):
        self.questions = [
            ("What is the capital of France?", "Paris"),
            ("What is the smallest prime number?", "2"),
            ("Who wrote '1984'?", "George Orwell")
        ]
        self.current_question = None
        self.is_over = False

    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.current_question = random.choice(self.questions)
        self.is_over = False
        observations = {0: self.current_question[0]}
        info = {}
        return observations, info

    def step(self, player_id: int, action: str):
        if action.strip().lower() == self.current_question[1].lower():
            reward = {player_id: 1}
            self.is_over = True
            observations = {player_id: "Correct!"}
        else:
            reward = {player_id: -1}
            observations = {player_id: "Incorrect. Try again."}
        truncated = False
        terminated = self.is_over
        info = {}
        return observations, reward, truncated, terminated, info

    def render(self):
        print(f"Question: {self.current_question[0]}")
```

## Using Your Environment
```python
env = QuizEnv()
observations, info = env.reset()

done = False
while not done:
    action = input("Your answer: ")
    observations, reward, truncated, terminated, info = env.step(0, action)
    env.render()
    if terminated or truncated:
        break
```
