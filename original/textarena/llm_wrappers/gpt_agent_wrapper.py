import openai
from typing import Any, Dict, Optional, Tuple, List
from .agent_interface import AgentInterface 

class GPTAgent(AgentInterface):
    """
    GPT-based Agent utilizing OpenAI's API to generate actions for the game.
    """

    def __init__(
        self, 
        unique_identifier: str, 
        api_key: str, 
        verbose: bool = False, 
        max_tokens: int = 1000, 
        model_name: str = "gpt-4"
    ):
        """
        Initialize the GPTAgent with the specified parameters.

        Args:
            unique_identifier (str): A unique identifier for the agent.
            api_key (str): Your OpenAI API key.
            verbose (bool, optional): Flag to enable or disable verbose output. Defaults to False.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1000.
            model_name (str, optional): The model to use, e.g., 'gpt-4'. Defaults to "gpt-4".
        """
        self.unique_identifier = unique_identifier
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.model_name = model_name
        self.history: List[Tuple[str, str]] = []  # Stores tuples of (observation, action)
        self.main_prompt: str = ""
        self.verbose = verbose 

        openai.api_key = self.api_key

    def reset(self, game_prompt: str) -> None:
        """
        Reset the agent with a new main prompt and clear history.

        Args:
            game_prompt (str): The main prompt or instructions for the player.
        """
        self.main_prompt = game_prompt
        self.history.clear()

    def get_action(
        self, 
        observation: str, 
        valid_actions: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        Generate an action using the OpenAI GPT-4 API based on the current observation and valid actions.

        Args:
            observation (str): The current state or observation of the game specific to the player.
            valid_actions (List[str], optional): A list of valid actions.

        Returns:
            Tuple[str, str]: A tuple containing the generated action and the prompt used to generate it.
        """
        # Construct the messages for the chat completion
        messages = [{"role": "system", "content": self.main_prompt}]
        for h_observation, h_action in self.history:
            messages.append({"role": "user", "content": h_observation})
            messages.append({"role": "assistant", "content": h_action})
        
        # Append valid actions if provided
        if valid_actions:
            valid_actions_str = f"Valid actions: {', '.join(valid_actions)}."
            messages.append({"role": "user", "content": valid_actions_str})
        
        # Append the current observation
        if observation:
            messages.append({"role": "user", "content": observation})
        
        # Verbose output of the prompt
        if self.verbose:
            prompt_display = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            print(f"\n[Agent - GPTAgent]\n{prompt_display}\n")

        # Call the GPT-4 API to generate a response
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            n=1,
            stop=None,
            temperature=0.7
        )

        # Extract the generated action from the API response
        action = response['choices'][0]['message']['content'].strip()

        # Add the current observation and generated action to history
        self.history.append((observation, action))

        # Prepare the prompt string for logging or display
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        return action, prompt
