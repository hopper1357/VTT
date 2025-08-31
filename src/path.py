from dataclasses import dataclass, field
from typing import List, Tuple
from .drawable import Drawable

@dataclass
class Path(Drawable):
    """Represents a freehand path or line on the map."""
    points: List[Tuple[int, int]] = field(default_factory=list)

    def to_dict(self):
        """Returns a serializable dictionary representation, including the path's points."""
        data = super().to_dict()
        data.update({
            'points': self.points
        })
        # Override object_type to be specific
        data['object_type'] = self.__class__.__name__
        return data

    @classmethod
    def from_dict(cls, data):
        """Creates a Path object from a dictionary."""
        obj = super().from_dict(data)
        # The points are stored as a list of lists in JSON, so convert them back to tuples
        obj.points = [tuple(p) for p in data.get('points', [])]
        return obj
