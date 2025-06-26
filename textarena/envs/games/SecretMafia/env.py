from enum import Enum
import re, random
from typing import Any, Dict, Optional, List
import textarena as ta

class Phase(Enum):
    NIGHT_MAFIA = "Night-Mafia"
    NIGHT_DOCTOR = "Night-Doctor"
    NIGHT_DETECTIVE = "Night-Detective"
    DAY_DISCUSSION = "Day-Discussion"
    DAY_VOTING = "Day-Voting"

class Role:
    name: str = "Role"
    team: str = "Unknown"
    description: str = ""
    def get_prompt(self, player_id: int, player_roles: Dict[int, str], num_players: int, num_discussion_rounds: int) -> str: raise NotImplementedError

class Villager(Role):
    name = "Villager"
    team = "Village"
    description = "A regular villager. Your goal is to identify and eliminate all Mafia members through voting during the day."
    def get_prompt(self, player_id, player_roles, num_players, num_discussion_rounds):
        return (
            f"Welcome to Secret Mafia! You are Player {player_id}.\n"
            f"Your role: {self.name}\nTeam: {self.team}\nDescription: {self.description}\n\n"
            f"Players: {', '.join([f'Player {i}' for i in range(num_players)])}\n\n"
            f"The game progresses through Day and Night phases.\n"
            f"- During the Day phase, there are {num_discussion_rounds} rounds of discussion followed by voting.\n"
            f"- During discussions, everything you say is automatically broadcasted to all players.\n"
            f"- After discussions, all players must vote to eliminate one player.\n"
            f"- During the Night phase, you have no special actions.\n\n"
            f"The game ends when either all Mafia members are eliminated (Village wins) or\n"
            f"Mafia members equal or outnumber Villagers (Mafia wins).\n"
        )

class Mafia(Role):
    name = "Mafia"
    team = "Mafia"
    description = "A Mafia member. Eliminate villagers and gain majority."
    def get_prompt(self, player_id, player_roles, num_players, num_discussion_rounds):
        teammates = [f"Player {pid}" for pid, r in player_roles.items() if r == "Mafia"]
        return (
            f"Welcome to Secret Mafia! You are Player {player_id}.\n"
            f"Your role: {self.name}\nTeam: {self.team}\nDescription: {self.description}\n\n"
            f"Players: {', '.join([f'Player {i}' for i in range(num_players)])}\n\n"
            f"Your teammates are: {', '.join(teammates)}.\n\n"
            f"During DAY phase: Speak freely and vote.\n"
            f"During NIGHT phase: '[Player X]' to vote and eliminate a villager.\n"
            f"Win by eliminating villagers until Mafia equal or outnumber them.\n"
        )

class Doctor(Role):
    name = "Doctor"
    team = "Village"
    description = "Protect one player each night from Mafia elimination."
    def get_prompt(self, player_id, player_roles, num_players, num_discussion_rounds):
        return (
            f"Welcome to Secret Mafia! You are Player {player_id}.\n"
            f"Your role: {self.name}\nTeam: {self.team}\nDescription: {self.description}\n\n"
            f"Players: {', '.join([f'Player {i}' for i in range(num_players)])}\n\n"
            f"During DAY phase: Speak freely and vote.\n"
            f"During NIGHT phase: '[Player X]' to protect a player.\n"
            f"Win by identifying and eliminating all Mafia members.\n"
        )

class Detective(Role):
    name = "Detective"
    team = "Village"
    description = "Investigate players to find Mafia members."
    def get_prompt(self, player_id, player_roles, num_players, num_discussion_rounds):
        return (
            f"Welcome to Secret Mafia! You are Player {player_id}.\n"
            f"Your role: {self.name}\nTeam: {self.team}\nDescription: {self.description}\n\n"
            f"Players: {', '.join([f'Player {i}' for i in range(num_players)])}\n\n"
            f"During DAY phase: Speak freely and vote.\n"
            f"During NIGHT phase: '[Player X]' to investigate.\n"
            f"You'll learn immediately if the target is Mafia.\n"
            f"Win by identifying and eliminating all Mafia members.\n"
        )



class SecretMafiaEnv(ta.Env):
    voting_pattern = re.compile(r'.*\[(?:player\s*)?(\d+)\].*', re.IGNORECASE)

    def __init__(self, mafia_ratio: float = 0.25, discussion_rounds: int = 3):
        self.mafia_ratio = mafia_ratio
        self.discussion_rounds = discussion_rounds
        self.roles = {"Villager": Villager(), "Mafia": Mafia(), "Doctor": Doctor(), "Detective": Detective()}

    def _assign_roles(self, num_players: int):
        self.player_roles = {}
        role_pool = ["Mafia"] * max(1, round(num_players * self.mafia_ratio)) + ["Doctor"] + ["Detective"]
        role_pool.extend(["Villager"] * (num_players - len(role_pool)))
        random.shuffle(role_pool)
        for i in range(num_players):
            self.player_roles[i] = role_pool[i]

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        role_name = game_state["player_roles"][player_id]
        role_obj = self.roles.get(role_name)
        return role_obj.get_prompt(
            player_id=player_id,
            player_roles=game_state["player_roles"],
            num_players=self.state.num_players,
            num_discussion_rounds=game_state["num_discussion_rounds"]
        )
