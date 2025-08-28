import unittest
from src.initiative import InitiativeTracker

class TestInitiativeTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = InitiativeTracker()
        self.tracker.add_combatant("player1")
        self.tracker.add_combatant("player2")
        self.tracker.add_combatant("npc1")

    def test_add_combatant(self):
        print("Running test: test_add_combatant")
        self.assertIn("player1", self.tracker.combatants)
        self.assertIsNone(self.tracker.combatants["player1"])

    def test_set_initiative(self):
        print("Running test: test_set_initiative")
        self.tracker.set_initiative("player1", 20)
        self.tracker.set_initiative("player2", 5)

        self.assertEqual(self.tracker.combatants["player1"], 20)
        self.assertEqual(self.tracker.combatants["player2"], 5)

        with self.assertRaises(ValueError):
            self.tracker.set_initiative("nonexistent", 10)

    def test_get_turn_order(self):
        print("Running test: test_get_turn_order")
        self.tracker.set_initiative("player1", 20)
        self.tracker.set_initiative("player2", 5)
        self.tracker.set_initiative("npc1", 15)

        turn_order = self.tracker.get_turn_order()
        expected_order = ["player1", "npc1", "player2"]
        self.assertEqual(turn_order, expected_order)

    def test_get_turn_order_with_ties(self):
        print("Running test: test_get_turn_order_with_ties")
        # Python's sort is stable, so original insertion order should be preserved for ties.
        self.tracker.set_initiative("player1", 20)
        self.tracker.set_initiative("player2", 5)
        self.tracker.set_initiative("npc1", 20) # Tie with player1

        turn_order = self.tracker.get_turn_order()
        # player1 was added first, so it should come before npc1 in a tie.
        expected_order = ["player1", "npc1", "player2"]
        self.assertEqual(turn_order, expected_order)

    def test_clear(self):
        print("Running test: test_clear")
        self.tracker.clear()
        self.assertEqual(len(self.tracker.combatants), 0)

if __name__ == '__main__':
    unittest.main()
