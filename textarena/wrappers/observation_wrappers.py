from textarena.core import ObservationWrapper, Env, Observations, Info
from typing import Dict, Optional, Tuple, Tuple

__all__ = [
    "LLMObservationWrapper"
]


class LLMObservationWrapper(ObservationWrapper):
    """TODO"""

    def __init__(self, env: Env):
        """TODO"""
        super().__init__(env)
        self.full_observations = {}

    def reset(self, seed: Optional[int] = None) -> Observations:
        """TODO"""
        observations = self.env.reset(seed=seed)
        self.full_observations = observations.copy() if observations else {}
        return self._convert_obs_to_str()

    def _convert_obs_to_str(self):
        """ TODO """
        return_dict = {}
        for recipient_id, message_tuple in self.full_observations.items():
            if recipient_id not in return_dict:
                return_dict[recipient_id] = ""
            
            for sender_id, message in message_tuple:
                if sender_id in self.state.role_mapping:
                    sender_name = self.state.role_mapping[sender_id]
                else:
                    sender_name = f"Player {sender_id}"
                return_dict[recipient_id] += f"\n[{sender_name}] {message}"
        return return_dict 


    def _convert_obs_to_str(self):
        """ TODO """
        return_dict = {}
        for recipient_id, message_tuple in self.full_observations.items():
            if recipient_id not in return_dict:
                return_dict[recipient_id] = ""
            
            for sender_id, message in message_tuple:
                if sender_id in self.state.role_mapping:
                    sender_name = self.state.role_mapping[sender_id]
                else:
                    sender_name = f"Player {sender_id}"
                return_dict[recipient_id] += f"\n[{sender_name}] {message}"
        return return_dict 


    def observation(
        self, observations: Optional[Observations]  # player-wise observations
    ) -> Optional[Observations]:  # full player-wise observations
        # """ TODO """
        if observations is None:
            return self.full_observations

        # Extend the full observations with the current observations
        for player_id, obs in observations.items():
            if player_id in self.full_observations:
                self.full_observations[player_id] += obs
            else:
                self.full_observations[player_id] = obs

        return self._convert_obs_to_str()
