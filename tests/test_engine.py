import unittest
from unittest.mock import patch
from src.engine import Engine

class TestEngine(unittest.TestCase):

    def setUp(self):
        self.engine = Engine(modules_directory="modules")

    def test_engine_initialization(self):
        print("Running test: test_engine_initialization")
        self.assertIsNotNone(self.engine.get_entity_manager())
        self.assertIsNotNone(self.engine.get_dice_roller())
        self.assertIsNotNone(self.engine.get_module_loader())

    def test_load_system_module(self):
        print("Running test: test_load_system_module")
        module = self.engine.load_system_module("dnd5e")
        self.assertIsNotNone(module)
        self.assertEqual(module.id, "dnd5e")
        self.assertEqual(self.engine.active_module, module)

    @patch('random.randint')
    def test_roll_with_attributes(self, mock_randint):
        print("Running test: test_roll_with_attributes")
        # Mock the d20 roll to always be 10
        mock_randint.return_value = 10

        em = self.engine.get_entity_manager()

        # Create a character with attributes
        character = em.create_entity("character", {
            "str": 14,         # modifier = +2
            "proficiency": 3
        })

        expression = "1d20 + @strength_mod + @proficiency"
        result = self.engine.get_dice_roller().roll(expression, character, em)

        # Expected total: 10 (d20 roll) + 2 (str_mod) + 3 (proficiency) = 15
        self.assertEqual(result["total"], 15)
        self.assertEqual(result["rolls"], [10])
        self.assertEqual(result["modifier"], 5) # 2 (str_mod) + 3 (proficiency)

if __name__ == '__main__':
    unittest.main()
