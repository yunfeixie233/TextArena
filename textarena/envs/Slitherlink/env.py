import re
from typing import Dict, Tuple, Any, Optional, List, Set

import textarena as ta


class SlitherlinkEnv(ta.Env):
    _ACTION_RE = re.compile(r"\[\s*([hv])\s+(\d+)\s+(\d+)\s*\]", re.I)

    def __init__(self, clues: List[List[Optional[int]]], max_turns: int = 200):
        """ clues  : rectangular list of ints (0-3) or None (blank cells) """
        super().__init__()
        self.clues: List[List[Optional[int]]] = clues
        self.R = len(clues)
        self.C = len(clues[0])
        self.max_turns = max_turns

        # Edge sets         (row, col) index the *upper-left* dot
        self.h_edges: Set[Tuple[int, int]] = set()
        self.v_edges: Set[Tuple[int, int]] = set()

    def reset(self, num_players: int, seed: Optional[int] = None):
        self.h_edges.clear()
        self.v_edges.clear()

        self.state = ta.SinglePlayerState(num_players=num_players, max_turns=self.max_turns, seed=seed)
        self.state.reset(game_state={}, player_prompt_function=self._prompt)
        self._observe()

    def step(self, action: str) -> Tuple[bool, ta.Info]:
        self.state.add_observation(self.state.current_player_id, action, ta.ObservationType.PLAYER_ACTION)

        m = self._ACTION_RE.fullmatch(action.strip().lower())
        if not m:
            self.state.set_invalid_move(self._progress(), "Bad action format.")
            return self.state.step()

        kind, r, c = m.group(1), int(m.group(2)), int(m.group(3))
        if not self._valid_edge(kind, r, c):
            self.state.set_invalid_move(self._progress(), "Edge outside board.")
            return self.state.step()

        self._toggle_edge(kind, r, c)
        self._observe()

        if self._is_solved():                self.state.set_outcome(1.0, "You formed a single loop. Puzzle solved!")
        elif self.state.check_turn_limit():  self.state.set_outcome(self._progress(), "Move limit reached. Puzzle unfinished.")

        return self.state.step()


    def _prompt(self, player_id: int, game_state: Dict[str, Any]) -> str:
        return (
            "You are playing Slitherlink. Draw a single continuous loop so each clue cell has that many bordering edges.\n"
            "Toggle edges with `[h r c]` or `[v r c]`.\n"
        )

    def _valid_edge(self, kind: str, r: int, c: int) -> bool:
        if kind == 'h': return 0 <= r <= self.R and 0 <= c < self.C
        else:           return 0 <= r < self.R and 0 <= c <= self.C # 'v'

    def _toggle_edge(self, kind: str, r: int, c: int):
        if kind == 'h':
            edge = (r, c)
            self.h_edges.discard(edge) if edge in self.h_edges else self.h_edges.add(edge)
        else:
            edge = (r, c)
            self.v_edges.discard(edge) if edge in self.v_edges else self.v_edges.add(edge)

    def _progress(self) -> float:
        """Fraction of clue cells currently satisfied."""
        satisfied = 0
        total = self.R * self.C
        for r in range(self.R):
            for c in range(self.C):
                if self.clues[r][c] is None:
                    total -= 1
                    continue
                if self._cell_edge_count(r, c) == self.clues[r][c]:
                    satisfied += 1
        return satisfied / max(1, total)

    def _cell_edge_count(self, r: int, c: int) -> int:
        cnt = 0
        if (r, c) in self.h_edges:               cnt += 1
        if (r+1, c) in self.h_edges:             cnt += 1
        if (r, c) in self.v_edges:               cnt += 1
        if (r, c+1) in self.v_edges:             cnt += 1
        return cnt

    def _is_solved(self) -> bool:
        # 1. All clues satisfied
        if self._progress() < 1.0: 
            return False
        # 2. Every dot has 0 or 2 incident edges AND at least one edge exists
        if not (self.h_edges or self.v_edges):
            return False
        from collections import defaultdict, deque
        deg = defaultdict(int)
        for (r, c) in self.h_edges:
            deg[(r, c)]     += 1
            deg[(r, c+1)]   += 1
        for (r, c) in self.v_edges:
            deg[(r, c)]     += 1
            deg[(r+1, c)]   += 1
        if any(v not in (0, 2) for v in deg.values()):
            return False
        # 3. Exactly one loop → start BFS from any edge-dot and ensure all
        start = next(iter(deg.keys()))
        seen = set([start])
        q = deque([start])
        while q:
            p = q.popleft()
            for nb in self._neighbors_with_edge(p):
                if nb not in seen:
                    seen.add(nb); q.append(nb)
        return len([p for p in deg if deg[p] == 2]) == len(seen)

    def _neighbors_with_edge(self, dot: Tuple[int, int]):
        r, c = dot
        if (r, c) in self.h_edges:           yield (r, c+1)
        if (r, c-1) in self.h_edges:         yield (r, c-1)
        if (r, c) in self.v_edges:           yield (r+1, c)
        if (r-1, c) in self.v_edges:         yield (r-1, c)

    def _render_board(self) -> str:
        """Row & column indices outside a boxed Slitherlink grid."""
        row_lbl_w = 2                     # 0‒9 fits; tweak if you want 1-based labels
        inner_rows: List[str] = []

        # ── Build the inner grid (no labels, no outer box yet) ──────────────
        for r in range(self.R + 1):
            # dot row:  +──  +──  + … +
            dot_line = ''.join('+' + ('──' if (r, c) in self.h_edges else '  ') for c in range(self.C)) + '+'
            inner_rows.append((True, r, dot_line))        # True = dot row (gets label)
            if r < self.R:
                # clue / vertical-edge row between dot rows
                mid = ''
                for c in range(self.C + 1):
                    mid += '│' if (r, c) in self.v_edges else ' '
                    if c < self.C:
                        clue = self.clues[r][c]
                        mid += f"{clue if clue is not None else '.'} "
                inner_rows.append((False, r, mid.rstrip()))
        inner_w = len(inner_rows[0][2])    # width of the grid content
        lines = []
        lines.append(' ' * (row_lbl_w + 1) + '+' + '-' * inner_w + '+')
        for is_dot, r, content in inner_rows:
            if is_dot:  prefix = f"{r:>{row_lbl_w}d} |"          # row label left of the box
            else:       prefix = ' ' * (row_lbl_w + 1) + '|'     # align under labels
            lines.append(prefix + content.ljust(inner_w) + '|')
        lines.append(' ' * (row_lbl_w + 1) + '+' + '-' * inner_w + '+')
        col_line = ' ' * (row_lbl_w + 1)
        col_line += ''.join(f"{c:>3}" for c in range(self.C + 1))
        lines.append(col_line)

        return '\n'.join(lines)


    def _observe(self):
        self.state.add_observation(message=f"{self._render_board()}\nSatisfied: {self._progress():.0%}", observation_type=ta.ObservationType.GAME_BOARD)
