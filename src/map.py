from dataclasses import dataclass, field
from typing import List
from enum import Enum, auto
from .token import Token

class GridType(Enum):
    SQUARE = auto()
    HEX = auto()

@dataclass
class Map:
    """Represents a game map holding tokens, with a specific grid type."""
    name: str
    width: int
    height: int
    tokens: List[Token] = field(default_factory=list)
    grid_type: GridType = GridType.SQUARE

    def add_token(self, token: Token):
        """Adds a token to the map."""
        if not any(t.id == token.id for t in self.tokens):
            self.tokens.append(token)

    def remove_token(self, token_id: str):
        """Removes a token from the map by its ID."""
        self.tokens = [t for t in self.tokens if t.id != token_id]

    def get_token(self, token_id: str):
        """Retrieves a token from the map by its ID."""
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
            'grid_type': self.grid_type.name,  # Store enum by name
            'tokens': [token.to_dict() for token in self.tokens]
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a map from a dictionary."""
        grid_type_name = data.get('grid_type', 'SQUARE')
        try:
            grid_type = GridType[grid_type_name]
        except KeyError:
            print(f"Warning: Unknown grid type '{grid_type_name}'. Defaulting to SQUARE.")
            grid_type = GridType.SQUARE

        map_instance = cls(
            name=data['name'],
            width=data['width'],
            height=data['height'],
            grid_type=grid_type
        )
        map_instance.tokens = [Token.from_dict(t_data) for t_data in data.get('tokens', [])]
        return map_instance
