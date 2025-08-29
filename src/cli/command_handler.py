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
        print("  action <id> <actor> <target>  - Executes a generic action by its ID.")
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

    def do_action(self, args):
        """Executes a generic action. Usage: action <action_id> <actor_name> <target_name>"""
        if len(args) != 3:
            print("Usage: action <action_id> <actor_name> <target_name>")
            return

        action_id, actor_name, target_name = args

        em = self.engine.get_entity_manager()
        actor = em.find_entity_by_name(actor_name)
        target = em.find_entity_by_name(target_name)

        if not actor:
            print(f"Error: Actor '{actor_name}' not found.")
            return
        if not target:
            print(f"Error: Target '{target_name}' not found.")
            return

        if not self.engine.get_action_manager().get_action(action_id):
            print(f"Error: Action '{action_id}' not found.")
            return

        print(f"\nExecuting action '{action_id}' from {actor_name} on {target_name}...")
        self.engine.execute_action(action_id, actor, target)

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
