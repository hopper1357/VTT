from dataclasses import dataclass
from typing import Optional

@dataclass
class Action:
    """Represents a single, registered action from a module."""
    id: str
    label: str
    formula: str
    on_success: str = "" # e.g., "damage(target, result.total)"
    check: Optional[dict] = None

class ActionManager:
    """Manages all actions available in the game session."""
    def __init__(self):
        self._actions = {}

    def register_action(self, action_data):
        """
        Registers a new action from a dictionary of data.

        Args:
            action_data (dict): A dictionary with action details,
                                e.g., {"id": "...", "label": "...", ...}
        """
        if 'id' not in action_data:
            raise ValueError("Action data must include an 'id'")

        action = Action(
            id=action_data['id'],
            label=action_data.get('label', ''),
            formula=action_data.get('formula', ''),
            on_success=action_data.get('onSuccess', ''), # JS uses camelCase, Python uses snake_case
            check=action_data.get('check')
        )

        if action.id in self._actions:
            print(f"Warning: Overwriting action with duplicate ID: {action.id}")

        self._actions[action.id] = action
        return action

    def get_action(self, action_id):
        """Retrieves a registered action by its ID."""
        return self._actions.get(action_id)
