from dataclasses import dataclass, field
from typing import List

@dataclass
class Map:
    """Represents a game map with a grid."""
    name: str
    width: int
    height: int
    grid: List[List[str]] = field(default_factory=list)

    def __post_init__(self):
        """Initializes the grid after the object is created."""
        if not self.grid:
            self.grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
