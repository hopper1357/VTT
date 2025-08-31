import unittest
from src.map import Map
from src.shape import Shape, ShapeType
from src.path import Path
from src.group import Group
from src.map_manager import MapManager

class TestDrawing(unittest.TestCase):

    def test_shape_serialization(self):
        """Tests that a Shape object can be serialized and deserialized correctly."""
        print("Running test: test_shape_serialization")
        shape = Shape(x=10, y=20, layer=1, shape_type=ShapeType.SQUARE, fill_color="#FF0000", opacity=0.5)
        map_obj = Map(name="test_map", width=100, height=100, objects=[shape])

        # Serialize
        map_dict = map_obj.to_dict()

        # Deserialize
        new_map = Map.from_dict(map_dict)
        self.assertEqual(len(new_map.objects), 1)
        new_shape = new_map.objects[0]

        self.assertIsInstance(new_shape, Shape)
        self.assertEqual(new_shape.x, 10)
        self.assertEqual(new_shape.y, 20)
        self.assertEqual(new_shape.shape_type, ShapeType.SQUARE)
        self.assertEqual(new_shape.fill_color, "#FF0000")
        self.assertEqual(new_shape.opacity, 0.5)
        self.assertEqual(new_shape.stroke_color, "#000000") # Check default value

    def test_path_serialization(self):
        """Tests that a Path object can be serialized and deserialized correctly."""
        print("Running test: test_path_serialization")
        points = [(0, 0), (10, 10), (20, 5)]
        path = Path(x=5, y=5, layer=2, points=points, stroke_width=3)
        map_obj = Map(name="test_map", width=100, height=100, objects=[path])

        # Serialize
        map_dict = map_obj.to_dict()

        # Deserialize
        new_map = Map.from_dict(map_dict)
        self.assertEqual(len(new_map.objects), 1)
        new_path = new_map.objects[0]

        self.assertIsInstance(new_path, Path)
        self.assertEqual(new_path.x, 5)
        self.assertEqual(new_path.y, 5)
        self.assertEqual(new_path.points, points)
        self.assertEqual(new_path.stroke_width, 3)

    def test_group_serialization(self):
        """Tests that a Group object can be serialized and deserialized correctly."""
        print("Running test: test_group_serialization")
        group = Group(x=0, y=0, layer=0, object_ids=["id1", "id2"])
        map_obj = Map(name="test_map", width=100, height=100, objects=[group])

        # Serialize
        map_dict = map_obj.to_dict()

        # Deserialize
        new_map = Map.from_dict(map_dict)
        self.assertEqual(len(new_map.objects), 1)
        new_group = new_map.objects[0]

        self.assertIsInstance(new_group, Group)
        self.assertEqual(new_group.object_ids, ["id1", "id2"])

    def test_group_movement(self):
        """Tests that moving a group also moves all its member objects."""
        print("Running test: test_group_movement")
        map_manager = MapManager()
        map_manager.create_map("group_test_map", 100, 100)

        # Create objects
        shape1 = Shape(x=10, y=10, layer=1)
        shape2 = Shape(x=20, y=20, layer=1)

        # Create a group containing the shapes
        # The group's own x/y can be an anchor, let's say at the average position
        group = Group(x=15, y=15, layer=0, object_ids=[shape1.id, shape2.id])

        # Add objects to the map
        map_manager.add_object_to_map("group_test_map", shape1)
        map_manager.add_object_to_map("group_test_map", shape2)
        map_manager.add_object_to_map("group_test_map", group)

        # Move the group
        map_manager.move_object("group_test_map", group.id, 25, 35) # dx=10, dy=20

        # Verify new positions
        self.assertEqual(group.x, 25)
        self.assertEqual(group.y, 35)

        # shape1 started at (10, 10), should move to (10+10, 10+20) = (20, 30)
        self.assertEqual(shape1.x, 20)
        self.assertEqual(shape1.y, 30)

        # shape2 started at (20, 20), should move to (20+10, 20+20) = (30, 40)
        self.assertEqual(shape2.x, 30)
        self.assertEqual(shape2.y, 40)

if __name__ == '__main__':
    unittest.main()
