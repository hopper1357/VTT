from src.token import Token
from src.map_object import MapObject


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
        print("  map create <name> <w> <h> [type=hex] - Creates a new map (default is square).")
        print("  map list                      - Lists all created maps.")
        print("  map view <map_name>           - Shows a map with its objects and tokens.")
        print("  token place <entity> <map> <x> <y> [layer=4] - Places an entity's token on a map.")
        print("  object place <char> <map> <x> <y> <layer> - Places a generic object on a map.")
        print("  object move <id> <map> <x> <y> - Moves any object or token to new coordinates.")
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
            if len(args) < 4:
                print("Usage: map create <name> <width> <height> [type=square|hex]")
                return

            name = args[1]
            try:
                width = int(args[2])
                height = int(args[3])
            except ValueError:
                print("Error: Width and height must be integers.")
                return

            from src.map import GridType
            grid_type = GridType.SQUARE
            if len(args) > 4:
                type_arg = args[4]
                if type_arg.lower().startswith("type="):
                    type_val = type_arg.split('=', 1)[1].upper()
                    if type_val == 'HEX':
                        grid_type = GridType.HEX
                    elif type_val != 'SQUARE':
                        print(f"Warning: Unknown grid type '{type_val}'. Defaulting to SQUARE.")
                else:
                    print(f"Warning: Ignoring unrecognized argument '{type_arg}'.")

            try:
                map_manager.create_map(name, width, height, grid_type)
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

            # --- Start of New Layered Rendering Logic ---
            top_objects = {}  # (x, y) -> MapObject
            for obj in game_map.objects:
                pos = (obj.x, obj.y)
                if 0 <= obj.x < game_map.width and 0 <= obj.y < game_map.height:
                    if pos not in top_objects or obj.layer > top_objects[pos].layer:
                        top_objects[pos] = obj
            # --- End of New Layered Rendering Logic ---

            em = self.engine.get_entity_manager()
            from src.map import GridType

            if game_map.grid_type == GridType.SQUARE:
                print(f"\n--- Map: {game_map.name} (Square Grid {game_map.width}x{game_map.height}) ---")
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
                print(f"\n--- Map: {game_map.name} (Hex Grid {game_map.width}x{game_map.height}) ---")
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
            print("Available subcommands: place, move")
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
        else:
            print(f"Unknown object command: '{subcommand}'")
