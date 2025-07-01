import re
from typing import Dict, List, Optional, Tuple, Any

import textarena as ta

class _Vehicle:
    __slots__ = ("vid", "row", "col", "length", "horizontal")

    def __init__(self, vid: str, row: int, col: int, length: int, horizontal: bool):
        self.vid = vid  # single‑letter identifier ("A"–"Z", "X" = target car)
        self.row = row
        self.col = col
        self.length = length
        self.horizontal = horizontal

    def cells(self) -> List[Tuple[int, int]]:
        return [(self.row + (i if not self.horizontal else 0), self.col + (i if self.horizontal else 0)) for i in range(self.length)]

    def front(self, forward: bool) -> Tuple[int, int]:
        """ Return the cell coordinate immediately *in front* of the vehicle if it moved by `+1` in the given direction (True = forward). """
        if self.horizontal:
            if forward:  return (self.row, self.col + self.length) # →
            else:        return (self.row, self.col - 1) # ←
        else:
            if forward:  return (self.row + self.length, self.col) # ↓
            else:        return (self.row - 1, self.col) # ↑

    def move(self, forward: bool):
        if self.horizontal: self.col += 1 if forward else -1
        else:               self.row += 1 if forward else -1


class RushHourEnv(ta.Env):
    BOARD_SIZE = 6
    ACTION_RE = re.compile(r"\[(?P<id>[A-Z])(?P<dir>[+-])\]", re.I)

    def __init__(self):
        super().__init__()
        self.initial_layout: List[_Vehicle] = [
            _Vehicle("X", 2, 1, 2, True),  # target (red) car
            _Vehicle("A", 0, 0, 2, False),
            _Vehicle("B", 0, 3, 3, False),
            _Vehicle("C", 0, 5, 2, False),
            _Vehicle("D", 1, 0, 2, True),
            _Vehicle("F", 1, 4, 2, True),
            _Vehicle("G", 3, 0, 3, False),
            _Vehicle("H", 3, 3, 2, True),
            _Vehicle("I", 4, 4, 2, False),
            _Vehicle("J", 5, 1, 2, True),
            _Vehicle("K", 4, 0, 2, True),
        ]

    def reset(self, num_players: int, seed: Optional[int] = None):
        self.state = ta.SinglePlayerState(num_players=num_players, seed=seed)
        vehicles = {v.vid: _Vehicle(v.vid, v.row, v.col, v.length, v.horizontal) for v in self.initial_layout}
        self.state.reset(game_state={"vehicles": vehicles}, player_prompt_function=self._prompt,)
        self._observe_state()

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            "You are playing a game of RushHour. Slide cars to free the red car [X] and drive it out the right edge.\n"
            "Actions: [A+], [B-], etc.  (+ = forward, - = backward)."
        )

    def _render_board(self) -> str:
        board = [["."] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        for v in self.state.game_state["vehicles"].values():
            for (r, c) in v.cells():
                board[r][c] = v.vid
        # Mark exit
        board[2].append(">")  # row 2 (zero‑indexed) is exit row
        lines = [" ".join(row) for row in board]
        return "\n".join(lines)

    def _observe_state(self):
        self.state.add_observation(message=self._render_board(), observation_type=ta.ObservationType.GAME_BOARD)

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)

        match = self.ACTION_RE.fullmatch(action.strip())
        if not match:
            self.state.set_invalid_move(reward=self._get_percentage_completion(), reason="Invalid action. Use format [A+] / [B-].")
            return self.state.step()

        car_id = match.group("id").upper()
        forward = match.group("dir") == "+"

        vehicles: Dict[str, _Vehicle] = self.state.game_state["vehicles"]
        if car_id not in vehicles:
            self.state.set_invalid_move(reward=self._get_percentage_completion(), reason=f"No car '{car_id}' on the board.")
            return self.state.step()

        moved = self._try_move(vehicles[car_id], forward)
        if not moved:
            self.state.set_invalid_move(reward=self._get_percentage_completion(), reason="Move blocked.")
            return self.state.step()

        # Check win condition
        if self._is_solved():
            self.state.add_observation(message="The red car zooms out! You solved the puzzle.", observation_type=ta.ObservationType.GAME_MESSAGE)
            self.state.set_outcome(reward=1.0, reason="Puzzle solved!")
        else:
            self._observe_state()

        return self.state.step()

    def _occupied(self) -> List[List[Optional[str]]]:
        grid: List[List[Optional[str]]] = [[None] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        for v in self.state.game_state["vehicles"].values():
            for r, c in v.cells():
                grid[r][c] = v.vid
        return grid

    def _try_move(self, car: _Vehicle, forward: bool) -> bool:
        grid = self._occupied()
        rr, cc = car.front(forward)
        # Check target cell in‑bounds and free
        if not (0 <= rr < self.BOARD_SIZE and 0 <= cc < self.BOARD_SIZE):
            # Special case: red car exiting to the right is allowed
            if car.vid == "X" and car.horizontal and forward and rr == car.row and cc == self.BOARD_SIZE:
                car.move(forward)
                return True
            return False
        if grid[rr][cc] is not None:
            return False
        # Move car one step
        car.move(forward)
        return True

    def _is_solved(self) -> bool:
        x = self.state.game_state["vehicles"]["X"]
        return x.horizontal and x.row == 2 and x.col + x.length - 1 == self.BOARD_SIZE  # head at exit

    def _get_percentage_completion(self) -> float:
        """Heuristic: how close is the red car to the exit?"""
        x = self.state.game_state["vehicles"]["X"]
        dist = (self.BOARD_SIZE - x.length) - x.col
        return 1.0 - dist / (self.BOARD_SIZE - x.length)
