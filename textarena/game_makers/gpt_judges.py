from textarena import GameMaker, JudgeVote, GameMasterAction
from typing import Optional, List, Dict
import numpy as np
import openai
import random
import os


class GPTGamemaster(GameMaker):
    """
    GPTGamemaster interfaces with OpenAI's language models to generate responses based on player input.
    """

    def __init__(
        self, 
        model_name: str,
        temperature: float = 0.7,
        max_tokens: int = 10,
    ):
        """
        Initialize GPTGamemaster with a specific OpenAI model and temperature.

        Args:
            model_name (str): The OpenAI model name (e.g., 'gpt-4', 'gpt-3.5-turbo').
            temperature (float): Sampling temperature. Defaults to 0.7.
            max_tokens (int): Maximum tokens per response. Defaults to 10.
            initial_context (str): Initial context for the conversation. Defaults to None.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        self.client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

    def __call__(self, text_input: str) -> str:
        """
        Generate a response using OpenAI's model based on input text.

        Args:
            text_input (str): Input text for response generation.

        Returns:
            str: The model's response.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": text_input}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                n=1
            )
            gamemaster_response = response.choices[0].message.content.strip()
            return gamemaster_response
            
        except Exception as e:
            return f"Error: {str(e)}"
        

class GPTJudge(GameMaker):
    """
    GPTJudge is responsible for interfacing with OpenAI's language models to generate judgments based on input text.
    
    It utilizes a specified GPT model to evaluate the given input and return a judgment or decision.
    """

    def __init__(
        self, 
        model_name: str,
        temperature: float = 0.7,
    ):
        """
        Initialize the GPTJudge with a specific OpenAI model and temperature setting.

        Args:
            model_name (str): The name of the OpenAI model to use (e.g., 'gpt-4', 'gpt-3.5-turbo').
            temperature (float, optional): Sampling temperature for the model's responses. Defaults to 0.7.
        """
        self.model_name = model_name
        self.temperature = temperature

    def __call__(self, text_input: str) -> str:
        """
        Generate a judgment based on the provided text input using the specified GPT model.

        Args:
            text_input (str): The input text for which the judge needs to provide a judgment.

        Returns:
            str: The judge's decision or judgment.
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": text_input}],
                max_tokens=10,  # Increased max_tokens to allow for more detailed responses
                temperature=self.temperature,
                n=1,
                stop=None
            )
            # Extract and return the judge's decision text
            judge_decision = response.choices[0].message['content'].strip()
            return judge_decision
        except Exception as e:
            # Handle potential API call failures
            return f"Error: {str(e)}"
        

class GPTGamemasterAction(GameMasterAction):
    """
    GPTGamemasterAction manages a GPTGamemaster instance to simulate a gamemaster's responses in games.
    """

    def __init__(
        self,
        options: List[str],
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 10,
    ):
        """
        Initialize with a specific OpenAI model and valid response options.

        Args:
            options (List[str]): Possible responses for the gamemaster (e.g., ["yes", "no", "I don't know"]).
            model_name (str): Model name to use. Defaults to 'gpt-4-mini'.
            temperature (float): Sampling temperature. Defaults to 0.7.
            max_tokens (int): Maximum tokens per response. Defaults to 10.
            initial_context (str): Initial context for the conversation. Defaults to None.
        """
        self.gamemaster = GPTGamemaster(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.options = options
        self.context_history = []  # History of questions and responses

    def set_initial_context(self, initial_context: str):
        """
        Set the initial context for the conversation.

        Args:
            initial_context (str): Initial context for the conversation.
        """
        self.initial_context = initial_context

    def _create_gamemaster_prompt(self, context: str) -> str:
        """
        Create a prompt based on the context and options for the gamemaster.

        Args:
            context (str): The scenario or question from the player.

        Returns:
            str: A formatted prompt for the gamemaster.
        """
        options_formatted = ", ".join([f"'{option}'" for option in self.options])
        history = "\n".join([f"Q: {q}\nA: {a}" for q, a in self.context_history])
        prompt = (
            f"{self.initial_context}\n"
            f"{history}\n\n"
            f"Q: {context}\n"
            f"Options: {options_formatted}\n\n"
            "Please strictly respond with the most appropriate option that is provided. Do not append anything extra."
        )
        return prompt

    def respond_to_action(self, context: str) -> str:
        """
        Generate and validate a response to the player's question.

        Args:
            context (str): Player's question or action to respond to.

        Returns:
            str: Gamemaster's validated response.
        """
        prompt = self._create_gamemaster_prompt(context)
        response = self.gamemaster(text_input=prompt)

        # Validate response against allowed options
        if any(option.casefold() in response.lower() for option in self.options):
            self.context_history.append((context, response))  # Update history for continuity
        else:
            # If the response is not one of the allowed options, update response to a default response
            response = "I'm sorry, I don't understand. Please try asking again."
            self.context_history.append((context, response))  # Update history with invalid response
        
        return response
        

    def get_summary(self) -> str:
        """
        Provide a summary of game history for transparency and player review.

        Returns:
            str: Summary of all questions and responses in the game.
        """
        summary = "\n".join([f"Q: {q} -> A: {a}" for q, a in self.context_history])
        return f"Game History:\n{summary}"


class GPTJudgeVote(JudgeVote):
    """
    GPTJudgeVote manages a collection of GPTJudge instances to simulate multiple judges voting on options.

    It initializes a specified number of judges with randomly selected models and facilitates the voting process.
    """

    def __init__(
        self,
        options: List[str],
        num_judges: int = 5,
        model_names: Optional[List[str]] = None,
        temperature: float = 0.7,
    ):
        """
        Initialize the GPTJudgeVote with a set of options and a specified number of judges.

        Args:
            options (List[str]): A list of options that judges can vote for.
            num_judges (int, optional): The number of judges to simulate. Defaults to 5.
            model_names (List[str], optional): A list of available GPT models for judges. 
                                               If None, a default list is used.
            temperature (float, optional): Sampling temperature for the judges' responses. Defaults to 0.7.
        """
        if model_names is None:
            self.available_models = [
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-4-mini",
            ]
        else:
            self.available_models = model_names

        self.judges = []
        for _ in range(num_judges):
            # Randomly select a model for each judge, allowing for repetition
            model_name = random.choice(self.available_models)
            judge = GPTJudge(
                model_name=model_name,
                temperature=temperature
            )
            self.judges.append(judge)

        self.options = options

    def _create_judge_prompt(self, context: str) -> str:
        """
        Create a prompt for the judge based on the provided context and options.

        Args:
            context (str): The context or scenario that judges are evaluating.

        Returns:
            str: A formatted prompt for the judge.
        """
        options_formatted = ", ".join([f"'{option}'" for option in self.options])
        prompt = (
            f"Based on the following context, please choose the most appropriate option from the provided choices.\n\n"
            f"Context: {context}\n\n"
            f"Options: {options_formatted}\n\n"
            f"Please respond with only the chosen option."
        )
        return prompt

    def evaluate(self, context: str) -> Dict[str, int]:
        """
        Evaluate the given context by having each judge cast a vote among the provided options.

        Args:
            context (str): The context or scenario to evaluate.

        Returns:
            Dict[str, int]: A dictionary mapping each option to the number of votes it received.
        """
        result_dict = {option: 0 for option in self.options}
        num_casted_votes = 0

        judge_prompt = self._create_judge_prompt(context)

        for judge in self.judges:
            # Get judgment from the judge
            judgement = judge(text_input=judge_prompt)

            # Determine which option was chosen
            chosen_option = None
            for option in self.options:
                if option.lower() in judgement.lower():
                    chosen_option = option
                    break

            if chosen_option:
                result_dict[chosen_option] += 1
                num_casted_votes += 1
            else:
                # Handle cases where the judge's response doesn't match any option
                # Optionally, you could log this or handle it differently
                continue

        # Normalize votes in case some judges didn't vote correctly
        if num_casted_votes > 0:
            for key in result_dict.keys():
                result_dict[key] /= num_casted_votes
        else:
            # Avoid division by zero; all votes remain zero
            pass

        return result_dict
