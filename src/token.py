from dataclasses import dataclass, field
from .map_object import MapObject

@dataclass
class Token(MapObject):
    """A MapObject that is linked to a specific game entity."""
    entity_id: str = None

    def __post_init__(self):
        """Ensure that an entity_id is always provided."""
        if self.entity_id is None:
            raise ValueError("Token must be created with a valid entity_id.")

    def to_dict(self):
        """Returns a serializable dictionary representation of the token."""
        data = super().to_dict()
        data['entity_id'] = self.entity_id
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a Token from a dictionary."""
        # We need to extract the args for the parent and for the child.
        entity_id = data['entity_id']

        # We call the constructor with all arguments.
        token = cls(
            entity_id=entity_id,
            x=data['x'],
            y=data['y'],
            layer=data.get('layer', 4),
            display_char=data.get('display_char', '?'),
            size=data.get('size', 1),
            asset_path=data.get('asset_path'),
            blocks_light=data.get('blocks_light', False),
            light_radius=data.get('light_radius')
        )
        token.id = data['id']
        return token
