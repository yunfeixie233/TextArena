import re
import string
from typing import Any, Dict, Optional, Tuple, List

import textarena as ta
from textarena.envs.games.ColonelBlotto.renderer import create_game_str

class ColonelBlottoEnv(ta.Env):
    def __init__(self, num_fields: int = 3, num_total_units: int = 20, max_turns: int = 10):
        """
        Args:
            num_fields (int): Number of fields to fight over (2-26).
            num_total_units (int): Total units each player can allocate per round.
            max_turns (int): Maximum number of rounds before the game ends.
        """
        self.num_fields = min(max(num_fields, 2), 26)
        self.field_names = list(string.ascii_uppercase[:self.num_fields])
        self.num_total_units = max(num_total_units, self.num_fields)
        self.max_turns = max_turns

    def get_board_str(self): 
        return create_game_str(game_state=self.state.game_state)

    def reset(self, num_players: int, seed: Optional[int] = None):
        self.state = ta.TwoPlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        initial_game_state = self._initialize_game_state()
        self.state.reset(
            game_state=initial_game_state, 
            player_prompt_function=self._prompt, 
            role_mapping={0: "Commander Alpha", 1: "Commander Beta"}
        )
        self.state.add_observation(
            message=f"Game started!\n{self._render_game_state()}", 
            observation_type=ta.ObservationType.GAME_BOARD
        )

    def _initialize_game_state(self) -> Dict[str, Any]:
        return {
            'fields': [
                {'name': field_name, 'value': 1, 'player_0_units': 0, 'player_1_units': 0} 
                for field_name in self.field_names                                
            ],
            'phase': 'allocation',
            'current_round': 1,
            'scores': {0: 0, 1: 0},
            'player_states': {
                0: {
                    'units_remaining': self.num_total_units,
                    'current_allocation': {field_name: 0 for field_name in self.field_names},
                    'allocation_complete': False
                },
                1: {
                    'units_remaining': self.num_total_units,
                    'current_allocation': {field_name: 0 for field_name in self.field_names},
                    'allocation_complete': False
                }
            }
        }

    def _render_game_state(self) -> str:
        phase = self.state.game_state['phase']
        current_round = self.state.game_state['current_round']
        scores = self.state.game_state['scores']
        
        lines = []
        lines.append(f"=== COLONEL BLOTTO - Round {current_round}/{self.max_turns} ===")
        lines.append(f"Phase: {phase.title()}")
        lines.append(f"Rounds Won - Commander Alpha: {scores[0]}, Commander Beta: {scores[1]}")
        
        if phase == 'allocation':
            lines.append(f"Available fields: {', '.join(self.field_names)}")
            lines.append(f"Units to allocate: {self.num_total_units}")
            lines.append("Format: A:4, B:2, C:2")
        elif phase == 'results':
            lines.append("\nBATTLE RESULTS:")
            for field in self.state.game_state['fields']:
                p0_units = field['player_0_units']
                p1_units = field['player_1_units']
                winner = "Alpha" if p0_units > p1_units else "Beta" if p1_units > p0_units else "TIE"
                lines.append(f"Field {field['name']}: Alpha {p0_units} vs Beta {p1_units} -> {winner}")
        
        return "\n".join(lines)

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        role = "Commander Alpha" if player_id == 0 else "Commander Beta"
        phase = game_state['phase']
        
        if phase == 'allocation':
            player_state = game_state['player_states'][player_id]
            if player_state['allocation_complete']:
                return (
                    f"You are {role} in Colonel Blotto.\n"
                    f"Your allocation: {player_state['current_allocation']}\n"
                    "Waiting for opponent to finish allocation..."
                )
            else:
                return (
                    f"You are {role} in Colonel Blotto.\n"
                    f"Allocate {self.num_total_units} units across fields: {', '.join(self.field_names)}\n"
                    "Format: A:4, B:2, C:2 (must sum to exactly {self.num_total_units})\n"
                    "Win the majority of fields to win the round!"
                )
        else:
            return f"You are {role}. Battle results are being calculated..."

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(
            from_id=self.state.current_player_id, 
            message=action, 
            observation_type=ta.ObservationType.PLAYER_ACTION
        )
        
        self._execute_player_move(action)
        self._check_gameover()
        
        self.state.add_observation(
            message=f"Current game state:\n{self._render_game_state()}", 
            observation_type=ta.ObservationType.GAME_BOARD
        )
        
        return self.state.step()

    def _execute_player_move(self, action: str):
        """Parse the action to find the requested allocation. If valid, make the allocation, otherwise set it as an invalid move"""
        if self.state.game_state['phase'] == 'results':
            self._transition_to_next_round()
            return
            
        allocation_dict = self._parse_allocation_input(action)
        validation_result = self._validate_allocation(allocation_dict)
        
        if validation_result != "Allocation is good.":
            self.state.set_invalid_move(reason=validation_result)
            return
            
        # Process valid allocation
        player_id = self.state.current_player_id
        for field in self.state.game_state['fields']:
            field[f'player_{player_id}_units'] = allocation_dict[field['name']]
            self.state.game_state['player_states'][player_id]['current_allocation'][field['name']] = allocation_dict[field['name']]
        
        self.state.game_state['player_states'][player_id]['units_remaining'] = 0
        self.state.game_state['player_states'][player_id]['allocation_complete'] = True
        
        # Check if both players have allocated
        other_player = 1 - player_id
        if self.state.game_state['player_states'][other_player]['allocation_complete']:
            self._resolve_battle()

    def _parse_allocation_input(self, action_string: str) -> Optional[Dict[str, int]]:
        """Parse allocation string into dictionary"""
        if not action_string or not action_string.strip():
            return None
            
        # Try comma separation first, then space separation
        split_list = action_string.split(",")
        if len(split_list) == 1:
            split_list = action_string.split(" ")
        
        try:
            result = {}
            for item in split_list:
                item = item.strip()
                if not item:  # Skip empty items
                    continue
                if ':' not in item:
                    return None  # Invalid format
                
                parts = item.split(":", 1)
                if len(parts) != 2:
                    return None
                    
                field, units_str = parts
                field = field.strip().upper()
                units_str = units_str.strip()
                
                if not field or not units_str:
                    return None
                    
                try:
                    units = int(units_str)
                    result[field] = units
                except ValueError:
                    return None
                    
            return result if result else None
        except Exception:
            return None

    def _validate_allocation(self, allocation_dict: Optional[Dict[str, int]]) -> str:
        """Validate allocation dictionary"""
        if allocation_dict is None:
            return "Invalid input format. Use: A:5, B:10, C:5"
        
        # Check if all required fields are present first
        if len(allocation_dict) != len(self.field_names):
            return f"Must allocate to all {len(self.field_names)} fields."
        
        # Check for invalid field names
        if any(field not in self.field_names for field in allocation_dict.keys()):
            return f"Invalid field name(s). Valid fields: {', '.join(self.field_names)}"
        
        # Check for non-negative integers
        if any(not isinstance(units, int) or units < 0 for units in allocation_dict.values()):
            return "All allocations must be non-negative integers."
        
        # Check sum last (after we know all fields are present and valid)
        if sum(allocation_dict.values()) != self.num_total_units:
            return f"Units must sum to exactly {self.num_total_units}. Current sum: {sum(allocation_dict.values())}"
        
        return "Allocation is good."

    def _resolve_battle(self):
        """Calculate battle results and determine round winner"""
        self.state.game_state['phase'] = 'results'
        
        # Determine field winners
        field_winners = []
        for field in self.state.game_state['fields']:
            p0_units = field['player_0_units']
            p1_units = field['player_1_units']
            if p0_units > p1_units:
                field_winners.append(0)
            elif p1_units > p0_units:
                field_winners.append(1)
            else:
                field_winners.append(None)  # Tie
        
        # Determine round winner (majority of fields)
        p0_wins = field_winners.count(0)
        p1_wins = field_winners.count(1)
        
        round_winner = None
        if p0_wins > p1_wins:
            round_winner = 0
            self.state.game_state['scores'][0] += 1
        elif p1_wins > p0_wins:
            round_winner = 1
            self.state.game_state['scores'][1] += 1
        
        # Add battle summary
        if round_winner is not None:
            winner_name = "Commander Alpha" if round_winner == 0 else "Commander Beta"
            self.state.add_observation(
                message=f"Round {self.state.game_state['current_round']} winner: {winner_name}!",
                observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
            )
        else:
            self.state.add_observation(
                message=f"Round {self.state.game_state['current_round']} ended in a tie!",
                observation_type=ta.ObservationType.GAME_ACTION_DESCRIPTION
            )

    def _transition_to_next_round(self):
        """Set up the next round"""
        self.state.game_state['current_round'] += 1
        self.state.game_state['phase'] = 'allocation'
        
        # Reset player states for new round
        for player_id in [0, 1]:
            self.state.game_state['player_states'][player_id]['units_remaining'] = self.num_total_units
            self.state.game_state['player_states'][player_id]['current_allocation'] = {
                field_name: 0 for field_name in self.field_names
            }
            self.state.game_state['player_states'][player_id]['allocation_complete'] = False
        
        # Reset field allocations
        for field in self.state.game_state['fields']:
            field['player_0_units'] = 0
            field['player_1_units'] = 0

    def _check_gameover(self):
        """Check if the game should end"""
        current_round = self.state.game_state['current_round']
        scores = self.state.game_state['scores']
        
        # Check if max rounds reached
        if current_round > self.max_turns:
            if scores[0] > scores[1]:
                self.state.set_winner(player_id=0, reason=f"Commander Alpha wins {scores[0]}-{scores[1]} after {self.max_turns} rounds!")
            elif scores[1] > scores[0]:
                self.state.set_winner(player_id=1, reason=f"Commander Beta wins {scores[1]}-{scores[0]} after {self.max_turns} rounds!")
            else:
                self.state.set_draw(reason=f"Game ends in a {scores[0]}-{scores[1]} tie after {self.max_turns} rounds!")
            return
        
        # Check for early victory (majority of possible rounds)
        rounds_needed_to_win = (self.max_turns // 2) + 1
        if scores[0] >= rounds_needed_to_win:
            self.state.set_winner(player_id=0, reason=f"Commander Alpha wins {scores[0]}-{scores[1]} (majority achieved)!")
        elif scores[1] >= rounds_needed_to_win:
            self.state.set_winner(player_id=1, reason=f"Commander Beta wins {scores[1]}-{scores[0]} (majority achieved)!")
        
        # Check turn limit
        if self.state.check_turn_limit():
            if scores[0] > scores[1]:
                self.state.set_winner(player_id=0, reason=f"Turn limit reached. Commander Alpha wins {scores[0]}-{scores[1]}!")
            elif scores[1] > scores[0]:
                self.state.set_winner(player_id=1, reason=f"Turn limit reached. Commander Beta wins {scores[1]}-{scores[0]}!")
            else:
                self.state.set_draw(reason=f"Turn limit reached. Game ends in a {scores[0]}-{scores[1]} tie!")