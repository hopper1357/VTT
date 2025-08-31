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
    blocks_light: bool = False
    light_radius: Optional[int] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        """Returns a serializable dictionary representation of the object."""
        return {
            'id': self.id,
            'object_type': self.__class__.__name__,
            'x': self.x,
            'y': self.y,
            'layer': self.layer,
            'display_char': self.display_char,
            'size': self.size,
            'asset_path': self.asset_path,
            'blocks_light': self.blocks_light,
            'light_radius': self.light_radius
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a MapObject from a dictionary."""
        obj = cls(
            x=data['x'],
            y=data['y'],
            layer=data.get('layer', 0),
            display_char=data.get('display_char', '?'),
            size=data.get('size', 1),
            asset_path=data.get('asset_path'),
            blocks_light=data.get('blocks_light', False),
            light_radius=data.get('light_radius')
        )
        obj.id = data['id']
        return obj
