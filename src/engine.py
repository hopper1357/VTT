import re
from .entity import EntityManager
from .dice import DiceRoller
from .module_loader import ModuleLoader
from .action_manager import ActionManager

class Engine:
    """The main VTT engine."""

    def __init__(self, modules_directory="modules"):
        self.entity_manager = EntityManager()
        self.dice_roller = DiceRoller()
        self.action_manager = ActionManager()
        self.module_loader = ModuleLoader(self.action_manager, modules_directory)
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

    def execute_action(self, action_id, actor, target=None):
        """
        Executes a registered action.

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

        # 2. Execute the onSuccess command string
        # For now, we assume a simple success/failure based on the roll,
        # but the design doc doesn't specify this logic yet (e.g. vs AC).
        # We will assume for now that the onSuccess command is always executed.
        self._execute_command_string(action.on_success, actor, target, roll_result)

        return {
            "action": action,
            "roll_result": roll_result
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
