import re
import numpy as np
from typing import Optional, Dict, Tuple, Any

import textarena as ta

from textarena.envs.games.Sokoban.renderer import create_board_str
from textarena.envs.games.Sokoban.utils import generate_room, CHANGE_COORDINATES


class SokobanEnv(ta.Env):
    def __init__(self, dim_room=(6, 6), max_turns=100, num_boxes=3):
        self.dim_room = dim_room
        self.num_gen_steps = int(1.7 * (dim_room[0] + dim_room[1]))
        self.num_boxes = num_boxes
        self.max_turns = max_turns
        self.action_space = ['no operation', 'push up', 'push down', 'push left', 'push right', 
                             'move up', 'move down', 'move left', 'move right']
        
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
        board_str = f"Current Board:\n\n{create_board_str(self.room_state)}\nAvailable Moves: " + ", ".join(self.action_space)
        self.state.add_observation(message=board_str, observation_type=ta.ObservationType.GAME_BOARD)

    def get_board_str(self):
        return create_board_str(board_state=self.state.game_state['board'])

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, to_id=-1, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        matches = re.compile(r'\[(.*?)\]').search(action)

        if matches is None: self.state.set_invalid_move(reason="The submitted move does not follow the correct format.")
        else:
            action = matches.group(1)
            if action not in self.action_space: self.state.set_invalid_move(reason="The submitted move is not a valid action.")
            else:
                if action.startswith('push'): self._push(action)
                elif action != 'no operation': self._move(action)
                board_str = f"Current Board:\n\n{create_board_str(self.room_state)}\nAvailable Moves: " + ", ".join(self.action_space)
                self.state.add_observation(from_id=-1, to_id=self.state.current_player_id, message=board_str, observation_type=ta.ObservationType.GAME_BOARD)
                
            boxes_on_targets, all_boxes_on_targets = self._check_if_all_boxes_on_target()
            if all_boxes_on_targets:
                self.state.set_outcome(reward=1, reason="Congratulations! You have solved the Sokoban puzzle!")
            elif self.state.turn >= self.max_turns:
                self.state.set_outcome(reward=(self.num_boxes-boxes_on_targets)/self.num_boxes, reason="The turn limit has been reached. You did not solve the puzzle.")

        return self.state.step()
    
    def reset(self, num_players: int, seed: Optional[int]=None):
        """ Reset the environment to start a new game """
        self.state = ta.SinglePlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        try:
            self.room_fixed, self.room_state, self.box_mapping = generate_room(
                dim=self.dim_room,
                num_steps=self.num_gen_steps,
                num_boxes=self.num_boxes,
                seed=seed
            )
        except (RuntimeError, RuntimeWarning): return self.reset(num_players=num_players, seed=seed)
        self.player_position = np.argwhere(self.room_state == 5)[0]
        self.state.reset(game_state={'board': create_board_str(self.room_state)}, player_prompt_function=self._generate_player_prompt)
        self._observe_current_state()

    def _push(self, action):
        """
        Perform a push, if a box is adjacent in the right direction. If no box, can be pushed, try to move.
        """
        change = CHANGE_COORDINATES[(self.action_space.index(action) - 1) % 4]
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
        change = CHANGE_COORDINATES[(self.action_space.index(action) - 1) % 4]
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
        empty_targets = self.room_state == 2
        player_hiding_target = (self.room_fixed == 2) & (self.room_state == 5)
        boxes_on_targets = np.where(empty_targets | player_hiding_target)[0].shape[0]
        return boxes_on_targets, boxes_on_targets == 0
    