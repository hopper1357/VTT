import unittest
from unittest.mock import patch
from src.engine import Engine
from src.cli.command_handler import CommandHandler
from src.shape import Shape, ShapeType
from src.path import Path
from src.group import Group

class TestCommandHandlerDrawing(unittest.TestCase):

    def setUp(self):
        self.engine = Engine()
        self.handler = CommandHandler(self.engine)
        self.map_manager = self.engine.get_map_manager()
        self.map_manager.create_map("testmap", 20, 20)

    def test_handle_command_shape_place(self):
        """Tests the 'shape place' command."""
        print("Running test: test_handle_command_shape_place")

        # Test basic shape creation
        self.handler.handle_command("shape", ["place", "circle", "testmap", "5", "5"])
        game_map = self.map_manager.get_map("testmap")
        self.assertEqual(len(game_map.objects), 1)
        shape = game_map.objects[0]
        self.assertIsInstance(shape, Shape)
        self.assertEqual(shape.shape_type, ShapeType.CIRCLE)
        self.assertEqual(shape.x, 5)
        self.assertEqual(shape.y, 5)

        # Test shape creation with optional args
        self.handler.handle_command("shape", ["place", "square", "testmap", "10", "10", "layer=2", "fill_color=#00FF00"])
        self.assertEqual(len(game_map.objects), 2)
        shape2 = game_map.objects[1]
        self.assertIsInstance(shape2, Shape)
        self.assertEqual(shape2.shape_type, ShapeType.SQUARE)
        self.assertEqual(shape2.layer, 2)
        self.assertEqual(shape2.fill_color, "#00FF00")

    def test_handle_command_draw_path(self):
        """Tests the 'draw path' command."""
        print("Running test: test_handle_command_draw_path")

        self.handler.handle_command("draw", ["path", "testmap", "1,1", "2,2", "3,1", "stroke_width=3"])
        game_map = self.map_manager.get_map("testmap")
        self.assertEqual(len(game_map.objects), 1)
        path = game_map.objects[0]
        self.assertIsInstance(path, Path)
        self.assertEqual(path.points, [(1, 1), (2, 2), (3, 1)])
        self.assertEqual(path.stroke_width, 3)
        self.assertEqual(path.x, 1) # Anchor point
        self.assertEqual(path.y, 1) # Anchor point

    @patch('uuid.uuid4')
    def test_handle_command_group_create(self, mock_uuid):
        """Tests the 'group create' command."""
        print("Running test: test_handle_command_group_create")

        # Create some objects to group
        mock_uuid.side_effect = ["id-shape1", "id-shape2", "id-group"]
        shape1 = Shape(x=10, y=10, layer=1)
        shape2 = Shape(x=20, y=30, layer=1)
        self.map_manager.add_object_to_map("testmap", shape1)
        self.map_manager.add_object_to_map("testmap", shape2)

        # Create the group via the command handler
        self.handler.handle_command("group", ["create", "testmap", "id-shape1", "id-shape2"])

        game_map = self.map_manager.get_map("testmap")
        self.assertEqual(len(game_map.objects), 3) # shape1, shape2, group

        # Find the group object
        group_obj = None
        for obj in game_map.objects:
            if isinstance(obj, Group):
                group_obj = obj
                break

        self.assertIsNotNone(group_obj)
        self.assertEqual(group_obj.id, "id-group")
        self.assertEqual(group_obj.object_ids, ["id-shape1", "id-shape2"])
        # Check that the anchor is the average of the members' positions
        self.assertEqual(group_obj.x, 15) # (10+20)/2
        self.assertEqual(group_obj.y, 20) # (10+30)/2


if __name__ == '__main__':
    unittest.main()
