import json

class PersistenceManager:
    """Handles saving and loading of the game state."""

    def __init__(self):
        pass

    def gather_game_state(self, engine):
        """
        Gathers the state from all engine components into a single dictionary.

        Args:
            engine (Engine): The main VTT engine instance.

        Returns:
            dict: A dictionary representing the complete game state.
        """
        game_state = {
            'entity_manager': engine.get_entity_manager().to_dict(),
            'initiative_tracker': engine.get_initiative_tracker().to_dict(),
            'map_manager': engine.get_map_manager().to_dict(),
            'active_module_id': engine.active_module.id if engine.active_module else None
        }
        return game_state

    def save_game(self, game_state, filepath):
        """Saves the given game state dictionary to a JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=4)
            print(f"Game state saved to {filepath}")
            return True
        except IOError as e:
            print(f"Error saving game to {filepath}: {e}")
            return False

    def load_game(self, filepath):
        """Loads a game state dictionary from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            print(f"Game state loaded from {filepath}")
            return game_state
        except FileNotFoundError:
            print(f"Error: Save file not found at {filepath}")
            return None
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading game from {filepath}: {e}")
            return None
