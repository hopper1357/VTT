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
        # This is a bit tricky with inheritance and dataclasses.
        # We need to extract the args for the parent and for the child.

        # Args for MapObject
        map_object_args = {
            'x': data['x'],
            'y': data['y'],
            'layer': data.get('layer', 4), # Default token layer
            'display_char': data.get('display_char', '?'),
            'size': data.get('size', 1),
            'asset_path': data.get('asset_path')
        }

        # Arg for Token
        entity_id = data['entity_id']

        # We can't use the kw_only solution, so we call the constructor
        # with all arguments.
        token = cls(
            entity_id=entity_id,
            x=map_object_args['x'],
            y=map_object_args['y'],
            layer=map_object_args['layer'],
            display_char=map_object_args['display_char'],
            size=map_object_args['size'],
            asset_path=map_object_args['asset_path']
        )
        token.id = data['id']
        return token
