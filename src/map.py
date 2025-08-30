from dataclasses import dataclass, field
from typing import List
from enum import Enum, auto
from .map_object import MapObject
from .token import Token

class GridType(Enum):
    SQUARE = auto()
    HEX = auto()

@dataclass
class Map:
    """Represents a game map holding objects, with a specific grid type."""
    name: str
    width: int
    height: int
    objects: List[MapObject] = field(default_factory=list)
    grid_type: GridType = GridType.SQUARE

    def add_object(self, obj: MapObject):
        """Adds an object to the map."""
        if not any(o.id == obj.id for o in self.objects):
            self.objects.append(obj)

    def remove_object(self, object_id: str):
        """Removes an object from the map by its ID."""
        self.objects = [o for o in self.objects if o.id != object_id]

    def get_object(self, object_id: str):
        """Retrieves an object from the map by its ID."""
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None

    def to_dict(self):
        """Returns a serializable dictionary representation of the map."""
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'grid_type': self.grid_type.name,
            'objects': [obj.to_dict() for obj in self.objects]
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a map from a dictionary, acting as a factory for objects."""
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

        objects_data = data.get('objects', [])
        for obj_data in objects_data:
            obj_type = obj_data.get('object_type')

            new_obj = None
            if obj_type == 'Token':
                new_obj = Token.from_dict(obj_data)
            elif obj_type == 'MapObject':
                new_obj = MapObject.from_dict(obj_data)
            else:
                print(f"Warning: Unknown object type '{obj_type}' found in map data. Skipping.")
                continue

            if new_obj:
                map_instance.objects.append(new_obj)

        return map_instance
