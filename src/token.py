import uuid
from dataclasses import dataclass, field

@dataclass
class Token:
    """Represents an object on a map, linked to an entity."""
    entity_id: str
    x: int
    y: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
