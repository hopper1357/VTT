import uuid
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class MapObject:
    """A generic object that can be placed on a map."""
    x: int
    y: int
    layer: int
    display_char: str = '?'
    size: int = 1
    asset_path: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        """Returns a serializable dictionary representation of the object."""
        # This is the base implementation. Subclasses should extend this.
        return {
            'id': self.id,
            'object_type': self.__class__.__name__, # e.g., 'MapObject' or 'Token'
            'x': self.x,
            'y': self.y,
            'layer': self.layer,
            'display_char': self.display_char,
            'size': self.size,
            'asset_path': self.asset_path
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a MapObject from a dictionary.

        Note: This method is for direct creation of a MapObject.
        For deserializing a map's objects, which could be MapObjects or
        subclasses like Tokens, a factory pattern in the Map class is needed.
        """
        obj = cls(
            x=data['x'],
            y=data['y'],
            layer=data.get('layer', 0), # Default layer 0
            display_char=data.get('display_char', '?'),
            size=data.get('size', 1),
            asset_path=data.get('asset_path')
        )
        obj.id = data['id']
        return obj
