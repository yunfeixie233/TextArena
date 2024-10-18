from textarena.core import ObservationWrapper, Env, Observation, Info
from typing import Dict, Optional, Tuple

__all__ = ["LLMObservationWrapper"]


class LLMObservationWrapper(ObservationWrapper):
    """TODO"""

    def __init__(self, env: Env):
        """TODO"""
        super().__init__(env)
        self.full_observations = {}

    def reset(self, seed: Optional[int] = None) -> tuple[Observation, Info]:
        """TODO"""
        observations, info = self.env.reset(seed=seed)
        self.full_observations = observations.copy() if observations else {}
        return self._convert_obs_to_str(), info
        # observations, info = self.env.reset(seed=seed)
        # # reset the full observations
        # self.full_observations = observations # inital observations are just copied

        # return self.full_observations, info

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
        self, observations: Optional[Observation]  # player-wise observations
    ) -> Optional[Observation]:  # full player-wise observations
        # """ TODO """
        # # check if game provided observations
        # if observations is None:
        #     return None

        # # extend the full observations with the current observations
        # for player_id in observations.keys():
        #     self.full_observations[player_id] += observations[player_id]

        # # return the full observations
        # # debugging
        # input(self.full_observations)
        # return self.full_observations
        if observations is None:
            return self.full_observations

        # Extend the full observations with the current observations
        for player_id, obs in observations.items():
            if player_id in self.full_observations:
                self.full_observations[player_id] += obs
            else:
                self.full_observations[player_id] = obs

        # Debugging: Display the full observations
        # input(self.full_observations)
        
        return self._convert_obs_to_str()
        # convert to string for llm
        return_dict = {}
        for player_id, obs in self.full_observations.items():
            return_dict[player_id] = return_dict.get(player_id, "") + self._convert_obs_to_str(obs)
        return return_dict
