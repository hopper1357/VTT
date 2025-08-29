import uuid

class Entity:
    """A generic entity in the VTT."""
    def __init__(self, entity_type, attributes=None):
        self.id = str(uuid.uuid4())
        self.entity_type = entity_type
        self.attributes = attributes if attributes is not None else {}

    def __repr__(self):
        return f"Entity(id={self.id}, type={self.entity_type}, attributes={self.attributes})"

    def to_dict(self):
        """Returns a serializable dictionary representation of the entity."""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'attributes': self.attributes
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an entity from a dictionary, preserving its ID."""
        entity = cls(data['entity_type'], data.get('attributes'))
        entity.id = data['id'] # Important: restore the original ID
        return entity

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

    def get_ability_modifier(self, score):
        """Calculates the D&D 5e ability modifier for a given score."""
        return (score - 10) // 2

    def resolve_variable(self, variable_name, entity):
        """Resolves a variable string like 'strength_mod' for a given entity."""
        if not entity:
            return 0

        # Simple attribute lookup
        if variable_name in entity.attributes:
            return entity.attributes.get(variable_name)

        # Handle D&D 5e style modifiers
        if variable_name.endswith("_mod"):
            base_attribute_name = variable_name[:-4]  # remove "_mod"
            # D&D uses 3-letter abbreviations for attributes
            dnd_attr_map = {
                "strength": "str", "dexterity": "dex", "constitution": "con",
                "intelligence": "int", "wisdom": "wis", "charisma": "cha"
            }
            attr_key = dnd_attr_map.get(base_attribute_name, base_attribute_name)

            if attr_key in entity.attributes:
                score = entity.attributes[attr_key]
                return self.get_ability_modifier(score)

        return 0  # Variable not found

    def to_dict(self):
        """Returns a serializable dictionary representation of the manager's state."""
        return {
            'entities': [entity.to_dict() for entity in self._entities.values()]
        }

    def load_from_dict(self, data):
        """Restores the manager's state from a dictionary."""
        self.clear_entities()
        for entity_data in data.get('entities', []):
            entity = Entity.from_dict(entity_data)
            self._entities[entity.id] = entity

    def clear_entities(self):
        """Clears all entities from the manager."""
        self._entities.clear()

    def find_entity_by_name(self, name):
        """Finds the first entity with a matching 'name' attribute."""
        for entity in self._entities.values():
            if entity.attributes.get('name') == name:
                return entity
        return None
