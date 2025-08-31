import unittest
from unittest.mock import MagicMock, patch
from src.cli.command_handler import CommandHandler
from src.engine import Engine
from src.entity import Entity
from src.user import User, UserRole

class TestCommandHandler(unittest.TestCase):

    def setUp(self):
        # We use a mock engine to isolate the command handler for testing
        self.mock_engine = MagicMock(spec=Engine)
        self.mock_engine.current_user = MagicMock(spec=User)
        self.mock_engine.current_user.role = UserRole.GM
        self.handler = CommandHandler(self.mock_engine)

    def test_create_command_simple(self):
        print("Running test: test_create_command_simple")
        args = ["char", "Player1"]
        self.handler.do_create(args)

        # Assert that the engine's entity manager was called correctly
        self.mock_engine.get_entity_manager().create_entity.assert_called_with(
            "character", {"name": "Player1"}
        )

    def test_create_command_with_attrs(self):
        print("Running test: test_create_command_with_attrs")
        args = ["char", "Player2", "hp=30", "str=16"]
        self.handler.do_create(args)

        self.mock_engine.get_entity_manager().create_entity.assert_called_with(
            "character", {"name": "Player2", "hp": 30, "str": 16}
        )

    def test_add_command_success(self):
        print("Running test: test_add_command_success")
        args = ["Player1"]

        # Mock the return value of find_entity_by_name
        mock_player = Entity("character", {"name": "Player1"})
        self.mock_engine.get_entity_manager().find_entity_by_name.return_value = mock_player

        self.handler.do_add(args)

        # Assert that find was called
        self.mock_engine.get_entity_manager().find_entity_by_name.assert_called_with("Player1")
        # Assert that add_combatant was called with the correct ID
        self.mock_engine.get_initiative_tracker().add_combatant.assert_called_with(mock_player.id)

    def test_add_command_not_found(self):
        print("Running test: test_add_command_not_found")
        args = ["Ghost"]

        # Mock the return value of find_entity_by_name to be None
        self.mock_engine.get_entity_manager().find_entity_by_name.return_value = None

        self.handler.do_add(args)

        # Assert that add_combatant was NOT called
        self.mock_engine.get_initiative_tracker().add_combatant.assert_not_called()

    def test_init_command(self):
        print("Running test: test_init_command")
        self.handler.do_init([])
        self.mock_engine.roll_for_initiative.assert_called_once()

    def test_attack_command(self):
        print("Running test: test_attack_command")
        args = ["Goblin", "with", "Player"]
        mock_player = Entity("character", {"name": "Player"})
        mock_goblin = Entity("npc", {"name": "Goblin"})

        # The order of side_effect matters. First call finds the actor, second finds the target.
        self.mock_engine.get_entity_manager().find_entity_by_name.side_effect = [mock_player, mock_goblin]

        self.handler.do_attack(args)
        self.mock_engine.execute_action.assert_called_with("sword_attack", mock_player, mock_goblin)

    def test_save_command(self):
        print("Running test: test_save_command")
        args = ["my_save.json"]
        self.handler.do_save(args)
        self.mock_engine.save_game.assert_called_with("my_save.json")

    def test_load_command(self):
        print("Running test: test_load_command")
        args = ["my_save.json"]
        self.handler.do_load(args)
        self.mock_engine.load_game.assert_called_with("my_save.json")

if __name__ == '__main__':
    unittest.main()
