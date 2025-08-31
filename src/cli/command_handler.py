from src.token import Token
from src.map_object import MapObject
import src.fov as fov


from .parser import CommandParser
from functools import wraps
from src.user import UserRole

def gm_only(func):
    """Decorator to restrict a command to the Game Master."""
    @wraps(func)
    def wrapper(self, args):
        if self.engine.current_user.role != UserRole.GM:
            print("Error: This command can only be used by the Game Master.")
            return
        return func(self, args)
    return wrapper

class CommandHandler:
    """Handles the execution of CLI commands."""

    def __init__(self, engine):
        self.engine = engine
        self.parser = CommandParser()

    def parse_and_handle(self, input_string):
        """Parses a string and handles the resulting command."""
        command, args = self.parser.parse(input_string)
        if command:
            return self.handle_command(command, args)
        return False

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
        print("  map view <map> [from=<id>]    - Shows a map. Optionally, view from an object's perspective (FOV).")
        print("  token place <ent> <map> <x> <y> [layer=4] [light=R] [blocks=T/F] - Places an entity's token.")
        print("  object place <char> <map> <x> <y> <layer> [light=R] [blocks=T/F] - Places a generic object.")
        print("  object move <id> <map> <x> <y> - Moves any object or token to new coordinates.")
        print("  object remove <id> <map>      - Removes an object or token from a map.")
        print("  save <filepath>               - Saves the game state.")
        print("  load <filepath>               - Loads the game state.")
        print("  players                       - Lists connected players.")
        print("  assign <token> to <player>    - (GM only) Assigns a token to a player.")
        print("  exit                          - Exits the application.")

    def do_players(self, args):
        """Lists the currently connected players."""
        user_manager = self.engine.get_user_manager()
        users = user_manager.list_users()
        print("\n--- Connected Players ---")
        if not users:
            print("No one is connected.")
            return

        for user in users:
            role = f"({user.role.name})"
            print(f"  - {user.username} {role}")
        print("-------------------------")

    @gm_only
    def do_assign(self, args):
        """Assigns a token to a player. Usage: assign <token_name> to <player_name>"""
        if len(args) != 3 or args[1].lower() != 'to':
            print("Usage: assign <token_name> to <player_name>")
            return

        token_name, player_name = args[0], args[2]

        em = self.engine.get_entity_manager()
        entity = em.find_entity_by_name(token_name)
        if not entity:
            print(f"Error: Entity '{token_name}' not found.")
            return

        user_manager = self.engine.get_user_manager()
        player = user_manager.find_user_by_name(player_name)
        if not player:
            print(f"Error: Player '{player_name}' not found.")
            return

        # Find the token on any map
        map_manager = self.engine.get_map_manager()
        token_found = False
        for map_name in map_manager.list_maps():
            game_map = map_manager.get_map(map_name)
            for obj in game_map.objects:
                if isinstance(obj, Token) and obj.entity_id == entity.id:
                    obj.owner_id = player.id
                    token_found = True
                    print(f"Assigned token '{token_name}' to player '{player_name}'.")
                    break
            if token_found:
                break

        if not token_found:
            print(f"Error: Token for entity '{token_name}' not found on any map.")

    # ... (status, create, add, init, attack, save, load methods are unchanged) ...
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

    @gm_only
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

    def _parse_kwargs(self, args_list):
        kwargs = {}
        for arg in args_list:
            if '=' in arg:
                key, value = arg.split('=', 1)
                kwargs[key.lower()] = value
        return kwargs

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
                print("Usage: map create <name> <width> <height> [type=hex] [bg=path]")
                return

            name, width_str, height_str = args[1], args[2], args[3]
            kwargs = self._parse_kwargs(args[4:])

            try:
                width, height = int(width_str), int(height_str)
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
            map_manager.create_map(name, width, height, grid_type, background)

        elif subcommand == "list":
            maps = map_manager.list_maps()
            if not maps:
                print("No maps have been created yet.")
                return
            print("\nAvailable maps:")
            for map_name in maps:
                print(f"  - {map_name}")

        elif subcommand == "view":
            if len(args) < 2:
                print("Usage: map view <map_name> [from=<id>]")
                return

            map_name = args[1]
            kwargs = self._parse_kwargs(args[2:])
            viewer_id = kwargs.get('from')

            game_map = map_manager.get_map(map_name)
            if not game_map:
                print(f"Error: Map '{map_name}' not found.")
                return

            visible_tiles = None
            if viewer_id:
                viewer = game_map.get_object(viewer_id)
                if not viewer:
                    print(f"Error: Viewer object with ID '{viewer_id}' not found on map.")
                    return
                if viewer.light_radius is None:
                    print(f"Warning: Object '{viewer_id}' has no light source (light_radius is not set).")
                    visible_tiles = set()
                else:
                    visible_tiles = fov.calculate_fov(game_map, viewer.x, viewer.y, viewer.light_radius)

            top_objects = {}
            for obj in game_map.objects:
                pos = (obj.x, obj.y)
                if 0 <= obj.x < game_map.width and 0 <= obj.y < game_map.height:
                    if pos not in top_objects or obj.layer > top_objects[pos].layer:
                        top_objects[pos] = obj

            em = self.engine.get_entity_manager()
            from src.map import GridType

            title = f"--- Map: {game_map.name} ({game_map.grid_type.name.lower()} grid {game_map.width}x{game_map.height}) ---"
            if game_map.background_asset_path:
                title += f"\nBackground: {game_map.background_asset_path}"
            print(title)

            if game_map.grid_type == GridType.SQUARE:
                header = "  " + " ".join([str(i) for i in range(game_map.width)])
                print(header)
                print("  " + "-" * (game_map.width * 2 - 1))
                for y in range(game_map.height):
                    row_str = f"{y}| "
                    for x in range(game_map.width):
                        if visible_tiles is not None and (x, y) not in visible_tiles:
                            row_str += "  "
                            continue
                        obj = top_objects.get((x, y))
                        row_str += (obj.display_char if obj else ".") + " "
                    print(row_str.rstrip())

            elif game_map.grid_type == GridType.HEX:
                for r in range(game_map.height):
                    row_str = " " * (r % 2)
                    for c in range(game_map.width):
                        if visible_tiles is not None and (c, r) not in visible_tiles:
                            row_str += "   "
                            continue
                        obj = top_objects.get((c, r))
                        row_str += f"[{obj.display_char if obj else '.'}]"
                    print(row_str)

            if game_map.objects:
                print("\nObjects on this map (sorted by layer):")
                for obj in sorted(game_map.objects, key=lambda o: o.layer):
                    info = f"at ({obj.x}, {obj.y}), Layer: {obj.layer}"
                    if obj.light_radius is not None:
                        info += f", Light: {obj.light_radius}"
                    if obj.blocks_light:
                        info += ", Blocks Light"
                    info += f", ID: {obj.id}"

                    if isinstance(obj, Token):
                        entity = em.get_entity(obj.entity_id)
                        name = entity.attributes.get('name', 'Unknown') if entity else 'Unknown'
                        print(f"  - Token: {name} ('{obj.display_char}') {info}")
                    else:
                        print(f"  - Object: '{obj.display_char}' {info}")
            print("--------------------")

        else:
            print(f"Unknown map command: '{subcommand}'")

    def _create_map_object_from_args(self, args, required_arg_count):
        """Helper to parse common arguments for object and token placement."""
        # ... (implementation to be added)
        pass

    @gm_only
    def do_token(self, args):
        """Handles token-related commands."""
        if not args or args[0].lower() != 'place':
            print("Usage: token place <entity> <map> <x> <y> [owner=username|ALL_PLAYERS] [layer=4] ...")
            return

        if len(args) < 5:
            print("Usage: token place <entity> <map> <x> <y> [owner=username|ALL_PLAYERS] [layer=4] ...")
            return

        entity_name, map_name, x_str, y_str = args[1], args[2], args[3], args[4]
        kwargs = self._parse_kwargs(args[5:])

        em = self.engine.get_entity_manager()
        entity = em.find_entity_by_name(entity_name)
        if not entity:
            print(f"Error: Entity '{entity_name}' not found.")
            return

        map_manager = self.engine.get_map_manager()
        if not map_manager.get_map(map_name):
            print(f"Error: Map '{map_name}' not found.")
            return

        owner_id = None
        if 'owner' in kwargs:
            owner_name = kwargs['owner']
            if owner_name.lower() == 'all_players':
                owner_id = 'ALL_PLAYERS'
            else:
                user_manager = self.engine.get_user_manager()
                owner = user_manager.find_user_by_name(owner_name)
                if not owner:
                    print(f"Error: Owner user '{owner_name}' not found.")
                    return
                owner_id = owner.id

        try:
            x, y = int(x_str), int(y_str)
            layer = int(kwargs.get('layer', 4))
            light_radius = int(kwargs['light']) if 'light' in kwargs else None
            blocks_light = kwargs.get('blocks', 'false').lower() in ['true', 't', '1', 'yes']
        except ValueError:
            print("Error: x, y, layer, and light radius must be integers.")
            return

        display_char = entity.attributes.get('name', '?')[0].upper()

        new_token = Token(
            entity_id=entity.id, x=x, y=y, layer=layer, display_char=display_char,
            light_radius=light_radius, blocks_light=blocks_light, owner_id=owner_id
        )

        map_manager.add_object_to_map(map_name, new_token)
        print(f"Placed token for '{entity_name}' on map '{map_name}' at ({x},{y}). ID: {new_token.id}")

    def do_object(self, args):
        """Handles generic object commands."""
        if not args:
            print("Usage: object <subcommand> [...]")
            print("Available subcommands: place, move, remove")
            return

        subcommand = args[0].lower()
        map_manager = self.engine.get_map_manager()

        if subcommand == 'place':
            if len(args) < 6:
                print("Usage: object place <char> <map> <x> <y> <layer> [light=R] [blocks=T/F]")
                return

            char, map_name, x_str, y_str, layer_str = args[1], args[2], args[3], args[4], args[5]
            kwargs = self._parse_kwargs(args[6:])

            if len(char) != 1:
                print("Error: Display character must be a single character.")
                return

            if not map_manager.get_map(map_name):
                print(f"Error: Map '{map_name}' not found.")
                return

            try:
                x, y, layer = int(x_str), int(y_str), int(layer_str)
                light_radius = int(kwargs['light']) if 'light' in kwargs else None
                blocks_light = kwargs.get('blocks', 'false').lower() in ['true', 't', '1', 'yes']
            except ValueError:
                print("Error: x, y, layer, and light radius must be integers.")
                return

            new_obj = MapObject(
                x=x, y=y, layer=layer, display_char=char,
                light_radius=light_radius, blocks_light=blocks_light
            )
            map_manager.add_object_to_map(map_name, new_obj)
            print(f"Placed object '{char}' on map '{map_name}' at ({x},{y}). ID: {new_obj.id}")

        elif subcommand == 'move':
            if len(args) != 5:
                print("Usage: object move <object_id> <map_name> <x> <y>")
                return

            object_id, map_name, x_str, y_str = args[1], args[2], args[3], args[4]

            game_map = map_manager.get_map(map_name)
            if not game_map:
                print(f"Error: Map '{map_name}' not found.")
                return

            obj_to_move = game_map.get_object(object_id)
            if not obj_to_move:
                print(f"Error: Object with ID '{object_id}' not found on map '{map_name}'.")
                return

            # Permission Check
            current_user = self.engine.current_user
            can_move = False
            if current_user.role == UserRole.GM:
                can_move = True
            elif isinstance(obj_to_move, Token):
                if obj_to_move.owner_id == 'ALL_PLAYERS' or obj_to_move.owner_id == current_user.id:
                    can_move = True

            if not can_move:
                print("Error: You do not have permission to move this object.")
                return

            try:
                x, y = int(x_str), int(y_str)
            except ValueError:
                print("Error: X and Y coordinates must be integers.")
                return

            map_manager.move_object(map_name, object_id, x, y)

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
