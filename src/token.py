import uuid
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Token:
    """Represents an object on a map, linked to an entity."""
    entity_id: str
    x: int
    y: int
    size: int = 1
    asset_path: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        """Returns a serializable dictionary representation of the token."""
        return {
            'id': self.id,
            'entity_id': self.entity_id,
            'x': self.x,
            'y': self.y,
            'size': self.size,
            'asset_path': self.asset_path
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a token from a dictionary."""
        token = cls(
            entity_id=data['entity_id'],
            x=data['x'],
            y=data['y'],
            size=data.get('size', 1),
            asset_path=data.get('asset_path')
        )
        token.id = data['id']
        return token
