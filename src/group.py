from dataclasses import dataclass, field
from typing import List
from .map_object import MapObject

@dataclass
class Group(MapObject):
    """Represents a group of map objects, allowing them to be manipulated as a single unit."""
    object_ids: List[str] = field(default_factory=list)

    def to_dict(self):
        """Returns a serializable dictionary representation, including the list of object IDs."""
        data = super().to_dict()
        data.update({
            'object_ids': self.object_ids
        })
        # Override object_type to be specific
        data['object_type'] = self.__class__.__name__
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a Group object from a dictionary."""
        # This creates an instance of Group
        obj = super().from_dict(data)
        obj.object_ids = data.get('object_ids', [])
        return obj
