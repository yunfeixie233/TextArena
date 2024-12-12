
"""
WIP
"""


import re
import random
from typing import Any, Dict, List, Optional, Tuple, Set

import textarena as ta

class CarPuzzleEnv(ta.Env):
    def __init__(self, N: int = 8):
        """
        Initialize the Car Puzzle game.
        
        Args:
            N (int): Size of the puzzle grid (including walls)
        """
        self.environment_name = "Car Puzzle"
        self.N = N
        
        # Initialize the state using ta.State
        self.state = ta.State(
            num_players=2,
            max_turns=3,  # 3 turns total: create, creator solve, challenger solve
            check_truncated=False,
        )

        # Define action patterns
        self.car_pattern = re.compile(r"\[PlaceCar\] ([A-Z*@]) ([HV]) (\d+) (\d+) (\d+)", re.IGNORECASE)
        self.move_pattern = re.compile(r"\[Move\] ([A-Z*]) (-?\d+)", re.IGNORECASE)

    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        """Generate the initial prompt for a player."""
        if player_id == 0:  # Creator
            prompt = (
                "Welcome to Car Puzzle! You are the Puzzle Creator (Player 0).\n\n"
                "Game Flow:\n"
                "1. Create a puzzle by placing cars on the grid\n"
                "2. Solve your own puzzle to prove it's valid\n"
                "3. Wait for the challenger to attempt your puzzle\n\n"
                "Puzzle Creation Format:\n"
                "[PlaceCar] car_id orientation x y length\n"
                "  - car_id: Single character (use * for target car)\n"
                "  - orientation: H (horizontal) or V (vertical)\n"
                "  - x,y: Starting position\n"
                "  - length: Car length (2 or 3)\n\n"
                "Example:\n"
                "[PlaceCar] * H 26 3 2\n"
                "[PlaceCar] A H 45 5 2\n"
                "[PlaceCar] B V 20 2 3\n\n"
                "Solution Format:\n"
                "[Move] car_id distance\n"
                "  - distance: number of spaces (negative for left/up)\n"
            )
        else:  # Challenger
            prompt = (
                "Welcome to Car Puzzle! You are the Challenger (Player 1).\n\n"
                "Game Flow:\n"
                "1. Wait for the Creator to make and verify a puzzle\n"
                "2. Solve the puzzle when it's provided\n\n"
                "Solution Format:\n"
                "[Move] car_id distance\n"
                "Example: [Move] A -3 (moves car A three spaces left)\n"
                "\nYou'll win if you successfully solve the puzzle!\n"
            )
        return prompt

    def reset(self, seed: Optional[int] = None) -> Optional[ta.Observations]:
        """Reset the game to its initial state."""
        if seed is not None:
            random.seed(seed)

        # Calculate the middle of the right wall for goal position
        goal_pos = (self.N - 1) * (self.N // 2)

        # Generate wall positions (all edges except goal)
        wall_positions = set()
        for i in range(self.N):
            wall_positions.add(i)  # Top wall
            wall_positions.add(i * self.N)  # Left wall
            wall_positions.add(i * self.N + (self.N - 1))  # Right wall
            wall_positions.add(i + (self.N * (self.N - 1)))  # Bottom wall
        wall_positions.remove(goal_pos)  # Remove goal position from walls

        return self.state.reset(
            game_state={
                "phase": 1,  # 1: Creation, 2: Creator Solving, 3: Challenger Solving
                "cars": {},  # Dict of car_id -> {orientation, positions}
                "walls": tuple(sorted(wall_positions)),
                "goal": (goal_pos,),
                "creator_solution": None,
                "game_complete": False,
                "winner": None,
                "board_size": self.N
            },
            player_prompt_function=self._generate_player_prompt,
        )

    def _get_car_orientation(self, positions: Tuple[int, ...]) -> str:
        """Determine if a car is horizontal or vertical based on its positions."""
        if len(positions) < 2:
            return None
        if positions[1] - positions[0] == 1:
            return 'H'  # Horizontal
        return 'V'  # Vertical

    def _can_move_car(self, car_id: str, distance: int, cars: Dict, walls: Set[int], N: int) -> bool:
        """Check if a car can move the specified distance."""
        if car_id not in cars:
            return False

        car = cars[car_id]
        positions = car["positions"]
        orientation = car["orientation"]

        # Calculate new positions
        new_positions = []
        if orientation == 'H':
            for pos in positions:
                new_pos = pos + distance
                if new_pos // N != pos // N:  # Check if moving across rows
                    return False
                new_positions.append(new_pos)
        else:  # Vertical
            for pos in positions:
                new_pos = pos + (distance * N)
                if new_pos < 0 or new_pos >= N * N:
                    return False
                new_positions.append(new_pos)

        # Check for collisions with walls and other cars
        occupied = walls.union(*(set(car["positions"]) for cid, car in cars.items() if cid != car_id))
        return not any(pos in occupied for pos in new_positions)

    def _move_car(self, cars: Dict, car_id: str, distance: int) -> Dict:
        """Move a car by the specified distance and return new car positions."""
        if car_id not in cars:
            return cars

        new_cars = dict(cars)
        car = new_cars[car_id]
        orientation = car["orientation"]
        
        # Calculate movement increment
        incr = 1 if orientation == 'H' else self.N
        
        # Update positions
        new_positions = tuple(pos + (distance * incr) for pos in car["positions"])
        new_cars[car_id] = {"orientation": orientation, "positions": new_positions}
        
        return new_cars

    def _check_victory(self, cars: Dict) -> bool:
        """Check if the target car (*) has reached the goal."""
        if '*' not in cars:
            return False
            
        target_positions = set(cars['*']["positions"])
        goal_position = set(self.state.game_state["goal"])
        return bool(target_positions & goal_position)

    def _process_puzzle_creation(self, submission: str) -> Tuple[bool, str]:
        """Process and validate a puzzle creation submission."""
        lines = submission.strip().split('\n')
        cars = {}
        
        for line in lines:
            if match := self.car_pattern.match(line):
                car_id, orientation, x, y, length = match.groups()
                x, y = int(x), int(y)
                length = int(length)
                
                if length not in (2, 3):
                    return False, f"Invalid car length: {length}"
                
                # Calculate positions
                positions = []
                if orientation == 'H':
                    for i in range(length):
                        pos = y * self.N + (x + i)
                        positions.append(pos)
                else:  # Vertical
                    for i in range(length):
                        pos = (y + i) * self.N + x
                        positions.append(pos)
                
                cars[car_id] = {
                    "orientation": orientation,
                    "positions": tuple(positions)
                }

        # Validate car placements
        occupied = set(self.state.game_state["walls"])
        for car_id, car in cars.items():
            if any(pos in occupied for pos in car["positions"]):
                return False, f"Car {car_id} overlaps with walls or other cars"
            occupied.update(car["positions"])

        # Ensure target car exists
        if '*' not in cars:
            return False, "No target car (*) defined"
        if cars['*']["orientation"] != 'H':
            return False, "Target car must be horizontal"

        self.state.game_state["cars"] = cars
        return True, "Puzzle created successfully"

    def step(
        self,
        player_id: int,
        action: str,
    ) -> Tuple[Optional[ta.Observations], Optional[ta.Rewards], bool, bool, ta.Info]:
        """Process a player's action."""
        # Check action format
        self.state.check_action_format(action=action, player_id=player_id)

        # Add action to observations
        self.state.add_observation(
            from_id=player_id,
            to_id=-1,  # Broadcast to all
            message=action
        )

        # Handle different phases
        if self.state.game_state["phase"] == 1:
            if player_id != 0:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=["Only Creator can submit a puzzle"]
                )
            else:
                success, message = self._process_puzzle_creation(action)
                if success:
                    self.state.game_state["phase"] = 2
                    self._show_board()
                    self.state.add_observation(
                        from_id=ta.GAME_ID,
                        to_id=0,
                        message="Puzzle created. Please provide your solution."
                    )
                else:
                    self.state.set_winners(
                        player_ids=[1],
                        reason=f"Invalid puzzle: {message}"
                    )

        elif self.state.game_state["phase"] == 2:
            if player_id != 0:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=["Waiting for Creator's solution"]
                )
            else:
                if self._verify_solution(action):
                    self.state.game_state["creator_solution"] = action
                    self.state.game_state["phase"] = 3
                    self._show_board()
                    self.state.add_observation(
                        from_id=ta.GAME_ID,
                        to_id=1,
                        message="Your turn to solve the puzzle."
                    )
                else:
                    self.state.set_winners(
                        player_ids=[1],
                        reason="Creator's solution failed"
                    )

        elif self.state.game_state["phase"] == 3:
            if player_id != 1:
                self.state.set_invalid_move(
                    player_ids=[player_id],
                    reasons=["Waiting for Challenger's solution"]
                )
            else:
                if self._verify_solution(action):
                    self.state.set_winners(
                        player_ids=[1],
                        reason="Challenger solved the puzzle!"
                    )
                else:
                    self.state.set_winners(
                        player_ids=[0],
                        reason="Challenger's solution failed"
                    )

        return self.state.step()

    def _verify_solution(self, solution: str) -> bool:
        """Verify if a solution successfully solves the puzzle."""
        lines = solution.strip().split('\n')
        cars = dict(self.state.game_state["cars"])
        walls = set(self.state.game_state["walls"])
        
        for line in lines:
            if not (match := self.move_pattern.match(line)):
                return False
            
            car_id, distance = match.groups()
            distance = int(distance)
            
            if not self._can_move_car(car_id, distance, cars, walls, self.N):
                return False
                
            cars = self._move_car(cars, car_id, distance)
            if self._check_victory(cars):
                return True
                
        return False

    def _show_board(self):
        """Display the current board state."""
        board = ['.'] * (self.N * self.N)
        
        # Place walls
        for pos in self.state.game_state["walls"]:
            board[pos] = '|'
            
        # Place goal
        board[self.state.game_state["goal"][0]] = '@'
        
        # Place cars
        for car_id, car in self.state.game_state["cars"].items():
            for pos in car["positions"]:
                board[pos] = car_id
        
        # Create board string
        board_str = '\n'.join(' '.join(board[i:i+self.N]) for i in range(0, self.N*self.N, self.N))
        
        self.state.add_observation(
            from_id=ta.GAME_ID,
            to_id=-1,  # Broadcast to all
            message=f"Current board state:\n{board_str}"
        )

    def close(self):
        """Clean up any resources."""
        pass