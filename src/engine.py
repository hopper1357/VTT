from .entity import EntityManager
from .dice import DiceRoller
from .module_loader import ModuleLoader

class Engine:
    """The main VTT engine."""

    def __init__(self, modules_directory="modules"):
        self.entity_manager = EntityManager()
        self.dice_roller = DiceRoller()
        self.module_loader = ModuleLoader(modules_directory)
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
