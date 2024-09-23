import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Any, Dict, Optional, Tuple, List
from .agent_interface import AgentInterface  # Assuming AgentInterface is in the same package

class HuggingFaceAgent(AgentInterface):
    """
    Agent utilizing Hugging Face models to generate actions for the game.
    """

    def __init__(
        self, 
        unique_identifier: str, 
        model_name: str, 
        verbose: bool = False, 
        max_tokens: int = 1000, 
        device: Optional[str] = None
    ):
        """
        Initialize the HuggingFaceAgent with the specified parameters.

        Args:
            unique_identifier (str): A unique identifier for the agent.
            model_name (str): The Hugging Face model name to use, e.g., 'gpt2'.
            verbose (bool, optional): Flag to enable or disable verbose output. Defaults to False.
            max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 1000.
            device (str, optional): Device to run the model on ('cpu' or 'cuda'). Defaults to 'cuda' if available.
        """
        self.unique_identifier = unique_identifier
        self.model_name = model_name
        self.verbose = verbose 
        self.max_tokens = max_tokens
        self.history: List[Tuple[str, str]] = []  # Stores tuples of (observation, action)
        self.main_prompt: str = ""

        # Set device
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)

        # Set padding token if not present
        #if self.tokenizer.pad_token is None:
        #    self.tokenizer.pad_token = self.tokenizer.eos_token

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
        Generate an action using a Hugging Face model based on the current observation and valid actions.

        Args:
            observation (str): The current state or observation of the game specific to the player.
            valid_actions (List[str], optional): A list of valid actions.

        Returns:
            Tuple[str, str]: A tuple containing the generated action and the prompt used to generate it.
        """
        # Construct the prompt
        prompt = self.main_prompt + "\n"
        for h_observation, h_action in self.history:
            prompt += f"User: {h_observation}\nAssistant: {h_action}\n"
        
        # Append valid actions if provided
        if valid_actions:
            valid_actions_str = f"Valid actions: {', '.join(valid_actions)}."
            prompt += f"User: {valid_actions_str}\n"
        
        # Append the current observation
        if observation:
            prompt += f"User: {observation}\nAssistant:"

        # Verbose output of the prompt
        if self.verbose:
            print(f"\n[Agent - HuggingFaceAgent]\n{prompt}\n")

        # Tokenize the input prompt
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        # Generate a response
        with torch.no_grad():
            output = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + self.max_tokens,
                do_sample=True,
                top_p=0.95,
                top_k=60,
                temperature=0.7,
                #pad_token_id=self.tokenizer.eos_token_id,
                #eos_token_id=self.tokenizer.eos_token_id
            )

        # Decode the generated tokens
        generated_text = self.tokenizer.decode(output[0][inputs.shape[1]:], skip_special_tokens=True).strip()

        # Post-process the generated text to extract the action
        # This assumes the model generates the action directly; adjust as needed
        action = generated_text.split('\n')[0] if '\n' in generated_text else generated_text

        # Add the current observation and generated action to history
        self.history.append((observation, action))

        return action, prompt
