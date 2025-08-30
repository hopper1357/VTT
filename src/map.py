from dataclasses import dataclass, field
from typing import List
from .token import Token

@dataclass
class Map:
    """Represents a game map with a grid and tokens."""
    name: str
    width: int
    height: int
    grid: List[List[str]] = field(default_factory=list)
    tokens: List[Token] = field(default_factory=list)

    def __post_init__(self):
        """Initializes the grid after the object is created."""
        if not self.grid:
            self.grid = [['.' for _ in range(self.width)] for _ in range(self.height)]

    def add_token(self, token: Token):
        """Adds a token to the map."""
        if not any(t.id == token.id for t in self.tokens):
            self.tokens.append(token)

    def remove_token(self, token_id: str):
        """Removes a token from the map by its ID."""
        self.tokens = [t for t in self.tokens if t.id != token_id]

    def get_token(self, token_id: str):
        """Retrievels a token from the map by its ID."""
        for token in self.tokens:
            if token.id == token_id:
                return token
        return None

    def to_dict(self):
        """Returns a serializable dictionary representation of the map."""
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'grid': self.grid,
            'tokens': [token.to_dict() for token in self.tokens]
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a map from a dictionary."""
        map_instance = cls(
            name=data['name'],
            width=data['width'],
            height=data['height'],
            grid=data.get('grid', [])
        )
        map_instance.tokens = [Token.from_dict(t_data) for t_data in data.get('tokens', [])]
        return map_instance
