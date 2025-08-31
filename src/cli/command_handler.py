from src.token import Token
from src.map_object import MapObject
from src.shape import Shape, ShapeType
from src.path import Path
from src.group import Group


class CommandHandler:
    """Handles the execution of CLI commands."""

    def __init__(self, engine):
        self.engine = engine
        # Using getattr is more extensible than a map for many commands.
        # The command 'create' will call the method 'do_create'.

    def handle_command(self, command, args):
        """
        Dispatches a command to the appropriate do_* method.
        Returns True if the command is to exit, False otherwise.
        """
        if command == 'exit':
            print("Exiting.")
            return True

        handler_method = getattr(self, f"do_{command}", None)
        if handler_method:
            handler_method(args)
        else:
            print(f"Unknown command: '{command}'. Type 'help' for a list of commands.")

        return False

    def do_help(self, args):
        """Displays a list of available commands."""
        print("\nWelcome to the Modular VTT CLI!")
        print("---------------------------------")
        print("Available Commands:")
        print("  help                          - Shows this help message.")
        print("  status                        - Shows the current game status (turn order, HP).")
        print("  create char <name> [hp=X]...  - Creates a new character entity.")
        print("  add <name>                    - Adds a character to the initiative tracker.")
        print("  init                          - Rolls initiative for all combatants.")
        print("  attack <target> with <actor>  - Executes an attack.")
        print("  map create <name> <w> <h> [type=hex] [bg=path] - Creates a new map.")
        print("  map list                      - Lists all created maps.")
        print("  map view <map_name>           - Shows a map with its objects and tokens.")
        print("  token place <entity> <map> <x> <y> [layer=4] - Places an entity's token on a map.")
        print("  object place <char> <map> <x> <y> <layer> - Places a generic object on a map.")
        print("  object move <id> <map> <x> <y> - Moves any object or token to new coordinates.")
        print("  object remove <id> <map>      - Removes an object or token from a map.")
        print("  shape place <type> <map> <x> <y> [opts] - Places a shape on a map (e.g. fill_color=#ff0000).")
        print("  draw path <map> <x,y>... [opts] - Draws a path with a series of points.")
        print("  group create <map> <id1> <id2>... - Groups multiple objects together.")
        print("  save <filepath>               - Saves the game state.")
        print("  load <filepath>               - Loads the game state.")
        print("  exit                          - Exits the application.")

    def do_status(self, args):
        """Displays the current game status."""
        print("\n--- Game Status ---")
        em = self.engine.get_entity_manager()
        tracker = self.engine.get_initiative_tracker()

        turn_order = tracker.get_turn_order()

        if not tracker.combatants:
            print("No combatants in the initiative tracker.")
            return

        print("Turn Order:")
        for i, entity_id in enumerate(turn_order):
            entity = em.get_entity(entity_id)
            score = tracker.combatants.get(entity_id)
            hp = entity.attributes.get('hp', 'N/A')
            print(f"  {i+1}. {entity.attributes.get('name', entity_id)} (HP: {hp}, Init: {score})")

        if len(turn_order) < len(tracker.combatants):
             print("\nCombatants not in turn order (roll initiative!):")
             in_order_ids = set(turn_order)
             for entity_id in tracker.combatants:
                 if entity_id not in in_order_ids:
                     entity = em.get_entity(entity_id)
                     hp = entity.attributes.get('hp', 'N/A')
                     print(f"  - {entity.attributes.get('name', entity_id)} (HP: {hp})")

    def do_create(self, args):
        """Creates a new entity. Usage: create char <name> [attr=value]..."""
        if len(args) < 2 or args[0].lower() != 'char':
            print("Usage: create char <name> [attr1=value1] [attr2=value2]...")
            return

        name = args[1]
        attributes = {"name": name}

        for arg in args[2:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                try:
                    # Try to convert to int, otherwise keep as string
                    attributes[key.lower()] = int(value)
                except ValueError:
                    attributes[key.lower()] = value
            else:
                print(f"Warning: Ignoring malformed attribute '{arg}'. Use key=value format.")

        em = self.engine.get_entity_manager()
        new_entity = em.create_entity("character", attributes)
        print(f"Created character '{name}' with ID {new_entity.id}.")

    def do_add(self, args):
        """Adds an entity to the initiative tracker. Usage: add <name>"""
        if len(args) != 1:
            print("Usage: add <name>")
            return

        name_to_add = args[0]
        em = self.engine.get_entity_manager()

        entity_to_add = em.find_entity_by_name(name_to_add)

        if not entity_to_add:
            print(f"Error: Entity '{name_to_add}' not found.")
            return

        tracker = self.engine.get_initiative_tracker()
        tracker.add_combatant(entity_to_add.id)
        print(f"Added '{name_to_add}' to the initiative tracker.")

    def do_init(self, args):
        """Rolls initiative for all combatants in the tracker."""
        print("\nRolling for initiative...")
        self.engine.roll_for_initiative()
        print("\nInitiative order set.")
        self.do_status(args) # Display the new turn order

    def do_attack(self, args):
        """Executes an attack. Usage: attack <target> with <actor>"""
        try:
            # This parsing is simple and rigid. A more complex parser
            # could be used for more flexible command structures.
            if len(args) != 3 or args[1].lower() != 'with':
                raise ValueError()
            target_name = args[0]
            actor_name = args[2]
        except (ValueError, IndexError):
            print("Usage: attack <target_name> with <actor_name>")
            return

        em = self.engine.get_entity_manager()
        actor = em.find_entity_by_name(actor_name)
        target = em.find_entity_by_name(target_name)

        if not actor:
            print(f"Error: Attacker '{actor_name}' not found.")
            return
        if not target:
            print(f"Error: Target '{target_name}' not found.")
            return

        # For now, we assume the default attack is 'sword_attack'
        print(f"\nExecuting attack from {actor_name} on {target_name}...")
        self.engine.execute_action("sword_attack", actor, target)

    def do_save(self, args):
        """Saves the game state. Usage: save <filepath>"""
        if len(args) != 1:
            print("Usage: save <filepath>")
            return
        filepath = args[0]
        if self.engine.save_game(filepath):
            print(f"Game saved successfully to {filepath}.")
        else:
            print(f"Failed to save game to {filepath}.")

    def do_load(self, args):
        """Loads the game state. Usage: load <filepath>"""
        if len(args) != 1:
            print("Usage: load <filepath>")
            return
        filepath = args[0]
        if self.engine.load_game(filepath):
            print(f"Game loaded successfully from {filepath}.")
        else:
            print(f"Failed to load game from {filepath}.")


    def do_map(self, args):
        """Handles map-related commands. Usage: map <subcommand> [...]"""
        if not args:
            print("Usage: map <subcommand> [args...]")
            print("Available subcommands: create, list, view")
            return

        subcommand = args[0].lower()
        map_manager = self.engine.get_map_manager()

        if subcommand == "create":
            if len(args) < 3:
                print("Usage: map create <name> <width> <height> [type=hex] [bg=path]")
                return

            # Core arguments
            name, width_str, height_str = args[1], args[2], args[3]

            # Parse optional arguments
            optional_args = args[4:]
            kwargs = {}
            for arg in optional_args:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    kwargs[key.lower()] = value

            try:
                width = int(width_str)
                height = int(height_str)
            except ValueError:
                print("Error: Width and height must be integers.")
                return

            from src.map import GridType
            grid_type = GridType.SQUARE
            if 'type' in kwargs:
                type_val = kwargs['type'].upper()
                if type_val == 'HEX':
                    grid_type = GridType.HEX
                elif type_val != 'SQUARE':
                    print(f"Warning: Unknown grid type '{kwargs['type']}'. Defaulting to SQUARE.")

            background = kwargs.get('bg')

            try:
                map_manager.create_map(name, width, height, grid_type, background)
            except ValueError as e:
                print(f"Error: {e}")

        elif subcommand == "list":
            maps = map_manager.list_maps()
            if not maps:
                print("No maps have been created yet.")
                return
            print("\nAvailable maps:")
            for map_name in maps:
                print(f"  - {map_name}")

        elif subcommand == "view":
            if len(args) != 2:
                print("Usage: map view <map_name>")
                return
            map_name = args[1]
            game_map = map_manager.get_map(map_name)
            if not game_map:
                print(f"Error: Map '{map_name}' not found.")
                return

            # --- Start of Layered Rendering Logic ---
            top_objects = {}
            for obj in game_map.objects:
                pos = (obj.x, obj.y)
                if 0 <= obj.x < game_map.width and 0 <= obj.y < game_map.height:
                    if pos not in top_objects or obj.layer > top_objects[pos].layer:
                        top_objects[pos] = obj
            # --- End of Layered Rendering Logic ---

            em = self.engine.get_entity_manager()
            from src.map import GridType

            title = f"--- Map: {game_map.name} ({game_map.grid_type.name.lower()} grid {game_map.width}x{game_map.height}) ---"
            if game_map.background_asset_path:
                title += f"\nBackground: {game_map.background_asset_path}"
            print(title)

            if game_map.grid_type == GridType.SQUARE:
                display_grid = [['.' for _ in range(game_map.width)] for _ in range(game_map.height)]
                for pos, obj in top_objects.items():
                    x, y = pos
                    display_grid[y][x] = obj.display_char

                header = "  " + " ".join([str(i) for i in range(game_map.width)])
                print(header)
                print("  " + "-" * (game_map.width * 2 - 1))
                for i, row in enumerate(display_grid):
                    print(f"{i}| {' '.join(row)}")

            elif game_map.grid_type == GridType.HEX:
                for r in range(game_map.height):
                    row_str = " " * (r % 2)
                    for c in range(game_map.width):
                        obj = top_objects.get((c, r))
                        if obj:
                            row_str += f"[{obj.display_char}]"
                        else:
                            row_str += "[.]"
                        row_str += " "
                    print(row_str)

            if game_map.objects:
                print("\nObjects on this map (sorted by layer):")
                for obj in sorted(game_map.objects, key=lambda o: o.layer):
                    if isinstance(obj, Token):
                        entity = em.get_entity(obj.entity_id)
                        name = entity.attributes.get('name', 'Unknown') if entity else 'Unknown'
                        print(f"  - Token: {name} ('{obj.display_char}') at ({obj.x}, {obj.y}), Layer: {obj.layer}, ID: {obj.id}")
                    else:
                        print(f"  - Object: '{obj.display_char}' at ({obj.x}, {obj.y}), Layer: {obj.layer}, ID: {obj.id}")
            print("--------------------")

        else:
            print(f"Unknown map command: '{subcommand}'")


    def do_token(self, args):
        """Handles token-related commands."""
        if not args or args[0].lower() != 'place':
            print("Usage: token place <entity_name> <map_name> <x> <y> [layer=4]")
            return

        if len(args) < 5:
            print("Usage: token place <entity_name> <map_name> <x> <y> [layer=4]")
            return

        entity_name, map_name, x_str, y_str = args[1], args[2], args[3], args[4]

        layer = 4 # Default token layer
        if len(args) > 5 and args[5].lower().startswith("layer="):
            try:
                layer = int(args[5].split('=')[1])
            except (ValueError, IndexError):
                print("Error: Invalid layer value. Must be an integer.")
                return

        em = self.engine.get_entity_manager()
        entity = em.find_entity_by_name(entity_name)
        if not entity:
            print(f"Error: Entity '{entity_name}' not found.")
            return

        map_manager = self.engine.get_map_manager()
        game_map = map_manager.get_map(map_name)
        if not game_map:
            print(f"Error: Map '{map_name}' not found.")
            return

        try:
            x, y = int(x_str), int(y_str)
        except ValueError:
            print("Error: X and Y coordinates must be integers.")
            return

        display_char = entity.attributes.get('name', '?')[0].upper()

        new_token = Token(entity_id=entity.id, x=x, y=y, layer=layer, display_char=display_char)

        try:
            map_manager.add_object_to_map(map_name, new_token)
            print(f"Placed token for '{entity_name}' on map '{map_name}' at ({x},{y}) on layer {layer}. ID: {new_token.id}")
        except ValueError as e:
            print(f"Error: {e}")

    def do_object(self, args):
        """Handles generic object commands."""
        if not args:
            print("Usage: object <subcommand> [...]")
            print("Available subcommands: place, move, remove")
            return

        subcommand = args[0].lower()
        map_manager = self.engine.get_map_manager()

        if subcommand == 'place':
            if len(args) != 6:
                print("Usage: object place <char> <map_name> <x> <y> <layer>")
                return

            char, map_name, x_str, y_str, layer_str = args[1], args[2], args[3], args[4], args[5]

            if len(char) != 1:
                print("Error: Display character must be a single character.")
                return

            game_map = map_manager.get_map(map_name)
            if not game_map:
                print(f"Error: Map '{map_name}' not found.")
                return

            try:
                x, y, layer = int(x_str), int(y_str), int(layer_str)
            except ValueError:
                print("Error: X, Y, and Layer must be integers.")
                return

            new_obj = MapObject(x=x, y=y, layer=layer, display_char=char)
            map_manager.add_object_to_map(map_name, new_obj)
            print(f"Placed object '{char}' on map '{map_name}' at ({x},{y}) on layer {layer}. ID: {new_obj.id}")

        elif subcommand == 'move':
            if len(args) != 5:
                print("Usage: object move <object_id> <map_name> <x> <y>")
                return

            object_id, map_name, x_str, y_str = args[1], args[2], args[3], args[4]

            try:
                x, y = int(x_str), int(y_str)
            except ValueError:
                print("Error: X and Y coordinates must be integers.")
                return

            try:
                map_manager.move_object(map_name, object_id, x, y)
            except ValueError as e:
                print(f"Error: {e}")

        elif subcommand == 'remove':
            if len(args) != 3:
                print("Usage: object remove <object_id> <map_name>")
                return

            object_id, map_name = args[1], args[2]

            try:
                map_manager.remove_object_from_map(map_name, object_id)
            except ValueError as e:
                print(f"Error: {e}")
        else:
            print(f"Unknown object command: '{subcommand}'")

    def _parse_drawable_kwargs(self, args):
        """Helper to parse common optional arguments for drawable objects."""
        kwargs = {}
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                key = key.lower()
                # Basic type conversion
                if key in ['opacity']:
                    try:
                        kwargs[key] = float(value)
                    except ValueError:
                        print(f"Warning: Invalid float value for {key}. Ignoring.")
                elif key in ['stroke_width', 'layer', 'size']:
                    try:
                        kwargs[key] = int(value)
                    except ValueError:
                        print(f"Warning: Invalid integer value for {key}. Ignoring.")
                else:
                    kwargs[key] = value
        return kwargs

    def do_shape(self, args):
        """Handles shape commands. Usage: shape place <type> <map> <x> <y> [opts]"""
        if not args or args[0].lower() != 'place':
            print("Usage: shape place <type> <map_name> <x> <y> [key=value...]")
            print("Types: circle, square, triangle, hexagon")
            print("Options: layer=N, size=N, stroke_color=#hex, stroke_width=N, opacity=0.N, fill_color=#hex")
            return

        if len(args) < 5:
            print("Usage: shape place <type> <map_name> <x> <y> [key=value...]")
            return

        shape_type_str, map_name, x_str, y_str = args[1], args[2], args[3], args[4]
        optional_args = self._parse_drawable_kwargs(args[5:])

        map_manager = self.engine.get_map_manager()
        game_map = map_manager.get_map(map_name)
        if not game_map:
            print(f"Error: Map '{map_name}' not found.")
            return

        try:
            shape_type = ShapeType[shape_type_str.upper()]
        except KeyError:
            print(f"Error: Invalid shape type '{shape_type_str}'. Valid types are: circle, square, triangle, hexagon.")
            return

        try:
            x, y = int(x_str), int(y_str)
        except ValueError:
            print("Error: X and Y coordinates must be integers.")
            return

        # Set default display char based on shape
        if 'display_char' not in optional_args:
            optional_args['display_char'] = 'S'

        if 'layer' not in optional_args:
            optional_args['layer'] = 1 # Default layer

        new_shape = Shape(x=x, y=y, shape_type=shape_type, **optional_args)
        map_manager.add_object_to_map(map_name, new_shape)
        print(f"Placed {shape_type.name.lower()} shape on map '{map_name}' at ({x},{y}). ID: {new_shape.id}")

    def do_draw(self, args):
        """Handles drawing commands. Usage: draw path <map> <x1,y1> <x2,y2>... [opts]"""
        if not args or args[0].lower() != 'path':
            print("Usage: draw path <map_name> <x1,y1> <x2,y2>... [key=value...]")
            print("Options: layer=N, stroke_color=#hex, stroke_width=N, opacity=0.N")
            return

        if len(args) < 3:
            print("Usage: draw path <map_name> <x1,y1> <x2,y2>...")
            return

        map_name = args[1]

        # Find where points end and optional args begin
        first_opt_idx = -1
        for i, arg in enumerate(args[2:]):
            if '=' in arg:
                first_opt_idx = i + 2
                break

        point_args = args[2:first_opt_idx] if first_opt_idx != -1 else args[2:]
        optional_args_list = args[first_opt_idx:] if first_opt_idx != -1 else []
        optional_args = self._parse_drawable_kwargs(optional_args_list)

        if not point_args:
            print("Error: At least one point (e.g., 10,20) is required for a path.")
            return

        points = []
        try:
            for p_arg in point_args:
                px, py = p_arg.split(',')
                points.append((int(px), int(py)))
        except ValueError:
            print("Error: Points must be in 'x,y' format without spaces (e.g., 10,20).")
            return

        map_manager = self.engine.get_map_manager()
        game_map = map_manager.get_map(map_name)
        if not game_map:
            print(f"Error: Map '{map_name}' not found.")
            return

        # Use the first point as the anchor x,y for the object
        anchor_x, anchor_y = points[0]

        # Set default display char
        if 'display_char' not in optional_args:
            optional_args['display_char'] = 'L'

        if 'layer' not in optional_args:
            optional_args['layer'] = 1 # Default layer

        new_path = Path(x=anchor_x, y=anchor_y, points=points, **optional_args)
        map_manager.add_object_to_map(map_name, new_path)
        print(f"Placed path with {len(points)} points on map '{map_name}'. ID: {new_path.id}")

    def do_group(self, args):
        """Handles group commands. Usage: group create <map> <id1> <id2>..."""
        if not args or args[0].lower() != 'create':
            print("Usage: group create <map_name> <object_id1> <object_id2>...")
            return

        if len(args) < 3:
            print("Usage: group create <map_name> <object_id1> <object_id2>...")
            return

        map_name = args[1]
        object_ids = args[2:]

        map_manager = self.engine.get_map_manager()
        game_map = map_manager.get_map(map_name)
        if not game_map:
            print(f"Error: Map '{map_name}' not found.")
            return

        # Validate that all objects exist on the map
        total_x, total_y = 0, 0
        valid_ids = []
        for obj_id in object_ids:
            obj = game_map.get_object(obj_id)
            if not obj:
                print(f"Warning: Object with ID '{obj_id}' not found on map. Skipping.")
                continue
            valid_ids.append(obj_id)
            total_x += obj.x
            total_y += obj.y

        if not valid_ids:
            print("Error: No valid objects found to group.")
            return

        # Place the group's anchor at the average position of its members
        anchor_x = total_x // len(valid_ids)
        anchor_y = total_y // len(valid_ids)

        new_group = Group(x=anchor_x, y=anchor_y, layer=0, display_char='G', object_ids=valid_ids)
        map_manager.add_object_to_map(map_name, new_group)
        print(f"Created group with {len(valid_ids)} members on map '{map_name}'. ID: {new_group.id}")
