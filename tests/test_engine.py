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

    def test_action_registration_on_module_load(self):
        print("Running test: test_action_registration_on_module_load")
        self.engine.load_system_module("dnd5e")

        action_manager = self.engine.get_action_manager()
        sword_attack_action = action_manager.get_action("sword_attack")

        self.assertIsNotNone(sword_attack_action)
        self.assertEqual(sword_attack_action.label, "Sword Attack")
        self.assertEqual(sword_attack_action.formula, "1d20 + @strength_mod + @proficiency")

    @patch('random.randint')
    def test_execute_action_damage(self, mock_randint):
        print("Running test: test_execute_action_damage")
        # Mock dice rolls: 15 for attack (1d20), 4 for damage (1d8)
        mock_randint.side_effect = [15, 4]

        self.engine.load_system_module("dnd5e")
        em = self.engine.get_entity_manager()

        actor = em.create_entity("character", {"name": "Fighter", "str": 16}) # +3 mod
        target = em.create_entity("npc", {"name": "Goblin", "hp": 10})

        self.engine.execute_action("sword_attack", actor, target)

        # Expected damage = 4 (1d8) + 3 (str_mod) = 7
        # Expected HP = 10 - 7 = 3
        self.assertEqual(em.get_attribute(target.id, "hp"), 3)

if __name__ == '__main__':
    unittest.main()
