class InitiativeTracker:
    """Manages the turn order for combat."""

    def __init__(self):
        self._combatants = {}  # {entity_id: initiative_score}

    def add_combatant(self, entity_id, initiative=None):
        """Adds a combatant to the tracker."""
        if entity_id in self._combatants:
            print(f"Warning: Combatant {entity_id} is already in the tracker.")
            return
        self._combatants[entity_id] = initiative

    def set_initiative(self, entity_id, score):
        """Sets the initiative score for a combatant."""
        if entity_id not in self._combatants:
            raise ValueError(f"Combatant {entity_id} not found in tracker.")
        self._combatants[entity_id] = score

    def get_turn_order(self, descending=True):
        """
        Returns a list of entity IDs sorted by initiative score.
        Handles ties by not changing the original insertion order (stable sort).
        """
        # Filter out combatants with no initiative score yet
        with_initiative = {
            entity_id: score
            for entity_id, score in self._combatants.items()
            if score is not None
        }

        # Sort by initiative score
        sorted_combatants = sorted(
            with_initiative.items(),
            key=lambda item: item[1],
            reverse=descending
        )

        return [entity_id for entity_id, score in sorted_combatants]

    def clear(self):
        """Clears all combatants from the tracker."""
        self._combatants.clear()

    @property
    def combatants(self):
        """Returns the dictionary of combatants and their scores."""
        return self._combatants

    def to_dict(self):
        """Returns a serializable dictionary representation of the tracker's state."""
        return {
            'combatants': self.combatants
        }

    def load_from_dict(self, data):
        """Restores the tracker's state from a dictionary."""
        self.clear()
        combatants_data = data.get('combatants', {})
        self._combatants = combatants_data.copy()
