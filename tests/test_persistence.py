import unittest
import os
from src.engine import Engine
from src.persistence import PersistenceManager

class TestPersistence(unittest.TestCase):

    def setUp(self):
        self.engine = Engine()
        self.engine.load_system_module("dnd5e")

        em = self.engine.get_entity_manager()
        tracker = self.engine.get_initiative_tracker()

        self.player = em.create_entity("character", {"name": "Player", "hp": 20})
        self.npc = em.create_entity("npc", {"name": "Goblin", "hp": 7})

        tracker.add_combatant(self.player.id)
        tracker.set_initiative(self.player.id, 15)
        tracker.add_combatant(self.npc.id)
        tracker.set_initiative(self.npc.id, 10)

        self.persistence_manager = PersistenceManager()

    def test_gather_game_state(self):
        print("Running test: test_gather_game_state")
        game_state = self.persistence_manager.gather_game_state(self.engine)

        self.assertIn("entity_manager", game_state)
        self.assertIn("initiative_tracker", game_state)
        self.assertIn("active_module_id", game_state)

        self.assertEqual(game_state['active_module_id'], 'dnd5e')

        # Check entity data
        self.assertEqual(len(game_state['entity_manager']['entities']), 2)
        entity_names = {e['attributes']['name'] for e in game_state['entity_manager']['entities']}
        self.assertEqual(entity_names, {"Player", "Goblin"})

        # Check initiative data
        self.assertEqual(len(game_state['initiative_tracker']['combatants']), 2)
        self.assertEqual(game_state['initiative_tracker']['combatants'][self.player.id], 15)

    def test_save_and_load_game(self):
        print("Running test: test_save_and_load_game")
        save_filepath = "test_save.json"

        # 1. Gather initial state
        original_state = self.persistence_manager.gather_game_state(self.engine)

        # 2. Save the state to a file
        save_success = self.persistence_manager.save_game(original_state, save_filepath)
        self.assertTrue(save_success)
        self.assertTrue(os.path.exists(save_filepath))

        # 3. Load the state back from the file
        loaded_state = self.persistence_manager.load_game(save_filepath)

        # 4. Compare the states
        self.assertIsNotNone(loaded_state)
        self.assertEqual(original_state, loaded_state)

        # 5. Clean up the save file
        os.remove(save_filepath)

if __name__ == '__main__':
    unittest.main()
