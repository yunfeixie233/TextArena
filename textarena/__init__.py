""" Root __init__ of textarena """

from textarena.core import (
    Env,
    Wrapper,
    ObservationWrapper,
    RenderWrapper,
    ActionWrapper
)
from textarena.envs.registration import (
    make,
    register,
    pprint_registry,
    pprint_registry_detailed,
    find_highest_version,
    check_env_exists,
)

from textarena import wrappers

import os

__all__ = [
    # core
    "Env",
    "Wrapper",
    "ObservationWrapper",
    "RenderWrapper",
    "ActionWrapper",
    # registration
    "make",
    "register",
    "pprint_registry",
    "pprint_registry_detailed",
    "find_highest_version",
    "check_env_exists",
    # module folders
    "envs",
    "utils",
    "wrappers",
]
__version__ = "1.0.0"


