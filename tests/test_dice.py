import unittest
from src.dice import DiceRoller

class TestDiceRoller(unittest.TestCase):

    def setUp(self):
        self.roller = DiceRoller()

    def test_simple_roll(self):
        print("Running test: test_simple_roll")
        result = self.roller.roll("1d20")
        self.assertIsInstance(result, dict)
        self.assertIn("total", result)
        self.assertIn("rolls", result)
        self.assertIn("modifier", result)
        self.assertEqual(len(result["rolls"]), 1)
        self.assertTrue(1 <= result["rolls"][0] <= 20)
        self.assertEqual(result["modifier"], 0)
        self.assertEqual(result["total"], result["rolls"][0])

    def test_roll_with_positive_modifier(self):
        print("Running test: test_roll_with_positive_modifier")
        result = self.roller.roll("2d6+5")
        self.assertEqual(len(result["rolls"]), 2)
        self.assertTrue(1 <= result["rolls"][0] <= 6)
        self.assertTrue(1 <= result["rolls"][1] <= 6)
        self.assertEqual(result["modifier"], 5)
        self.assertEqual(result["total"], sum(result["rolls"]) + 5)

    def test_roll_with_negative_modifier(self):
        print("Running test: test_roll_with_negative_modifier")
        result = self.roller.roll("3d8-2")
        self.assertEqual(len(result["rolls"]), 3)
        self.assertEqual(result["modifier"], -2)
        self.assertEqual(result["total"], sum(result["rolls"]) - 2)

    def test_roll_with_spaces(self):
        print("Running test: test_roll_with_spaces")
        result = self.roller.roll("1d10 + 3")
        self.assertEqual(len(result["rolls"]), 1)
        self.assertEqual(result["modifier"], 3)
        self.assertEqual(result["total"], sum(result["rolls"]) + 3)

    def test_invalid_expression(self):
        print("Running test: test_invalid_expression")
        with self.assertRaises(ValueError):
            self.roller.roll("d20")
        with self.assertRaises(ValueError):
            self.roller.roll("1d")
        with self.assertRaises(ValueError):
            self.roller.roll("abc")
        with self.assertRaises(ValueError):
            self.roller.roll("1d20+ 5a")

if __name__ == '__main__':
    unittest.main()
