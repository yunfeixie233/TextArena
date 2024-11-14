from textarena.core import ObservationWrapper, Env, Observations, Info
from typing import Dict, Optional, Tuple, Tuple

__all__ = [
    "LLMObservationWrapper"
]


class LLMObservationWrapper(ObservationWrapper):
    """
    A wrapper for converting environment observations into formatted strings suitable
    for large language models (LLMs). It ensures that duplicate observations are not
    added to the full observations.
    """

    def _init_(self, env: Env):
        """
        Initializes the LLMObservationWrapper.

        Args:
            env (Env): The environment to wrap.
        """
        super()._init_(env)
        self.full_observations: Dict[int, List[Tuple[int, str]]] = {}
        self.state = self.env.state

    def reset(self, seed: Optional[int] = None) -> Observations:
        """
        Resets the environment and initializes full observations.

        Args:
            seed (Optional[int]): Optional seed for the environment reset.

        Returns:
            Observations: The initial observations as formatted strings.
        """
        observations = self.env.reset(seed=seed)
        self.full_observations = observations.copy() if observations else {}
        return self._convert_obs_to_str()

    def _convert_obs_to_str(self) -> Observations:
        """
        Converts the full observations into formatted strings for each recipient.

        Returns:
            Observations: A dictionary mapping recipient IDs to their formatted observation strings.
        """
        return_dict: Observations = {}
        for recipient_id, message_tuples in self.full_observations.items():
            if recipient_id not in return_dict:
                return_dict[recipient_id] = ""

            for sender_id, message in message_tuples:
                sender_name = self.state.role_mapping.get(sender_id, f"Player {sender_id}")
                return_dict[recipient_id] += f"\n[{sender_name}] {message}"

            recipient_name = self.state.role_mapping.get(recipient_id, f"Player {recipient_id}")
            return_dict[recipient_id] += f"\n[{recipient_name}]"

        return return_dict

    def observation(
        self, observations: Optional[Observations]
    ) -> Optional[Observations]:
        """
        Processes new observations, ensuring no duplicates are added.

        Args:
            observations (Optional[Observations]): New player-wise observations.

        Returns:
            Optional[Observations]: The updated full observations as formatted strings.
        """
        if observations is None:
            return self._convert_obs_to_str()

        # Extend the full observations with the current observations without duplicates
        for player_id, new_obs in observations.items():
            if player_id not in self.full_observations:
                self.full_observations[player_id] = []
            
            for obs in new_obs:
                if obs not in self.full_observations[player_id]:
                    self.full_observations[player_id].append(obs)

        return self._convert_obs_to_str()
