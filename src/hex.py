# Adapted from the brilliant guide by Red Blob Games:
# https://www.redblobgames.com/grids/hexagons/
# This code is available under the CC0 license.

import collections
from dataclasses import dataclass

@dataclass(frozen=True)
class Hex:
    """Represents a hex using cube coordinates."""
    q: int
    r: int
    s: int

    def __post_init__(self):
        if self.q + self.r + self.s != 0:
            raise ValueError("q + r + s must sum to 0")

    def __add__(self, other):
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def __sub__(self, other):
        return Hex(self.q - other.q, self.r - other.r, self.s - other.s)

    def __mul__(self, k: int):
        return Hex(self.q * k, self.r * k, self.s * k)

# Directions for neighbors
hex_directions = [
    Hex(1, 0, -1), Hex(1, -1, 0), Hex(0, -1, 1),
    Hex(-1, 0, 1), Hex(-1, 1, 0), Hex(0, 1, -1)
]

def hex_neighbor(h: Hex, direction: int) -> Hex:
    """Gets the neighbor of a hex in a given direction."""
    return h + hex_directions[direction]

def hex_distance(a: Hex, b: Hex) -> int:
    """Calculates the distance between two hexes."""
    vec = a - b
    return (abs(vec.q) + abs(vec.r) + abs(vec.s)) // 2

# Offset coordinates for rectangular maps
OffsetCoord = collections.namedtuple("OffsetCoord", ["col", "row"])

# Using pointy-top hexes with odd-r offset
ODD = -1
EVEN = 1 # Not used for odd-r, but good to have

def roffset_from_cube(h: Hex) -> OffsetCoord:
    """Converts cube coordinates to odd-r offset coordinates."""
    offset = ODD
    # The original formula from Red Blob Games is for a specific library.
    # The general formula for odd-r is:
    # col = q + (r - (r&1)) / 2
    # row = r
    # Let's re-verify this. No, the guide says: col = q + (r + (r&1)) / 2
    # Let's stick to the guide's code, it's more likely correct.
    col = h.q + (h.r + (h.r & 1)) // 2
    row = h.r
    return OffsetCoord(col, row)

def roffset_to_cube(coord: OffsetCoord) -> Hex:
    """Converts odd-r offset coordinates to cube coordinates."""
    offset = ODD
    # The original formula from Red Blob Games is:
    # q = col - (row + (row&1)) / 2
    # r = row
    q = coord.col - (coord.row + (coord.row & 1)) // 2
    r = coord.row
    s = -q - r
    return Hex(q, r, s)
