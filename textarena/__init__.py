""" Root __init__ of textarena """

from textarena.core import (
    Env,
    Wrapper,
    ObservationWrapper,
    RenderWrapper,
    ActionWrapper,
    Agent,
    AgentWrapper,
    State,
    Message,
    Observations,
    Rewards,
    Info,
    GAME_ID,
    GameMaker,
    JudgeVote,
    GameMasterAction
)
from textarena.envs.registration import (
    make,
    register,
    pprint_registry,
    pprint_registry_detailed,
    find_highest_version,
    check_env_exists,
)

from textarena.api import (
    register_online_model,
    make_online,
)

from textarena.wrappers import (
    TkinterRenderWrapper,
    LLMObservationWrapper,
    ClipWordsActionWrapper
)
from textarena.wrappers.agent_wrappers import (
    ThoughtAgentWrapper,
    InterpreterAgentWrapper,
    ChainAgentWrapper,
    ActorCriticAgentWrapper
)

from textarena import wrappers
from textarena.basic_agents import (
    HumanAgent,
    OpenRouterAgent,
    HFLocalAgent,
    CerebrasAgent
) 


__all__ = [
    # core
    "Env",
    "Wrapper",
    "ObservationWrapper",
    "RenderWrapper",
    "ActionWrapper",
    "AgentWrapper",
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
    # play online
    "make_online",
]
__version__ = "1.0.0"
