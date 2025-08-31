from dataclasses import dataclass, field
from typing import Optional
from .map_object import MapObject

@dataclass
class Drawable(MapObject):
    """A base class for objects that can be drawn on the map, extending MapObject."""
    stroke_color: str = "#000000"  # Default to black
    stroke_width: int = 2
    opacity: float = 1.0

    def to_dict(self):
        """Returns a serializable dictionary representation, including drawable properties."""
        data = super().to_dict()
        data.update({
            'stroke_color': self.stroke_color,
            'stroke_width': self.stroke_width,
            'opacity': self.opacity
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a Drawable object from a dictionary."""
        # This creates an instance of the class that calls this method (e.g., ShapeObject)
        obj = super().from_dict(data)
        obj.stroke_color = data.get('stroke_color', "#000000")
        obj.stroke_width = data.get('stroke_width', 2)
        obj.opacity = data.get('opacity', 1.0)
        return obj
