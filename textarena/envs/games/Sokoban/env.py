import re
import numpy as np
from typing import Optional, Dict, Tuple, Any

import textarena as ta

from textarena.envs.games.Sokoban.utils import generate_room, CHANGE_COORDINATES


class SokobanEnv(ta.Env):
    def __init__(self, dim_room=(6, 6), max_turns=100, num_boxes=3):
        self.dim_room = dim_room
        self.num_gen_steps = int(1.7 * (dim_room[0] + dim_room[1]))
        self.num_boxes = num_boxes
        self.max_turns = max_turns
        self.action_space = ['up', 'down', 'left', 'right']
        
    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        return """You are solving the Sokoban puzzle. You are the player and you need to push all boxes to targets.
        When you are right next to a box, you can push it by moving in the same direction.
        You cannot push a box through a wall, and you cannot pull a box.
        On the board, objects are represented as: 
        - The player (you) appears as 'P' 
        - Walls are represented with '#' 
        - Boxes are marked as 'X' 
        - Empty goals are shown with a 'O'
        - Boxes on goals are visualized with '√'"""
    
    def _observe_current_state(self):
        board_str = f"Current Board:\n\n{self.create_board_str(self.room_state)}\nAvailable Moves: " + ", ".join(self.action_space)
        self.state.add_observation(message=board_str, observation_type=ta.ObservationType.GAME_BOARD)

    def get_board_str(self):
        return self.create_board_str(board_state=self.state.game_state['board'])
    
    def create_board_str(self, board_state: np.ndarray) -> str:
        grid_lookup = {0:"#", 1:"_", 2:"O", 3:"√", 4:"X", 5:"P", 6:"S"}

        board_str = ""
        for row in board_state:
            board_str += ' '.join([grid_lookup[cell] for cell in row])
            board_str += "\n"
        return board_str

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, to_id=-1, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        matches = re.compile(r'\[(up|down|left|right)\]').search(action)

        if matches is None: self.state.set_invalid_move(reward=self._get_percentage_completion(), reason="The submitted move does not follow the correct format.")
        else:
            action = matches.group(1)
            if action not in self.action_space: self.state.set_invalid_move(reward=self._get_percentage_completion(), reason="The submitted move is not a valid action.")
            else:
                self._push(action)
                board_str = f"Current Board:\n\n{self.create_board_str(self.room_state)}\nAvailable Moves: " + ", ".join(self.action_space)
                self.state.add_observation(from_id=-1, to_id=self.state.current_player_id, message=board_str, observation_type=ta.ObservationType.GAME_BOARD)
                
            boxes_on_targets, all_boxes_on_targets = self._check_if_all_boxes_on_target()
            if all_boxes_on_targets:
                self.state.set_outcome(reward=1, reason="Congratulations! You have solved the Sokoban puzzle!")
            elif self.state.turn >= self.max_turns:
                self.state.set_outcome(reward=self._get_percentage_completion(), reason="The turn limit has been reached. You did not solve the puzzle.")

        return self.state.step()
    
    def reset(self, num_players: int, seed: Optional[int]=None, max_retries: int = 50):
        self.state = ta.SinglePlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        
        for attempt in range(max_retries):
            try:
                # Vary the seed for each attempt to avoid identical failures
                current_seed = None if seed is None else seed + attempt
                self.room_fixed, self.room_state, self.box_mapping = generate_room(
                    dim=self.dim_room,
                    num_steps=self.num_gen_steps,
                    num_boxes=self.num_boxes,
                    seed=current_seed
                )
                break
            except (RuntimeError, RuntimeWarning):
                if attempt == max_retries - 1:
                    # Fallback: reduce constraints or use simpler generation
                    raise RuntimeError(f"Failed to generate valid room after {max_retries} attempts")
                continue
                
        self.player_position = np.argwhere(self.room_state == 5)[0]
        self.state.reset(game_state={'board': self.create_board_str(self.room_state)}, player_prompt_function=self._generate_player_prompt)
        self._observe_current_state()

    def _push(self, action):
        """
        Perform a push, if a box is adjacent in the right direction. If no box, can be pushed, try to move.
        """
        change = CHANGE_COORDINATES[self.action_space.index(action)]
        new_position = self.player_position + change
        current_position = self.player_position.copy()

        # No push, if the push would get the box out of the room's grid
        new_box_position = new_position + change
        if new_box_position[0] >= self.room_state.shape[0] or new_box_position[1] >= self.room_state.shape[1]:
            return False, False

        can_push_box = self.room_state[new_position[0], new_position[1]] in [3, 4]
        can_push_box &= self.room_state[new_box_position[0], new_box_position[1]] in [1, 2]
        if can_push_box:
            self.new_box_position = tuple(new_box_position)
            self.old_box_position = tuple(new_position)

            # Move Player
            self.player_position = new_position
            self.room_state[(new_position[0], new_position[1])] = 5
            self.room_state[current_position[0], current_position[1]] = self.room_fixed[current_position[0], current_position[1]]

            # Move Box
            box_type = 4
            if self.room_fixed[new_box_position[0], new_box_position[1]] == 2: box_type = 3
            self.room_state[new_box_position[0], new_box_position[1]] = box_type
            return True, True

        # Try to move if no box to push, available
        else: return self._move(action), False

    def _move(self, action):
        """
        Moves the player to the next field, if it is not occupied.
        """
        change = CHANGE_COORDINATES[self.action_space.index(action)]
        new_position = self.player_position + change
        current_position = self.player_position.copy()

        # Move player if the field in the moving direction is either
        # an empty field or an empty box target.
        if self.room_state[new_position[0], new_position[1]] in [1, 2]:
            self.player_position = new_position
            self.room_state[(new_position[0], new_position[1])] = 5
            self.room_state[current_position[0], current_position[1]] = self.room_fixed[current_position[0], current_position[1]]
            return True
        return False

    def _check_if_all_boxes_on_target(self):
        """
        Check how many boxes are currently on targets and if all boxes are on targets.
        
        Returns:
            tuple: (number_of_boxes_on_targets, all_boxes_on_targets_boolean)
        """
        # Count boxes that are on targets (value 3 = √)
        boxes_on_targets = int(np.sum(self.room_state == 3))
        
        # Check if player is standing on a target that should have a box
        player_on_target_with_box = 0
        player_pos = np.where(self.room_state == 5)
        if len(player_pos[0]) > 0:
            player_row, player_col = player_pos[0][0], player_pos[1][0]
            # If player is on a target position in the fixed room layout
            if self.room_fixed[player_row, player_col] == 2:
                # Check if this target should have a box (from box_mapping)
                if hasattr(self, 'box_mapping'):
                    for target_pos in self.box_mapping.keys():
                        if target_pos == (player_row, player_col):
                            # There should be a box here but player is standing on it
                            # This doesn't count as a box on target
                            break
        
        all_boxes_on_targets = (boxes_on_targets == self.num_boxes)
        return boxes_on_targets, all_boxes_on_targets

    def _get_percentage_completion(self) -> float:
        """ Compute how many boxes are on targets """
        boxes_on_targets, all_boxes_on_targets = self._check_if_all_boxes_on_target()
        return boxes_on_targets / self.num_boxes if not all_boxes_on_targets else 1.0
    