import re
import importlib
from typing import Any, Callable, Dict, Tuple, Optional
from dataclasses import dataclass, field

# Global environment registry
ENV_REGISTRY: Dict[str, Callable] = {}

@dataclass
class EnvSpec:
    """A specification for creating environments."""
    id: str
    entry_point: Callable
    kwargs: Dict[str, Any] = field(default_factory=dict)
    
    def make(self, **kwargs) -> Any:
        """Create an environment instance."""
        all_kwargs = {**self.kwargs, **kwargs}
        return self.entry_point(**all_kwargs)

def register(id: str, entry_point: Callable, **kwargs: Any):
    """Register an environment with a given ID."""
    if id in ENV_REGISTRY:
        raise ValueError(f"Environment {id} already registered.")
    ENV_REGISTRY[id] = EnvSpec(id=id, entry_point=entry_point, kwargs=kwargs)

def pprint_registry():
    """Pretty print the current registry of environments."""
    if not ENV_REGISTRY:
        print("No environments registered.")
    else:
        print("Registered Environments:")
        for env_id, env_spec in ENV_REGISTRY.items():
            print(f"  - {env_id}: {env_spec.entry_point}")

def pprint_registry_detailed():
    """Pretty print the registry with additional details like kwargs."""
    if not ENV_REGISTRY:
        print("No environments registered.")
    else:
        print("Detailed Registered Environments:")
        for env_id, env_spec in ENV_REGISTRY.items():
            print(f"  - {env_id}:")
            print(f"      Entry Point: {env_spec.entry_point}")
            print(f"      Kwargs: {env_spec.kwargs}")

def find_highest_version(name: str):
    """Find the highest registered version of an environment by its name."""
    versions = []
    
    # Define regex to match the pattern "-v<number>"
    version_pattern = re.compile(r"-v(\d+)")
    
    for env_id in ENV_REGISTRY.keys():
        if env_id.startswith(name):
            match = version_pattern.search(env_id)
            if match:
                version_number = int(match.group(1))
                versions.append(version_number)
    
    return max(versions) if versions else None

def check_env_exists(env_id: str):
    """Check if an environment exists in the registry."""
    if env_id not in ENV_REGISTRY:
        raise ValueError(f"Environment {env_id} is not registered.")
    else:
        print(f"Environment {env_id} is registered.")


# def make(env_id: str, **kwargs) -> Any:
#     """Create an environment instance using the registered ID."""
#     if env_id not in ENV_REGISTRY:
#         raise ValueError(f"Environment {env_id} not found in registry.")
    
#     env_spec = ENV_REGISTRY[env_id]
    
#     # Resolve the entry point if it's a string
#     if isinstance(env_spec.entry_point, str):
#         module_name, class_name = env_spec.entry_point.split(":")
#         module = importlib.import_module(module_name)
#         env_class = getattr(module, class_name)
#     else:
#         env_class = env_spec.entry_point
    
#     # Pass additional keyword arguments
#     return env_class(**{**env_spec.kwargs, **kwargs})

def make(env_id: str, **kwargs) -> Any:
    """Create an environment instance using the registered ID."""
    if env_id not in ENV_REGISTRY:
        raise ValueError(f"Environment {env_id} not found in registry.")
    
    env_spec = ENV_REGISTRY[env_id]
    
    # Resolve the entry point if it's a string
    if isinstance(env_spec.entry_point, str):
        module_path, class_name = env_spec.entry_point.split(":")
        try:
            module = importlib.import_module(module_path)
            env_class = getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(f"Could not import {module_path}.{class_name}. Error: {e}")
    else:
        env_class = env_spec.entry_point
    
    env = env_class(**{**env_spec.kwargs, **kwargs})

    # Dynamically attach the env_id
    env.env_id = env_id
    env.entry_point = env_spec.entry_point

    return env


def classify_games(filter_category: str = "all"):
    """Classify games in the registry based on keywords in entry points, with optional filtering."""
    classified_games = {}

    for env_id, env_spec in ENV_REGISTRY.items():
        entry_point = env_spec.entry_point if isinstance(env_spec.entry_point, str) else ""
        
        # Extract category keyword from entry point (e.g., multi_player, two_player)
        match = re.search(r"(multi_player|two_player|single_player|[\w]+_player)", entry_point)
        category = match.group(0) if match else "Other"
        
        # Initialize list for category if it doesn't exist
        if category not in classified_games:
            classified_games[category] = []
        
        # Append environment ID to the detected category
        classified_games[category].append(env_id)

    # Filter for a specific category if provided
    if filter_category != "all":
        return {filter_category: classified_games.get(filter_category, [])}
    
    return classified_games