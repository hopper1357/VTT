# This implementation is a Python adaptation of the brilliant shadow casting
# algorithm described by Bob Nystrom in his article:
# https://journal.stuffwithstuff.com/2015/09/07/what-the-hero-sees/

from collections import namedtuple

# A simple tuple to represent a shadow's start and end slopes.
Shadow = namedtuple("Shadow", ["start", "end"])

class ShadowLine:
    """Manages a list of shadows, keeping them sorted and merged."""
    def __init__(self):
        self._shadows = []

    def is_in_shadow(self, projection):
        """Checks if a given projection is completely covered by shadows."""
        for shadow in self._shadows:
            if shadow.start <= projection.start and shadow.end >= projection.end:
                return True
        return False

    def add(self, shadow):
        """Adds a new shadow to the line, merging with existing shadows."""
        index = 0
        for index, s in enumerate(self._shadows):
            if s.start >= shadow.start:
                break
        else:
            index += 1

        # Overlap with the previous shadow
        if index > 0 and self._shadows[index - 1].end > shadow.start:
            overlapping_previous = self._shadows[index - 1]
        else:
            overlapping_previous = None

        # Overlap with the next shadow
        if index < len(self._shadows) and self._shadows[index].start < shadow.end:
            overlapping_next = self._shadows[index]
        else:
            overlapping_next = None

        if overlapping_next:
            if overlapping_previous:
                # Overlaps both, merge previous and next, and discard new
                overlapping_previous.end = overlapping_next.end
                self._shadows.pop(index)
            else:
                # Overlaps next, merge with it
                self._shadows[index] = Shadow(shadow.start, overlapping_next.end)
        else:
            if overlapping_previous:
                # Overlaps previous, merge with it
                self._shadows[index - 1] = Shadow(overlapping_previous.start, shadow.end)
            else:
                # No overlap, insert new shadow
                self._shadows.insert(index, shadow)

    @property
    def is_full_shadow(self):
        return len(self._shadows) == 1 and self._shadows[0].start == 0.0 and self._shadows[0].end == 1.0


def _project_tile(row, col):
    """Calculates the start and end slopes of a tile's projection."""
    top_left = col / (row + 2)
    bottom_right = (col + 1) / (row + 1)
    return Shadow(top_left, bottom_right)


def calculate_fov(map_data, origin_x, origin_y, radius):
    """
    Calculates the Field of View for a given map and origin point.
    Returns a set of (x, y) tuples for all visible tiles.
    """
    visible_tiles = set()
    visible_tiles.add((origin_x, origin_y))

    # Pre-calculate positions of blocking objects for faster lookups
    walls = {
        (obj.x, obj.y) for obj in map_data.objects if obj.blocks_light
    }

    for octant in range(8):
        _refresh_octant(map_data, octant, origin_x, origin_y, radius, visible_tiles, walls)

    return visible_tiles


def _refresh_octant(map_data, octant, origin_x, origin_y, radius, visible_tiles, walls):
    line = ShadowLine()
    full_shadow = False

    for row in range(1, radius + 1):
        for col in range(0, row + 1):
            x, y = _transform_octant(row, col, octant)
            abs_x, abs_y = origin_x + x, origin_y + y

            # Stop if we go out of map bounds
            if not (0 <= abs_x < map_data.width and 0 <= abs_y < map_data.height):
                continue

            if full_shadow:
                continue

            projection = _project_tile(row, col)

            is_visible = not line.is_in_shadow(projection)
            if is_visible:
                visible_tiles.add((abs_x, abs_y))
                if (abs_x, abs_y) in walls:
                    line.add(projection)
                    full_shadow = line.is_full_shadow


def _transform_octant(row, col, octant):
    """Transforms octant-local coordinates (row, col) to world-relative (x, y)."""
    if octant == 0: return col, -row
    if octant == 1: return row, -col
    if octant == 2: return row, col
    if octant == 3: return col, row
    if octant == 4: return -col, row
    if octant == 5: return -row, col
    if octant == 6: return -row, -col
    if octant == 7: return -col, -row
    raise ValueError("Invalid octant: " + str(octant))
