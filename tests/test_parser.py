import unittest
from src.cli.parser import CommandParser

class TestCommandParser(unittest.TestCase):

    def setUp(self):
        self.parser = CommandParser()

    def test_parse_simple_command(self):
        print("Running test: test_parse_simple_command")
        command, args = self.parser.parse("status")
        self.assertEqual(command, "status")
        self.assertEqual(args, [])

    def test_parse_command_with_args(self):
        print("Running test: test_parse_command_with_args")
        command, args = self.parser.parse("create char Player hp=20")
        self.assertEqual(command, "create")
        self.assertEqual(args, ["char", "Player", "hp=20"])

    def test_parse_with_quoted_args(self):
        print("Running test: test_parse_with_quoted_args")
        command, args = self.parser.parse('attack "The Big Goblin"')
        self.assertEqual(command, "attack")
        self.assertEqual(args, ["The Big Goblin"])

    def test_parse_empty_string(self):
        print("Running test: test_parse_empty_string")
        command, args = self.parser.parse("")
        self.assertIsNone(command)
        self.assertEqual(args, [])

    def test_parse_case_insensitivity(self):
        print("Running test: test_parse_case_insensitivity")
        command, args = self.parser.parse("CREATE CHAR Player")
        self.assertEqual(command, "create") # Command should be lowercased
        self.assertEqual(args, ["CHAR", "Player"]) # Args should preserve case

if __name__ == '__main__':
    unittest.main()
