import re
from .entity import EntityManager
from .dice import DiceRoller
from .module_loader import ModuleLoader
from .action_manager import ActionManager
from .initiative import InitiativeTracker
from .persistence import PersistenceManager

class Engine:
    """The main VTT engine."""

    def __init__(self, modules_directory="modules"):
        self.entity_manager = EntityManager()
        self.dice_roller = DiceRoller()
        self.action_manager = ActionManager()
        self.module_loader = ModuleLoader(self.action_manager, modules_directory)
        self.initiative_tracker = InitiativeTracker()
        self.persistence_manager = PersistenceManager()
        self.active_module = None

    def load_system_module(self, module_id):
        """Loads a system module and sets it as the active module."""
        self.active_module = self.module_loader.load_module(module_id)
        print(f"Active module set to: {self.active_module.name}")
        return self.active_module

    def get_entity_manager(self):
        return self.entity_manager

    def get_dice_roller(self):
        return self.dice_roller

    def get_module_loader(self):
        return self.module_loader

    def get_action_manager(self):
        return self.action_manager

    def get_initiative_tracker(self):
        return self.initiative_tracker

    def roll_for_initiative(self):
        """
        Rolls initiative for all combatants in the tracker.
        It uses the 'initiative' action.
        """
        tracker = self.get_initiative_tracker()
        em = self.get_entity_manager()

        for entity_id in list(tracker.combatants.keys()):
            entity = em.get_entity(entity_id)
            if not entity:
                print(f"Warning: Could not find entity {entity_id} for initiative roll.")
                continue

            # We use execute_action because it correctly resolves the formula
            # with the entity's attributes. The initiative action has no onSuccess.
            result = self.execute_action("initiative", actor=entity)
            initiative_score = result["roll_result"]["total"]

            tracker.set_initiative(entity_id, initiative_score)
            print(f"Rolled initiative for {entity.attributes.get('name', entity.id)}: {initiative_score}")

    def execute_action(self, action_id, actor, target=None):
        """
        Executes a registered action, including checking for success.

        Args:
            action_id (str): The ID of the action to execute.
            actor (Entity): The entity performing the action.
            target (Entity, optional): The target of the action.

        Returns:
            A dictionary containing the result of the action.
        """
        action = self.action_manager.get_action(action_id)
        if not action:
            raise ValueError(f"Action not found: {action_id}")

        # 1. Roll the primary formula (e.g., the attack roll)
        roll_result = self.dice_roller.roll(action.formula, actor, self.entity_manager)
        roll_total = roll_result['total']
        print(f"{actor.attributes.get('name', actor.id)} rolls a {roll_total} for {action.label} (formula: {action.formula}).")
        if roll_result.get("details"):
            for detail in roll_result["details"]:
                print(f"  > {detail}")

        # 2. Check for success condition if 'check' is defined
        is_success = True  # Default to success if no check is specified
        if action.check and target:
            check_data = action.check
            left_str = check_data.get('left')
            op = check_data.get('op')
            right_str = check_data.get('right')

            if not all([left_str, op, right_str]):
                print(f"Warning: Incomplete check data for action '{action.id}'. Defaulting to success.")
            else:
                # Resolve left value (e.g., "roll.total")
                left_val = roll_total if left_str == "roll.total" else 0

                # Resolve right value (e.g., "target.ac")
                right_val = 0
                if right_str.startswith("target."):
                    attr_name = right_str.split('.', 1)[1]
                    target_entity = self.entity_manager.get_entity(target.id)
                    if target_entity:
                        right_val = self.entity_manager.get_attribute(target_entity.id, attr_name) or 0

                print(f"Checking vs. Target AC: {left_val} {op} {right_val}")

                # Evaluate the operation
                op_map = {">=": (lambda a, b: a >= b), ">": (lambda a, b: a > b), "<=": (lambda a, b: a <= b), "<": (lambda a, b: a < b), "==": (lambda a, b: a == b)}
                if op in op_map:
                    try:
                        is_success = op_map[op](int(left_val), int(right_val))
                    except (ValueError, TypeError):
                        is_success = False
                else:
                    print(f"Warning: Unsupported operator '{op}'.")

        # 3. Execute onSuccess if the check passed
        if is_success:
            print(f"Result: Success! Executing onSuccess command...")
            self._execute_command_string(action.on_success, actor, target, roll_result)
        else:
            print(f"Result: Failure. {actor.attributes.get('name', actor.id)}'s action has no effect.")

        return {
            "action": action,
            "roll_result": roll_result,
            "success": is_success
        }

    def _execute_command_string(self, command_string, actor, target, roll_result):
        """Parses and executes a command string like 'damage(target, 1d8)'."""
        if not command_string:
            return

        match = re.match(r"(\w+)\((.*)\)", command_string)
        if not match:
            print(f"Warning: Could not parse command string: {command_string}")
            return

        command_name = match.group(1)
        args_string = match.group(2)
        args = [arg.strip() for arg in args_string.split(',')]

        if command_name == "damage":
            if len(args) != 2:
                print(f"Warning: 'damage' command expects 2 arguments, got {len(args)}")
                return

            target_arg = args[0]
            damage_formula = args[1]

            damage_target = None
            if target_arg == 'target' and target:
                damage_target = target
            elif target_arg == 'actor' and actor:
                damage_target = actor
            else:
                # Could be an entity ID in the future
                print(f"Warning: Could not resolve damage target '{target_arg}'")
                return

            # Roll for damage
            damage_result = self.dice_roller.roll(damage_formula, actor, self.entity_manager)
            damage_amount = damage_result['total']

            # Apply damage
            current_hp = self.entity_manager.get_attribute(damage_target.id, "hp") or 0
            new_hp = current_hp - damage_amount
            self.entity_manager.update_attribute(damage_target.id, "hp", new_hp)

            print(f"{actor.attributes.get('name', actor.id)} deals {damage_amount} damage to {damage_target.attributes.get('name', damage_target.id)}. New HP: {new_hp}")

    def get_persistence_manager(self):
        return self.persistence_manager

    def save_game(self, filepath):
        """Gathers the game state and saves it to a file."""
        game_state = self.persistence_manager.gather_game_state(self)
        return self.persistence_manager.save_game(game_state, filepath)

    def load_game(self, filepath):
        """Loads the game state from a file and restores the engine."""
        game_state = self.persistence_manager.load_game(filepath)
        if game_state is None:
            return False

        # Restore active module
        if game_state.get('active_module_id'):
            self.load_system_module(game_state['active_module_id'])

        # Restore entities
        if 'entity_manager' in game_state:
            self.entity_manager.load_from_dict(game_state['entity_manager'])

        # Restore initiative
        if 'initiative_tracker' in game_state:
            self.initiative_tracker.load_from_dict(game_state['initiative_tracker'])

        print("Game state successfully loaded and restored.")
        return True
