"""Interface and code for agents in the game.
In general the interface is (minimally) string to string functions, but we may want to take in lists of messages etc.
"""

from typing import Generic, TypeVar
from abc import ABC, abstractmethod
import textarena as ta
import textarena.utils as gen_utils

# TODO: make compatible with player id maps

# Define a type variable T
T = TypeVar("T")


# Make AgentInterface generic with respect to T
class AgentInterface(ABC, Generic[T]):
    """Basic Interface for an agent"""

    @abstractmethod
    def observation_map(self, messages: list[ta.Message]) -> T:
        """Map an observation to a format the agent can understand."""

    @abstractmethod
    def __call__(self, observation_rendering: T) -> str:
        """Given an observation, return a (string) action."""


class OpenRouterChatAgent(AgentInterface[list[dict]]):
    """An agent that uses the OpenRouter API to generate responses to observations."""

    def __init__(self, player_id, model_name: str):
        super().__init__()
        self.player_id = player_id
        self.model_name = model_name

    def observation_map(self, messages: list[ta.Message]) -> list[dict]:
        """Map into the format expected by the OpenRouter API.
        This uses the ChatML format, with roles system, user, assistant.
        We can map the agent to the assistant role, the system role is used for game messages
        and the user role is used for other player messages."""
        output_messages = []
        for player_id, content in messages:
            if player_id == ta.GAME_ID:
                role = "system"
            elif player_id == self.player_id:
                role = "assistant"
            else:
                role = "user"
            output_messages.append({"role": role, "content": content})
        return output_messages

    def __call__(self, observation_rendering: list[dict]) -> str:
        """Given an observation, return a (string) action."""
        gen_utils.batch_open_router_generate(
            texts=observation_rendering,
            model_string=self.model_name,
            message_history=[
                {
                    "role": "system",
                    "content": "You are a helpful game-playing assistant.",
                }
            ],
            **gen_utils.DEFAULT_GEN_KWARGS,
        )


class DummyStringAgent(AgentInterface[str]):
    """An agent that just returns a fixed string."""

    def __init__(self, fixed_string: str):
        super().__init__()
        self.fixed_string = fixed_string

    def observation_map(self, messages: list[ta.Message]) -> str:
        """Map into the format expected by the OpenRouter API.
        This uses the ChatML format, with roles system, user, assistant.
        We can map the agent to the assistant role, the system role is used for game messages
        and the user role is used for other player messages."""
        return self.fixed_string

    def __call__(self, observation_rendering: str) -> str:
        """Given an observation, return a (string) action."""
        return self.fixed_string
