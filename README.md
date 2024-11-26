# **Work in Progress - official launch: 01.12.2024**


# TextArena: A Framework for Text-Based Game Environments 

Welcome to **TextArena**, a flexible framework for creating and interacting with text-based game environments. This framework allows developers and researchers to build, customize, and extend environments for language model agents, reinforcement learning, and interactive storytelling.


## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
- [Core Components](#core-components)
  - [Environment Interface](#environment-interface)
  - [Wrapper Classes](#wrapper-classes)
  - [Basic Agents](#basic-agents)
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
pip install textarena
```

Ensure you have NLTK installed along with the necessary datasets:
```bash
pip install nltk
python -m nltk.downloader words
```


### Basic Usage
Here's a simple example of how to use the **Don't Say It** game environment with two LLMs
```python
import textarena as ta

# initialize the agents
agents = {
    0: ta.basic_agents.OpenRouter(model_name="GPT-4o"),
    1: ta.basic_agents.OpenRouter(model_name="GPT-4o-mini"),
}

# Initialize the environment
env = ta.make(env_id="Negotiation-v0")

# Wrap the environment in the LLMObservation wrapper
env = ta.wrappers.LLMObservationWrapper(env=env)

# Wrap the environment for nice rendering
# env = ta.TkinterRenderWrapper(
#     env=env,
#     player_names={
#         0: "GPT-4o",
#         1: "GPT-4o-mini",
#     },
#     enable_recoding=False
# )

# Reset the environment
observations = env.reset()

# Play the game
terminated, truncated = False, False
while not (terminated or truncated):
    # get the current player id 
    current_player_id = env.get_current_player_id()

    # get the action
    action = agents[current_player_id](
        observations[current_player_id]
    )

    # step in the environment
    observations, rewards, truncated, terminated, info = env.step(
        player_id=current_player_id,
        action=action
    )

# close the environment
env.close()
```
The above example provides a basic understanding of the game flow, showcasing how players interact with the environment in turns. The **LLMObservationWrapper** is used to accumulate and convert the player observations (a list of tuples, where each tuple contains the sender id, and message), into a single string.


### Basic Online Usage
Here's a simple example of how to evaluate your model online in the **Don't Say It** game environment:
```python
import textarena as ta

model_name = "GPT-4o demo model"

# Register the model 
model_token = ta.register_online_model(
    model_name=model_name,
    model_description="OpenAI's GPT-4o model with the default prompt.",
    email="Guertlerlo@cfar.a-star.edu.sg"
) # please save the model token somewhere, you can't register the same model twice


# initialize the agent
agent = ta.basic_agents.OpenRouter(model_name="GPT-4o"),

# Initialize the online environment
env = ta.make_online(
    env_id="DontSayIt-v0",
    model_name=model_name,
    model_token=model_token
)

# Wrap the environment in the LLMObservation wrapper
env = ta.wrappers.LLMObservationWrapper(env=env)

# Reset the environment
observations = env.reset()

# Play the game
terminated, truncated = False, False
while not (terminated or truncated):
    # get the current player id 
    current_player_id = env.get_current_player_id()

    # get the action
    action = agents(observations[current_player_id])

    # step in the environment
    observations, reward, truncated, terminated, info = env.step(
        player_id=current_player_id,
        action=action
    )

    # Optimally, render the environment
    # env.render()

# print the game outcome and change in elo
env.print_results()
```
We tried to keep the transition from offline to online model as simple as possible. The key components are the **register_online_mmodel** and **make_online** functions. For the former, please make sure that you provide a valid e-mail address and a unique model name. Please also note down your model_token. You won't be able to register the same model twice, and besides us sending you the token manually, there currently exists no mechanism for you to get the token again. The **make_online** works very similarly to **make**. The key difference is that you are required to provide the model_name and model_token as well.


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

### Basic Agents
The **basic_agents** module defines a set of pre-built agents that can interact with TextArena environments by processing observations and generating actions. Each agent class extends a generic Agent base class, which sets up a structure for handling observations and deciding on actions. These agents offer versatile interaction methods:

- **HumanAgent**: Allows manual input, making it useful for testing or interactive play.
- **OpenRouter**: Connects to OpenRouter's API to use models like GPT-4o-mini, requiring an API key and customizable prompts.
- **HFLocalAgent**: Utilizes Hugging Face’s Transformers library to run models locally, with optional quantization for performance efficiency.

Each agent can be used out-of-the-box or customized further by subclassing the Agent class, allowing for flexible experimentation in various text-based games and tasks. Here's an example of how each can be loaded into the script.

#### Requirements

Some agents require environment variables for proper configuration:

- **`OPENAI_API_KEY`**: Required by the `OpenRouter` agent to access OpenRouter models. Set this variable to your OpenAI API key.
- **`HF_ACCESS_TOKEN`**: Required by the `HFLocalAgent` to download models from the Hugging Face Hub. Set this variable to your Hugging Face access token.

To set these variables, use the following commands in your terminal:

```bash
export OPENAI_API_KEY=your_openai_api_key_here
export HF_ACCESS_TOKEN=your_huggingface_access_token_here
```

Alternatively, you can add them to your .env file if you're using a tool like dotenv in Python.

#### Example Usage

##### 1. Using a human agent
```python
# Initialize an agent
import textarena.basic_agents as basic_agents

agent = basic_agents.HumanAgent(model_name="Napolean")

# Process an observation
response = agent("Is the hat just for the vibe?")
print(response)
```

##### 2. Using the OpenRouter API
Ensure the `OPENAI_API_KEY` is set before running this example.
```python
# Initialize an agent
import textarena.basic_agents as basic_agents

agent = basic_agents.OpenRouter(model_name="gpt-3.5-turbo")

# Process an observation
response = agent("What is the weather like today?")
print(response)
```

##### 3. Using the Huggingface API
Ensure the `HF_ACCESS_TOKEN` is set before running this example.
```python
# Initialize an agent
import textarena.basic_agents as basic_agents

agent = basic_agents.HFLocalAgent(model_name="meta-llama/Llama-3.2-1B-Instruct", quantize=False)

# Process an observation
response = agent("Why is Friday a happy day?") # Because the next day is called Saturday (which sounds like sadder day...)
print(response)
```


## Creating a New Environment
Creating a new environment involves subclassing the **Env** class and implementing the required methods. Below is a step-by-step guide to help you create and register a new environment. For an actual implementaion, read the section [Tutorial: Understanding the Code and Creating a New Environment](#tutorial-understanding-the-code-and-creating-a-new-environment)

### Step-by-Step Guide
1. Import Necessary Modules.
```python
from textarena.core import Env
from typing import Any, Dict, Optional, Tuple
```
2. Define Your Environment Class.
Subclass the **Env** class.
```python
class MyCustomEnv(Env):
    def __init__(self, your_parameters):
        pass
```
3. Implement the **reset** Method.
The **reset** method should initialize the environment and return the initial observations.
```python
def reset(self, seed: Optional[int] = None):
    # Initialize your environment state
    # Return initial observations 
    return observations
```
4. Implement the **step** Method.
The **step** method processes an action and returns the result.
```python
def step(self, player_id: int, action: str):
    # Process the action
    # Update the environment state
    # Return observations, reward, truncated, terminated, and info
    return observations, rewards, truncated, terminated, info
```
5. Implement the **render** Method.
Provide a method to render the environment's current state.
```python
def render(self):
    # Output the current state
    pass
```
6. Register Your Environment (Optional).
If you have an environment registry, you can register your new environment for easy access.
```python
from textarena.envs import register_env

register_env('MyCustomEnv-v0', lambda: MyCustomEnv(your_parameters))
```
7. Example.
Here's a simple example of a custom environment:
```python
class EchoEnv(Env):
    def reset(self, seed: Optional[int] = None):
        self.state = ""
        return {0: "Start typing to echo your messages."}

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
Contributions are welcome! Please submit a pull request or open an issue to discuss changes or additions. This project is part of the Super Tiny Language Models (STLM) research. If you have any questions or concerns, please feel free to join the discord: https://discord.gg/KMndsqwMaZ




# Tutorial: Understanding the Code and Creating a New Environment
This short tutorial will walk you through the structure of the TextArena framework and guide you in creating and registering a new environment.

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
<!-- I don't think this is needed because the simple quiz example doesn't use any wrappers... -->
<!-- ### Wrapper Classes
Wrappers are powerful tools that allow you to modify or extend the functionality of environments without changing their core logic.
- **ObservationWrapper**: Alters the observations returned by the environment.
- **ActionWrapper**: Modifies actions before they are passed to the environment.
- **RenderWrapper**: Changes how the environment is rendered.
Each wrapper class inherits from the **Wrapper** base class and overrides specific methods to alter behavior. -->

## Creating a Simple Quiz Game
Here's an example of a simple quiz environment that randomly selects a question and prompts the human agent for an answer whilst keeping track of its number of tries:
```python
import random
import textarena as ta
from typing import Any, Dict, Optional, Tuple

class QuizEnv(ta.Env):
    def __init__(self):
        self.questions = [
            ("What is the capital of France?", "Paris"),
            ("What is the smallest prime number?", "2"),
            ("Who wrote '1984'?", "George Orwell")
        ]
        self.current_question = None
        self.is_over = False
        self.num_tries = 0

    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.current_question = random.choice(self.questions)
        self.is_over = False
        observations = {0: self.current_question[0]}
        return observations

    def step(self, player_id: int, action: str):
        self.num_tries += 1
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
        if self.is_over:
            print("You got the right answer!")
        else:
            print(f"Number of tries: {self.num_tries}")
```

## Using Your Environment
```python
env = QuizEnv()
observations = env.reset()

agent = ta.basic_agents.HumanAgent(model_name="Napolean")

done = False
while not done:
    obs = observations[0]
    action = agent(obs)
    observations, reward, truncated, terminated, info = env.step(0, action)
    env.render()
    if terminated or truncated:
        break
```
