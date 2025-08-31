from .map import Map, GridType
from .map_object import MapObject
from .group import Group

class MapManager:
    """Manages all game maps and the objects on them."""
    def __init__(self):
        self._maps = {}
        self.active_map_name = None

    def create_map(self, name, width, height, grid_type=GridType.SQUARE, background=None):
        """Creates a new map and adds it to the manager."""
        if name in self._maps:
            raise ValueError(f"A map with the name '{name}' already exists.")

        new_map = Map(
            name=name,
            width=width,
            height=height,
            grid_type=grid_type,
            background_asset_path=background
        )
        self._maps[name] = new_map
        self.set_active_map(name)
        print(f"Created new {grid_type.name.lower()} map '{name}' of size {width}x{height}.")
        if background:
            print(f"  with background: {background}")
        return new_map

    def set_active_map(self, name: str):
        """Sets the currently active map."""
        if name not in self._maps:
            raise ValueError(f"Map '{name}' not found.")
        self.active_map_name = name
        print(f"Active map set to '{name}'.")

    def get_active_map(self):
        """Returns the currently active map instance."""
        if not self.active_map_name:
            return None
        return self.get_map(self.active_map_name)

    def get_map(self, name):
        """Retrieves a map by its name."""
        return self._maps.get(name)

    def add_object_to_map(self, map_name: str, obj: MapObject):
        """Adds an object to the specified map."""
        game_map = self.get_map(map_name)
        if not game_map:
            raise ValueError(f"Map '{map_name}' not found.")
        game_map.add_object(obj)
        print(f"Added object {obj.id} to map '{map_name}'.")

    def remove_object_from_map(self, map_name: str, object_id: str):
        """Removes an object from the specified map."""
        game_map = self.get_map(map_name)
        if not game_map:
            raise ValueError(f"Map '{map_name}' not found.")
        game_map.remove_object(object_id)
        print(f"Removed object {object_id} from map '{map_name}'.")

    def get_objects_on_map(self, map_name: str):
        """Retrieves all objects on a given map."""
        game_map = self.get_map(map_name)
        if not game_map:
            raise ValueError(f"Map '{map_name}' not found.")
        return game_map.objects

    def move_object(self, map_name: str, object_id: str, new_x: int, new_y: int):
        """Moves an object on a specified map to new coordinates."""
        game_map = self.get_map(map_name)
        if not game_map:
            raise ValueError(f"Map '{map_name}' not found.")

        obj_to_move = game_map.get_object(object_id)
        if not obj_to_move:
            raise ValueError(f"Object '{object_id}' not found on map '{map_name}'.")

        # Calculate the change in position
        dx = new_x - obj_to_move.x
        dy = new_y - obj_to_move.y

        # If the object is a group, move all its members by the same delta
        if isinstance(obj_to_move, Group):
            print(f"Moving group {obj_to_move.id}. Propagating move to {len(obj_to_move.object_ids)} members.")
            for member_id in obj_to_move.object_ids:
                member_obj = game_map.get_object(member_id)
                if member_obj:
                    member_obj.x += dx
                    member_obj.y += dy
                    print(f"  - Moved member {member_id} to ({member_obj.x}, {member_obj.y}).")
                else:
                    print(f"  - Warning: Member object with ID '{member_id}' not found.")

        # Move the primary object (or the group object itself)
        obj_to_move.x = new_x
        obj_to_move.y = new_y
        print(f"Moved object {object_id} to ({new_x}, {new_y}) on map '{map_name}'.")

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
