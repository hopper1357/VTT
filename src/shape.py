from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional
from .drawable import Drawable

class ShapeType(Enum):
    CIRCLE = auto()
    SQUARE = auto()
    TRIANGLE = auto()
    HEXAGON = auto()

@dataclass
class Shape(Drawable):
    """Represents a geometric shape that can be placed on the map."""
    shape_type: ShapeType = ShapeType.CIRCLE
    fill_color: Optional[str] = None  # e.g., "#FF0000" for red fill

    def to_dict(self):
        """Returns a serializable dictionary representation, including shape properties."""
        data = super().to_dict()
        data.update({
            'shape_type': self.shape_type.name,
            'fill_color': self.fill_color
        })
        # Override object_type to be more specific
        data['object_type'] = self.__class__.__name__
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a Shape object from a dictionary."""
        obj = super().from_dict(data)

        shape_type_name = data.get('shape_type', 'CIRCLE')
        try:
            obj.shape_type = ShapeType[shape_type_name]
        except KeyError:
            print(f"Warning: Unknown shape type '{shape_type_name}'. Defaulting to CIRCLE.")
            obj.shape_type = ShapeType.CIRCLE

        obj.fill_color = data.get('fill_color')
        return obj
