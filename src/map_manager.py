from .map import Map, GridType
from .token import Token


class MapManager:
    """Manages all game maps and the tokens on them."""
    def __init__(self):
        self._maps = {}

    def create_map(self, name, width, height, grid_type=GridType.SQUARE):
        """Creates a new map and adds it to the manager."""
        if name in self._maps:
            raise ValueError(f"A map with the name '{name}' already exists.")

        new_map = Map(name=name, width=width, height=height, grid_type=grid_type)
        self._maps[name] = new_map
        print(f"Created new {grid_type.name.lower()} map '{name}' of size {width}x{height}.")
        return new_map

    def get_map(self, name):
        """Retrieves a map by its name."""
        return self._maps.get(name)

    def add_token_to_map(self, map_name: str, token: Token):
        """Adds a token to the specified map."""
        game_map = self.get_map(map_name)
        if not game_map:
            raise ValueError(f"Map '{map_name}' not found.")
        game_map.add_token(token)
        print(f"Added token {token.id} to map '{map_name}'.")

    def remove_token_from_map(self, map_name: str, token_id: str):
        """Removes a token from the specified map."""
        game_map = self.get_map(map_name)
        if not game_map:
            raise ValueError(f"Map '{map_name}' not found.")
        game_map.remove_token(token_id)
        print(f"Removed token {token_id} from map '{map_name}'.")

    def get_tokens_on_map(self, map_name: str):
        """Retrieves all tokens on a given map."""
        game_map = self.get_map(map_name)
        if not game_map:
            raise ValueError(f"Map '{map_name}' not found.")
        return game_map.tokens

    def move_token(self, map_name: str, token_id: str, new_x: int, new_y: int):
        """Moves a token on a specified map to new coordinates."""
        game_map = self.get_map(map_name)
        if not game_map:
            raise ValueError(f"Map '{map_name}' not found.")

        token_to_move = game_map.get_token(token_id)
        if not token_to_move:
            raise ValueError(f"Token '{token_id}' not found on map '{map_name}'.")

        token_to_move.x = new_x
        token_to_move.y = new_y
        print(f"Moved token {token_id} to ({new_x}, {new_y}) on map '{map_name}'.")

    def to_dict(self):
        """Returns a serializable dictionary representation of the map manager."""
        return {
            'maps': {name: map_obj.to_dict() for name, map_obj in self._maps.items()}
        }

    def from_dict(self, data):
        """Restores the map manager's state from a dictionary."""
        self._maps.clear()
        maps_data = data.get('maps', {})
        for name, map_data in maps_data.items():
            self._maps[name] = Map.from_dict(map_data)

    def list_maps(self):
        """Returns a list of all map names."""
        return list(self._maps.keys())
