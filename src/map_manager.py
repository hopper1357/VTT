from .map import Map

class MapManager:
    """Manages all game maps."""
    def __init__(self):
        self._maps = {}

    def create_map(self, name, width, height):
        """Creates a new map and adds it to the manager."""
        if name in self._maps:
            raise ValueError(f"A map with the name '{name}' already exists.")

        new_map = Map(name=name, width=width, height=height)
        self._maps[name] = new_map
        print(f"Created new map '{name}' of size {width}x{height}.")
        return new_map

    def get_map(self, name):
        """Retrieves a map by its name."""
        return self._maps.get(name)
