# ── replace the old helper block with this one ─────────────────────────────
import re, pathlib, textwrap
from math import gcd
from itertools import islice
import re, textwrap, json, pathlib
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Set


HexCoord = Tuple[int, int]         # (q, r)   axial   (flat-top)
InterCoord = Tuple[int, int, int]    # cube coords – uniquely identifies a corner
EdgeCoord = Tuple[InterCoord, InterCoord]
AXIAL2CUBE = lambda q, r: (q, -q - r, r)
CUBE2AXIAL = lambda x, y, z: (x, z)            # because y = -x-z



class Terrain(Enum):
    BRICK = "brick"
    WOOD = "wood"
    ORE = "ore"
    WHEAT = "wheat"
    SHEEP = "sheep"
    DESERT = "desert" # produces nothing
    def __str__(self): return self.value

class Piece(Enum):
    ROAD = auto()
    SETTLEMENT = auto()
    CITY = auto()

class Color(Enum):
    BLUE = 0
    ORANGE = 1
    WHITE = 2
    RED = 3
    def __str__(self): return self.name.lower()

def _coord_key(coord: HexCoord) -> str:
    """Convert axial coord to template key root, e.g. (-1,2) → 'C_12'."""
    q, r = coord
    def part(n: int) -> str:  return str(n) if n >= 0 else "_" + str(-n)
    return "C" + part(q) + part(r)           # 'C' prefix is part of template


class _SafeDict(dict):
    """format_map replacement-dict that returns '' for unknown keys."""
    def __missing__(self, k): return ""



@dataclass(eq=False)
class Intersection:
    coord: InterCoord
    neighbours: Set['Intersection'] = field(default_factory=set, repr=False)
    adjacent_hexes: Set[HexCoord]   = field(default_factory=set, repr=False)
    piece: Optional[Piece] = None
    owner: Optional[Color] = None

    def __hash__(self): return hash(self.coord)
    def __eq__(self, other): return isinstance(other, Intersection) and self.coord == other.coord
    def __repr__(self):      # optional – a concise one-liner
        tag = f"{self.piece.name[0]}" if self.piece else "_"
        return f"Intersection{self.coord}<{tag}>"


@dataclass
class Edge:                              # 72 of these
    ends: EdgeCoord                     # (cornerA, cornerB) – sorted
    adjacent_hexes: Set[HexCoord]       # 1 or 2 tiles
    owner: Optional[Color] = None       # road or None


@dataclass
class Hex:
    coord: HexCoord
    terrain: Terrain
    token: Optional[int] # None for desert
    has_robber: bool = False
    def produces(self) -> Optional[str]: return None if self.terrain is Terrain.DESERT else self.terrain.value

# 1) keep your OLD template string here (the one in your message)
_OLD_TEMPLATE = """
                                   _        _
                                  ╱{P0_23O}╲______╱{P0_32O}╲        
                                  ╲{P0_23C}╱      ╲{P0_32C}╱   
                        _        _╱▔        ▔╲_        _
                       ╱{P_1_13O}╲______╱{P_1_22O}╲  {C02T:^5}   ╱{P1_22O}╲______╱{P1_31O}╲
                       ╲{P_1_13C}╱      ╲{P_1_22C}╱   [{C02N:^2}]   ╲{P1_22C}╱      ╲{P1_31C}╱
             _        _╱▔        ▔╲_        _╱▔        ▔╲_        _ 
            ╱{P_203O}╲______╱{P_2_12O}╲   {C_12T:^5}  ╱{P0_12O}╲______╱{P0_21O}╲   {C11T:^5}  ╱{P2_21O}╲______╱{P2_30O}╲
            ╲{P_203C}╱      ╲{P_2_12C}╱   [{C_12N:^2}]   ╲{P0_12C}╱      ╲{P0_21C}╱    [{C11N:^2}]  ╲{P2_21C}╱      ╲{P2_30C}╱ 
           _╱▔        ▔╲_        _╱▔        ▔╲_        _╱▔        ▔╲_   
          ╱{P_302O}╲  {C_22T:^5}   ╱{P_102O}╲______╱{P_1_11O}╲  {C01T:^5}   ╱{P1_11O}╲______╱{P1_20O}╲  {C20T:^5}   ╱{P3_20O}╲
          ╲{P_302C}╱   [{C_22N:^2}]   ╲{P_102C}╱      ╲{P_1_11C}╱   [{C01N:^2}]   ╲{P1_11C}╱      ╲{P1_20C}╱   [{C20N:^2}]   ╲{P3_20C}╱
           ▔╲_         ╱▔        ▔╲_        _╱▔        ▔╲_        _╱▔ 
            ╱{P_212O}╲______╱{P_201O}╲   {C_11T:^5}  ╱{P001O}╲______╱{P0_10O}╲   {C10T:^5}  ╱{P2_10O}╲______╱{P2_2_1C}╲
            ╲{P_212C}╱      ╲{P_201C}╱   [{C_11N:^2}]   ╲{P001C}╱      ╲{P0_10C}╱    [{C10N:^2}]  ╲{P2_10C}╱      ╲{P2_2_1C}╱
           _╱▔        ▔╲_        _╱▔        ▔╲_        _╱▔        ▔╲_ 
          ╱{P_311O}╲   {C_21T:^5}  ╱{P_111O}╲______╱{P_100O}╲  {C00T:^6}  ╱{P1_0_0C}╲______╱{P1_1_1C}╲  {C2_1T:^5}   ╱{P3_1_1C}╲
          ╲{P_311C}╱   [{C_21N:^2}]   ╲{P_111C}╱      ╲{P_100C}╱   [{C00N:^2}]   ╲{1_0_C}╱      ╲{P1_1_1C}╱   [{C2_1N:^2}]   ╲{P3_1_1C}╱
           ▔╲_        _╱▔        ▔╲_        _╱▔        ▔╲_        _╱▔ 
            ╱{P_221O}╲______╱{P_210O}╲  {C_10T:^5}   ╱{P010O}╲______╱{P00_1O}╲  {C1_1T:^5}   ╱{P20_1C}╲______╱{P2_1_2C}╲
            ╲{P_221C}╱      ╲{P_210C}╱   [{C_10N:^2}]   ╲{P010C}╱      ╲{P00_1C}╱   [{C1_1N:^2}]   ╲{P20_1C}╱      ╲{P2_1_2C}╱            
           _╱▔        ▔╲_        _╱▔        ▔╲_        _╱▔        ▔╲_              
          ╱{P_320O}╲  {C_20T:^5}   ╱{P_120O}╲______╱{P_11_1O}╲   {C0_1T:^5}  ╱{P11_1O}╲______╱{P10_2O}╲  {C2_2T:^5}   ╱{P30_2O}╲               
          ╲{P_320C}╱   [{C_20N:^2}]   ╲{P_120C}╱      ╲{P_11_1C}╱   [{C0_1N:^2}]   ╲{P11_1C}╱      ╲{P10_2C}╱    [{C2_2N:^2}]  ╲{P30_2C}╱              
           ▔╲_        _╱▔        ▔╲_        _╱▔        ▔╲_        _╱▔             
            ╱{P_230O}╲______╱{P_22_1O}╲  {C_1_1T:^5}   ╱{P11_1O}╲______╱{P10_2O}╲   {C1_2T:^5}  ╱{P21_2O}╲______╱{P20_3O}╲            
            ╲{P_230O}╱      ╲{P_22_1O}╱   [{C_1_1N:^2}]   ╲{P11_1C}╱      ╲{P10_2C}╱    [{C1_2N:^2}]  ╲{P21_2C}╱      ╲{P20_3C}╱       
             ▔        ▔╲_        _╱▔        ▔╲_        _╱▔        ▔         
                       ╱{P_13_1O}╲______╱{P_12_2O}╲   {P0_2T:^5}  ╱{P12_2O}╲______╱{P11_3O}╲                     
                       ╲{P_13_1C}╱      ╲{P_12_2C}╱   [{P0_2N:^2}]   ╲{P12_2C}╱      ╲{P11_3C}╱                
                        ▔        ▔╲_        _╱▔        ▔               
                                  ╱{P03_2O}╲______╱{P02_3O}╲                                  
                                  ╲{P03_2C}╱      ╲{P02_3C}╱                                                                 
                                   ▔        ▔                         
"""

class Board:
    # axial directions (for neighbour hexes)
    HEX_OFFSETS = [(+1,  0), (+1, -1), ( 0, -1),
                   (-1,  0), (-1, +1), ( 0, +1)]

    # six vertex vectors on the triple grid (clockwise, NE first)
    #   centre (x,y,z)*3  +  (dx,dy,dz)  ⇒  vertex
    CORNER_OFFSETS = [
        ( 2, -1, -1),   # NE
        ( 1,  1, -2),   # ENE
        (-1,  2, -1),   # WNW
        (-2,  1,  1),   # NW
        (-1, -1,  2),   # WSW
        ( 1, -2,  1),   # ESE
    ]

    def __init__(self):
        self.hexes:   Dict[HexCoord, Hex]    = {}
        self.corners: Dict[InterCoord, Intersection] = {}
        self.edges:   Dict[frozenset, Edge]  = {}
        self.robber:  Optional[HexCoord]     = None

    # ── public helpers ────────────────────────────────────────────────────
    def neighbour_hexes(self, h: HexCoord) -> list[HexCoord]:
        q, r = h
        return [(q+dq, r+dr) for dq,dr in Board.HEX_OFFSETS if (q+dq, r+dr) in self.hexes]

    def corners_of_hex(self, h: HexCoord) -> list[InterCoord]:
        """Return the 6 cube coordinates of the hex’s vertices (×3 grid)."""
        x, y, z = AXIAL2CUBE(*h)
        # hop onto the triple grid
        x3, y3, z3 = 3*x, 3*y, 3*z
        return [(x3+dx, y3+dy, z3+dz) for dx,dy,dz in Board.CORNER_OFFSETS]

    def edges_of_hex(self, h: HexCoord) -> list[frozenset]:
        cs = self.corners_of_hex(h)
        return [frozenset((cs[i], cs[(i+1)%6])) for i in range(6)]

    # ── construction – default 3-4-5-4-3 board ───────────────────────────
    @classmethod
    def build_standard(cls) -> "Board":
        board = cls()

        # ── 19 hex tiles with terrain + token (centre row first just for readability)
        board.hexes = {
            # r =  0
            (-2,  0): Hex((-2,  0), Terrain.WHEAT,  9 ),
            (-1,  0): Hex((-1,  0), Terrain.WOOD,  11),
            ( 0,  0): Hex(( 0,  0), Terrain.DESERT, None, True),
            ( 1,  0): Hex(( 1,  0), Terrain.WOOD,   3 ),
            ( 2,  0): Hex(( 2,  0), Terrain.ORE,    8 ),

            # r = +1
            (-2,  1): Hex((-2,  1), Terrain.WHEAT, 12),
            (-1,  1): Hex((-1,  1), Terrain.BRICK,  6),
            ( 0,  1): Hex(( 0,  1), Terrain.SHEEP,  4),
            ( 1,  1): Hex(( 1,  1), Terrain.BRICK, 10),

            # r = -1
            (-1, -1): Hex((-1, -1), Terrain.WOOD,   8),
            ( 0, -1): Hex(( 0, -1), Terrain.ORE,    3),
            ( 1, -1): Hex(( 1, -1), Terrain.WHEAT,  4),
            ( 2, -1): Hex(( 2, -1), Terrain.SHEEP,  5),

            # r = +2  (top)
            (-2,  2): Hex((-2,  2), Terrain.ORE,   10),
            (-1,  2): Hex((-1,  2), Terrain.SHEEP,  2),
            ( 0,  2): Hex(( 0,  2), Terrain.WOOD,   9),

            # r = -2  (bottom)
            ( 0, -2): Hex(( 0, -2), Terrain.BRICK,  5),
            ( 1, -2): Hex(( 1, -2), Terrain.WHEAT,  6),
            ( 2, -2): Hex(( 2, -2), Terrain.SHEEP, 11),
        }

        # ── populate corners & edges ────────────────────────────────────
        for h_coord in board.hexes:
            # vertices
            for v in board.corners_of_hex(h_coord):
                inter = board.corners.setdefault(v, Intersection(v))
                inter.adjacent_hexes.add(h_coord)

            # edges
            for e_id in board.edges_of_hex(h_coord):
                a, b = e_id
                edge = board.edges.setdefault(e_id, Edge((a, b), set()))
                edge.adjacent_hexes.add(h_coord)

        # link neighbouring intersections (cube distance 1 on ×3 grid)
        for inter in board.corners.values():
            x,y,z = inter.coord
            for dx,dy,dz in Board.CORNER_OFFSETS:      # distance-1 in ×3 lattice
                nb = (x+dx, y+dy, z+dz)
                if nb in board.corners:
                    inter.neighbours.add(board.corners[nb])

        # ── sanity checks ───────────────────────────────────────────────
        assert len(board.hexes)   == 19, "need 19 tiles"
        assert len(board.corners) == 54, "need 54 intersections"
        assert len(board.edges)   == 72, "need 72 edges"
        return board

def _corner_key(cube: InterCoord) -> str:
    """ Convert cube vertex coord → template key, e.g. (0, -2, 3) → 'P0_23'"""
    x, y, z = cube                       # already integers, already sum ±1
    def part(n: int) -> str: return str(n) if n >= 0 else "_" + str(-n)
    print("P" + part(x) + part(y) + part(z))
    return "P" + part(x) + part(y) + part(z)


# --------------------------------------------------------------------------
# --- decode the old tag ---------------------------------------------------
def old_key_to_coords(key: str) -> tuple[int, int, int]:
    """P_7_18  →  (-7, -1, 8)"""
    s = key[1:]               # drop leading 'P'
    nums, i = [], 0
    while i < len(s):
        sign = -1 if s[i] == '_' else +1
        if s[i] == '_': i += 1
        nums.append(sign * int(s[i]))
        i += 1
    if len(nums) != 3:
        raise ValueError(f"{key}: expected 3 numbers")
    return tuple(nums)


# --- map old root → new root ---------------------------------------------
def make_corner_map(board: Board) -> dict[str, str]:
    new_roots = {_corner_key(c) for c in board.corners}
    mapping   = {}

    for m in re.finditer(r"\{(P[^:}]+?)[OC](?=[:}])", _OLD_TEMPLATE):
        old_root = m.group(1)
        if old_root in mapping:
            continue

        ox, oy, oz = old_key_to_coords(old_root)
        s          = ox + oy + oz                 #  1, -1, or 0
        nx, ny, nz = 3*ox - s, 3*oy - s, 3*oz - s
        new_root   = _corner_key((nx, ny, nz))

        if new_root not in new_roots:
            raise ValueError(
                f"{old_root}: mapped to ({nx},{ny},{nz}) "
                f"which does not exist on the board"
            )
        mapping[old_root] = new_root

    return mapping


def build_new_template():
    board = Board.build_standard()
    cmap  = make_corner_map(board)

    def repl(match):
        root, spec = match.group(1), match.group(2) or ""
        if root[:-1] in cmap:                       # remove trailing O/C
            new_root = cmap[root[:-1]] + root[-1]   # append O/C back
            return "{" + new_root + spec + "}"
        return match.group(0)                      # untouched

    newer = re.sub(r"\{(P[^:}]+?)([OC])(:[^}]*)?\}", repl, _OLD_TEMPLATE)

    out = pathlib.Path("updated_template.txt")
    out.write_text(textwrap.dedent(newer))
    print(f"✅  New template written to {out.absolute()}\n"
          f"   Copy its content back into your code as _TEMPLATE.")

# --------------------------------------------------------------------------
if __name__ == "__main__":
    build_new_template()
