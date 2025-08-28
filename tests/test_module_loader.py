import unittest
import os
from src.module_loader import ModuleLoader

class TestModuleLoader(unittest.TestCase):

    def setUp(self):
        # We know the dnd5e module exists from the previous step
        self.loader = ModuleLoader(modules_directory="modules")

    def test_load_module_success(self):
        print("Running test: test_load_module_success")
        module = self.loader.load_module("dnd5e")

        # Check manifest data
        self.assertIsNotNone(module)
        self.assertEqual(module.id, "dnd5e")
        self.assertEqual(module.name, "Dungeons & Dragons 5e")

        # Check that it's stored in the loader
        self.assertIn("dnd5e", self.loader.loaded_modules)

        # Check rules data
        self.assertIn("dice", module.rules)
        self.assertEqual(module.rules["dice"]["attack_roll"], "1d20 + @strength_mod + @proficiency")

        # Check sheets data
        self.assertIn("character", module.sheets)
        self.assertEqual(module.sheets["character"]["tabs"][0]["name"], "Attributes")

    def test_load_nonexistent_module(self):
        print("Running test: test_load_nonexistent_module")
        with self.assertRaises(FileNotFoundError):
            self.loader.load_module("nonexistent")

    def test_get_module(self):
        print("Running test: test_get_module")
        self.loader.load_module("dnd5e")

        retrieved_module = self.loader.get_module("dnd5e")
        self.assertIsNotNone(retrieved_module)
        self.assertEqual(retrieved_module.id, "dnd5e")

if __name__ == '__main__':
    # We need to run tests from the root directory for paths to work
    # This can be run with `python3 -m unittest tests/test_module_loader.py`
    unittest.main()
