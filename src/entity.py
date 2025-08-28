import uuid

class Entity:
    """A generic entity in the VTT."""
    def __init__(self, entity_type, attributes=None):
        self.id = str(uuid.uuid4())
        self.entity_type = entity_type
        self.attributes = attributes if attributes is not None else {}

    def __repr__(self):
        return f"Entity(id={self.id}, type={self.entity_type}, attributes={self.attributes})"

class EntityManager:
    """Manages all entities in the game session."""
    def __init__(self):
        self._entities = {}

    def create_entity(self, entity_type, attributes=None):
        """Creates a new entity and adds it to the manager."""
        entity = Entity(entity_type, attributes)
        self._entities[entity.id] = entity
        return entity

    def get_entity(self, entity_id):
        """Retrieves an entity by its ID."""
        return self._entities.get(entity_id)

    def update_attribute(self, entity_id, attribute_name, attribute_value):
        """Updates an attribute for a given entity."""
        entity = self.get_entity(entity_id)
        if entity:
            entity.attributes[attribute_name] = attribute_value
            return True
        return False

    def get_attribute(self, entity_id, attribute_name):
        """Gets an attribute for a given entity."""
        entity = self.get_entity(entity_id)
        if entity:
            return entity.attributes.get(attribute_name)
        return None

    def list_entities(self, entity_type=None):
        """Lists all entities, optionally filtering by type."""
        if entity_type:
            return [e for e in self._entities.values() if e.entity_type == entity_type]
        return list(self._entities.values())
