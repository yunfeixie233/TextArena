import random
from typing import List, Optional, Tuple, Dict, Any

import textarena as ta


class Game2048Env(ta.Env):

    BOARD_SIZE = 4
    ACTIONS = {"[UP]": 0, "[DOWN]": 1, "[LEFT]": 2, "[RIGHT]": 3}
    def __init__(self, target_tile: int = 2048):
        super().__init__()
        self.target_tile = target_tile

    def reset(self, num_players: int, seed: Optional[int] = None):
        # Initialise state & deterministic RNG (for reproducibility if seed)
        self.state = ta.SinglePlayerState(num_players=num_players, seed=seed)
        random.seed(seed)

        board = [[0] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
        # Start with two tiles (usual 2048 opening)
        self._spawn_tile(board)
        self._spawn_tile(board)

        game_state = {"board": board, "score": 0}
        self.state.reset(game_state=game_state, player_prompt_function=self._prompt)
        self._observe_state()

    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            f"You are playing 2048. Your goal is to each a {self.target_tile} tile by sliding identical numbers together!\n"
            "Valid moves: [Up], [Down], [Left], [Right]. Tiles combine when they collide, doubling their value.\n"
        )

    def _observe_state(self):
        board = self.state.game_state["board"]
        score = self.state.game_state["score"]
        # Render board as monospace grid – use "." for empty
        lines = [" ".join(f"{v:4}" if v else "   ." for v in row) for row in board]
        self.state.add_observation(message=f"Score: {score}\n" + "\n".join(lines),observation_type=ta.ObservationType.GAME_BOARD)

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(from_id=self.state.current_player_id, message=action, observation_type=ta.ObservationType.PLAYER_ACTION)
        dir_idx = self._parse_action(action)
        if dir_idx is None:
            self.state.set_invalid_move(reward=self._get_percentage_completion(), reason="Invalid action. Use '[Up]'/'[Down]'/'[Left]'/'[Right]'.",)
            return self.state.step()

        moved, gained = self._apply_move(dir_idx)
        if not moved: # Move had no effect – treat as invalid but continue the episode.
            self.state.set_invalid_move(reward=self._get_percentage_completion(), reason="Board did not change - choose a different direction.")
            return self.state.step()

        self.state.game_state["score"] += gained
        self._spawn_tile(self.state.game_state["board"])

        status = self._check_status()
        if status == "win":     self.state.set_outcome(reward=1.0, reason=f"Congratulations, you reached {self.target_tile}! Final score {self.state.game_state['score']}.")
        elif status == "lose":  self.state.set_outcome(reward=self._get_percentage_completion(), reason=f"No moves left. Max tile {self._max_tile()} - final score {self.state.game_state['score']}.")
        else:                   self._observe_state()

        return self.state.step()

    def _parse_action(self, action: str) -> Optional[int]:
        """Return direction index or *None* if invalid."""
        return self.ACTIONS.get(action.strip().upper())

    def _apply_move(self, dir_idx: int) -> Tuple[bool, int]:
        """Shift the board in *dir_idx* direction.

        Returns (moved?, score_gained).
        0 = Up, 1 = Down, 2 = Left, 3 = Right.
        """
        board = self.state.game_state["board"]
        moved = False
        gained = 0

        # Helper generating *views* of rows/columns, allowing us to reuse
        # the left‑shift logic for every direction.
        def iterable_rows():
            if dir_idx == 0:  # Up: treat each column top→bottom
                for c in range(self.BOARD_SIZE):    yield [board[r][c] for r in range(self.BOARD_SIZE)], c, True
            elif dir_idx == 1:  # Down: column bottom→top (reversed)
                for c in range(self.BOARD_SIZE):    yield [board[r][c] for r in reversed(range(self.BOARD_SIZE))], c, True
            elif dir_idx == 2:  # Left: natural rows
                for r in range(self.BOARD_SIZE):    yield board[r][:], r, False
            else:  # Right: rows reversed
                for r in range(self.BOARD_SIZE):    yield list(reversed(board[r])), r, False

        for line, idx, is_col in iterable_rows():
            original = line[:]
            new_line, delta_score = self._compress_and_merge(line)
            gained += delta_score
            if new_line != original:
                moved = True

            # Write back to *board* with appropriate orientation
            for i, v in enumerate(new_line):
                if is_col:
                    if dir_idx == 0:    board[i][idx] = v # Up: top→bottom
                    else:               board[self.BOARD_SIZE - 1 - i][idx] = v # Down: bottom→top
                else:
                    if dir_idx == 2:    board[idx][i] = v # Left
                    else:               board[idx][self.BOARD_SIZE - 1 - i] = v # Right

        return moved, gained

    def _compress_and_merge(self, line: List[int]) -> Tuple[List[int], int]:
        """Slide non- zero tiles left and merge identical neighbours."""
        tiles = [v for v in line if v != 0]
        score_gain = 0
        i = 0
        while i < len(tiles) - 1:
            if tiles[i] == tiles[i + 1]:
                tiles[i] *= 2
                score_gain += tiles[i]
                del tiles[i + 1]
                i += 1
            else:
                i += 1
        tiles.extend([0] * (self.BOARD_SIZE - len(tiles)))
        return tiles, score_gain

    def _spawn_tile(self, board: List[List[int]]):
        """Spawn a new tile (2 with 90%, 4 with 10%) in a random empty cell."""
        empties = [(r, c) for r in range(self.BOARD_SIZE) for c in range(self.BOARD_SIZE) if board[r][c] == 0]
        if not empties: return
        r, c = random.choice(empties)
        board[r][c] = 4 if random.random() < 0.1 else 2

    def _max_tile(self) -> int:
        return max(max(row) for row in self.state.game_state["board"])

    def _check_status(self) -> str:
        # Win condition
        if self._max_tile() >= self.target_tile:                        return "win"
        # Still space? Continue
        if any(0 in row for row in self.state.game_state["board"]):     return "ongoing"
        # Any possible merge?
        board = self.state.game_state["board"]
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                v = board[r][c]
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.BOARD_SIZE and 0 <= nc < self.BOARD_SIZE and board[nr][nc] == v:
                        return "ongoing"
        return "lose"

    def _get_percentage_completion(self) -> float:
        """Fractional reward used for invalid moves / early termination."""
        return self._max_tile() / self.target_tile
