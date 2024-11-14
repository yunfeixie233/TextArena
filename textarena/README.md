# Basic Agent Documentation

This module provides the agent framework to facilitate interaction with various language models, including human input, OpenRouter API for OpenRouter models, and Hugging Face models. Each agent inherits from a generic `Agent` class and implements the `__call__` method to process observations and return responses.

## Agents

### 1. Agent (Abstract Base Class)
The `Agent` class is an abstract base class that defines the structure for all agents. It includes the following:
- **Attributes**:
  - `model_name`: Name of the model being used.
- **Method**:
  - `__call__(observation: str) -> str`: Abstract method to process observations and generate a response.

### 2. HumanAgent
The `HumanAgent` class allows manual input from a user in response to an observation, making it suitable for testing or demonstration purposes where a human agent’s decision is required.
- **Attributes**:
  - Inherits all attributes from `Agent`.
- **Method**:
  - `__call__(observation: str) -> str`: Prints the observation and prompts the user to input an action manually.

### 3. OpenRouter
The `OpenRouter` class uses the OpenRouter API to interact with GPT models hosted by OpenAI.
- **Initialization**:
  - Requires the environment variable `OPENAI_API_KEY` to authenticate with the OpenRouter API.
  - Optional `system_prompt` parameter to define the initial behavior of the model.
- **Attributes**:
  - `client`: OpenRouter API client instance.
  - `system_prompt`: Initial prompt to define the agent's behavior (default: "You are a competitive game player").
- **Method**:
  - `__call__(observation: str) -> str`: Sends the observation to the OpenAI model via OpenRouter and returns the generated response.
- **Error Handling**:
  - If the API call fails, an error message is returned.

### 4. HFLocalAgent
The `HFLocalAgent` class loads and uses models from the Hugging Face Transformers library for local inference.
- **Initialization**:
  - Requires the environment variable `HF_ACCESS_TOKEN` to download models.
  - Optional `quantize` parameter to enable 8-bit model quantization for reduced memory usage.
- **Attributes**:
  - `tokenizer`: Tokenizer for text preprocessing.
  - `model`: Language model for text generation, quantized if specified.
  - `pipeline`: Hugging Face pipeline for text generation.
- **Method**:
  - `__call__(observation: str) -> str`: Processes the observation locally using Hugging Face and returns the generated response.
- **Error Handling**:
  - If model inference fails, an error message is returned.

## Installation and Setup

1. **Install Dependencies**:

Make sure you have the required libraries installed:

   ```bash
   pip install openai transformers
   ```

2. **Environment Variables**:

- `OPENAI_API_KEY`: Required for OpenRouter agent to access OpenRouter models.
- `HF_ACCESS_TOKEN`: Required for HFLocalAgent to download HuggingFace models

3. **Usage Example**:
```python
# Initialize an agent
import basic_agents

agent = basic_agents.OpenRouter(model_name="gpt-3.5-turbo")

# Process an observation
response = agent("What is the weather like today?")
print(response)
```

## Contributing
To add new agents or improve existing ones, please follow the contribution guidelines. For each new agent, ensure it inherits from `Agent` and implements the `__call__` method to maintain a consistent interface.
