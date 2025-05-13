from typing import Any, Dict, Optional, Tuple

import textarena as ta

import gym
import babyai_text


class BabyAiTextEnv(ta.Env):
    """Environment for BabyAI-text game"""

    def __init__(self, env_name: str = "BabyAI-MixedTestLocal-v0", max_turns: int = 20, seed: Optional[int] = None) -> None:
        """
        Initialize the 'BabyAI-Text' game environment.

        Args:
            env_name (str): The name of the environment, currently supported are: BabyAI-MixedTestLocal-v0,
            BabyAI-MixedTrainLocal-v0.
            max_turns (int)
        """
        self.max_turns = max_turns
        self.name_environment = env_name
        self.baby_ai_text_env = gym.make(env_name, seed=seed)
        self.seed = seed
        self.action_space = ["turn left", "turn right", "go forward", "pick up", "drop", "toggle"]

    def reset(self, num_players: int, seed: Optional[int]=None) -> None:
        """ Reset the 'BabyAI-Text' game to its initial state """
        # Initialize game state variables
        self.baby_ai_text_env.seed(seed if seed is not None else self.seed)
        binary_state, text_state = self.baby_ai_text_env.reset()
        self.state = ta.State(num_players=num_players, min_players=1, max_players=1, max_turns=self.max_turns)
        self.state.reset(
            seed=seed,
            game_state=binary_state | text_state,
            player_prompt_function=self._generate_player_prompt
        )

    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        """ Generate the initial prompt for the player, providing them with their goal and available actions """
        descriptions = ". ".join(game_state["descriptions"])
        actions = ", ".join(self.action_space)
        prompt = (
            f"You are playing 'BabyAI-Text'.\n"
            f"Your goal is to {game_state['mission']}.\n"
            f"Available actions are {actions}.\n"
            f"{descriptions} \n"
            "On your turn, simply type your message.\n"
        )
        if self.state.max_turns:
            prompt += f"The game lasts for {self.state.max_turns} turns in total.\n"
        return prompt

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        """ Process the player's action """
        player_id = self.state.current_player_id

        # update the observations and log the action
        self.state.add_observation(from_id=player_id, to_id=-1, message=action)
        try:
            action_id = self.action_space.index(action)
        except ValueError:
            observation = "Invalid action"
            self.state.add_observation(from_id=-1, to_id=player_id, message=observation)
            return (False, {'observations': observation, 'reward': -1, 'info': {}})

        obs, reward, done, info = self.baby_ai_text_env.step(action_id)
        new_description = ". ".join(info["descriptions"])
        self.state.add_observation(from_id=-1, to_id=player_id, message=new_description)
        self.state.info = {'observations': obs, 'reward': reward, 'info': info}
        self.state.done = done

        return self.state.step()

    def get_board_str(self):
        return str(self.baby_ai_text_env.env.env)