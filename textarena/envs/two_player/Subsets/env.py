import random
from typing import Any, Dict, Optional, Tuple, List

import textarena as ta


class SubsetEnv(ta.Env):
    """ TODO """

    def __init__(self, env_ids: List[str], max_num_characters: int):
        """ TODO """
        env = ta.make(
            env_id=random.choice(env_ids)
        )

        self.env = ta.wrappers.ClipCharactersActionWrapper(
            env=env,
            max_num_characters=max_num_characters
        )

    def reset(self, seed: Optional[int]=None):
        self.env.reset(seed=seed)

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        return self.env.step(action=action)


    def __getattr__(self, name):
        """
        Delegate attribute access to the wrapped environment.

        This method is called only if the attribute wasn't found the usual ways.
        It allows the wrapper to pass through attributes and methods to the underlying environment.

        Args:
            name (str): The attribute name.

        Returns:
            The attribute from the wrapped environment.
        """
        return getattr(self.env, name)

    