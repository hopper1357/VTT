import unittest
from src.action_manager import ActionManager, Action

class TestActionManager(unittest.TestCase):

    def setUp(self):
        self.manager = ActionManager()
        self.sample_action_data = {
            "id": "sword_attack",
            "label": "Sword Attack",
            "formula": "1d20 + @strength_mod",
            "onSuccess": "damage(target, 1d8 + @strength_mod)"
        }

    def test_register_action(self):
        print("Running test: test_register_action")
        action = self.manager.register_action(self.sample_action_data)

        self.assertIsInstance(action, Action)
        self.assertEqual(action.id, "sword_attack")
        self.assertEqual(action.on_success, "damage(target, 1d8 + @strength_mod)")

    def test_get_action(self):
        print("Running test: test_get_action")
        self.manager.register_action(self.sample_action_data)

        retrieved_action = self.manager.get_action("sword_attack")
        self.assertIsNotNone(retrieved_action)
        self.assertEqual(retrieved_action.id, "sword_attack")

    def test_register_action_no_id(self):
        print("Running test: test_register_action_no_id")
        with self.assertRaises(ValueError):
            self.manager.register_action({"label": "Action without ID"})

    def test_get_nonexistent_action(self):
        print("Running test: test_get_nonexistent_action")
        action = self.manager.get_action("nonexistent_action")
        self.assertIsNone(action)

if __name__ == '__main__':
    unittest.main()
