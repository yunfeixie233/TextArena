import re
from typing import Optional, Dict, Tuple, List, Any

import textarena as ta
from textarena.envs.Othello.renderer import create_board_str


BOARD_SIZE = 8
EMPTY, BLACK, WHITE = "", "B", "W"
DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
MOVE_RE = re.compile(r"\[\s*(\d)\s*,?\s*(\d)\s*\]")

def _opponent(p: str) -> str:
    return WHITE if p == BLACK else BLACK

def _in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

class OthelloEnv(ta.Env):
    """Two-player Othello (Reversi) environment."""

    def __init__(self, show_valid: bool = True):
        super().__init__()
        self.show_valid = show_valid

    def get_board_str(self):
        return create_board_str(self.board)

    def reset(self, num_players: int, seed: Optional[int] = None):
        # Initialize game state
        role_mapping = {0: "Black", 1: "White"}
        self.state = ta.State(num_players=num_players, min_players=2, max_players=2, role_mapping=role_mapping)
        
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board[3][3] = self.board[4][4] = WHITE
        self.board[3][4] = self.board[4][3] = BLACK

        # Precompute counts and valid moves for first prompt (Black starts)
        b_count, w_count = self._counts()
        valid_moves = self._valid_moves(BLACK)

        game_state = {"board": self.board, "rendered_board": self._render_board(), "black_count": b_count, "white_count": w_count, "valid_moves": valid_moves}
        self.state.reset(seed=seed, game_state=game_state, player_prompt_function=self._generate_player_prompt,)

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        pid = self.state.current_player_id
        piece = BLACK if pid == 0 else WHITE
        opp = _opponent(piece)

        self.state.add_observation(pid, -1, action)
        valid = self._valid_moves(piece)
        # self.state.game_state["valid_moves"] = valid

        # If no moves, skip or end
        if not valid:
            self._handle_skip(pid, piece, opp)
            return self.state.step()

        # Parse move
        match = MOVE_RE.search(action)
        if match is None:
            self.state.set_invalid_move(pid, "Move must be of the form [row, col] with 0-7 indices.")
            return self.state.step(rotate_player=False)

        r, c = int(match.group(1)), int(match.group(2))
        if [r, c] not in valid:
            self.state.set_invalid_move(pid, f"Illegal move. Valid moves: {valid}")
            return self.state.step(rotate_player=False)

        # Make move
        flipped = self._place_and_flip(r, c, piece)

        next_valid = self._valid_moves(opp)
        self.state.game_state["valid_moves"] = next_valid  # store only this

        # Update board / counts
        self._push_gamestate()

        # Build the message that every player sees
        observation = (
            f"Player {pid} ({piece}) played [{r}, {c}] "
            f"flipping {flipped} piece(s).\n\n"
            f"{self.state.game_state['rendered_board']}"
        )
        if self.show_valid:
            observation += (
                "\nValid moves: " + ", ".join(map(str, next_valid))
                if next_valid else
                "\nNo valid moves – you may have to skip."
            )
        observation += (
            f"\nScores - Black: {self.state.game_state['black_count']}, "
            f"White: {self.state.game_state['white_count']}\n"
        )
        self.state.add_observation(ta.GAME_ID, -1, observation)


        # valid = self._valid_moves(piece)
        # self.state.game_state["valid_moves"] = valid


        # # Update and broadcast board
        # self._push_gamestate()
        # observation = f"Player {pid} ({piece}) played [{r}, {c}] flipping {flipped} piece(s).\n\n{self.state.game_state['rendered_board']}"
        # if self.show_valid:
        #     moves = self.state.game_state.get("valid_moves", [])
        #     observation += "\nValid moves: " + ", ".join(map(str, moves)) if moves else "No valid moves - you may have to skip."
        # observation += f"\nScores - Black: {self.state.game_state['black_count']}, White: {self.state.game_state['white_count']}\n"
        # self.state.add_observation(ta.GAME_ID, -1, observation)

        # Check end condition
        if self._game_over():
            self._declare_winner()
        else:
            self.state.game_state["valid_moves"] = self._valid_moves(opp)

        return self.state.step()

    def _handle_skip(self, pid: int, piece: str, opp: str):
        self.state.add_observation(ta.GAME_ID, -1, f"Player {pid} ({piece}) has no valid moves and must skip.")
        if not self._valid_moves(opp):
            self._declare_winner()
        else:
            self.state.game_state["valid_moves"] = self._valid_moves(opp)

    def _valid_moves(self, piece: str) -> List[List[int]]:
        return [[r, c] for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.board[r][c] == EMPTY and self._would_flip(r, c, piece)]

    def _would_flip(self, r: int, c: int, piece: str) -> bool:
        opp = _opponent(piece)
        for dr, dc in DIRS:
            rr, cc = r + dr, c + dc
            if not (_in_bounds(rr, cc) and self.board[rr][cc] == opp):
                continue
            while _in_bounds(rr, cc) and self.board[rr][cc] == opp:
                rr += dr; cc += dc
            if _in_bounds(rr, cc) and self.board[rr][cc] == piece:
                return True
        return False

    def _place_and_flip(self, r: int, c: int, piece: str) -> int:
        opp = _opponent(piece)
        self.board[r][c] = piece
        flipped = 0
        for dr, dc in DIRS:
            rr, cc = r + dr, c + dc
            line: List[Tuple[int, int]] = []
            while _in_bounds(rr, cc) and self.board[rr][cc] == opp:
                line.append((rr, cc))
                rr += dr; cc += dc
            if _in_bounds(rr, cc) and self.board[rr][cc] == piece:
                for fr, fc in line:
                    self.board[fr][fc] = piece
                flipped += len(line)
        return flipped

    def _counts(self) -> Tuple[int, int]:
        b = sum(row.count(BLACK) for row in self.board)
        w = sum(row.count(WHITE) for row in self.board)
        return b, w

    def _game_over(self) -> bool:
        full = all(cell != EMPTY for row in self.board for cell in row)
        return full or (not self._valid_moves(BLACK) and not self._valid_moves(WHITE))

    def _declare_winner(self):
        b, w = self._counts()
        if b > w:
            self.state.set_winners([0], f"Black wins {b}-{w}.")
        elif w > b:
            self.state.set_winners([1], f"White wins {w}-{b}.")
        else:
            self.state.set_draw(f"Draw {b}-{w}.")

    def _render_board(self) -> str:
        header = "  " + " ".join(map(str, range(BOARD_SIZE)))
        rows = [header]
        for i, row in enumerate(self.board):
            cells = [cell if cell else "." for cell in row]
            rows.append(f"{i}|" + "|".join(cells) + "|")
        return "\n".join(rows)

    def _push_gamestate(self):
        b, w = self._counts()
        self.state.game_state.update({"rendered_board": self._render_board(), "black_count": b, "white_count": w})

    def _generate_player_prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        piece, colour = (BLACK, "Black") if player_id == 0 else (WHITE, "White")
        prompt = (
            f"You are playing {colour} ({piece}). Provide your move as [row, col].\n\n"
            f"Current board:\n{game_state['rendered_board']}\n\n"
            f"Scores - Black: {game_state['black_count']}, White: {game_state['white_count']}\n"
        )
        if self.show_valid:
            moves = game_state.get("valid_moves", [])
            prompt += "Valid moves: " + ", ".join(map(str, moves)) if moves else "No valid moves - you may have to skip."
        return prompt
