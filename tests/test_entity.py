import unittest
from src.entity import EntityManager

class TestEntityManager(unittest.TestCase):

    def setUp(self):
        self.manager = EntityManager()

    def test_create_and_get_entity(self):
        print("Running test: test_create_and_get_entity")
        entity = self.manager.create_entity("character", {"name": "Aragorn", "hp": 100})
        self.assertIsNotNone(entity)

        retrieved_entity = self.manager.get_entity(entity.id)
        self.assertEqual(retrieved_entity.id, entity.id)
        self.assertEqual(retrieved_entity.attributes["name"], "Aragorn")

    def test_update_and_get_attribute(self):
        print("Running test: test_update_and_get_attribute")
        entity = self.manager.create_entity("character", {"name": "Aragorn", "hp": 100})

        self.manager.update_attribute(entity.id, "hp", 90)
        updated_hp = self.manager.get_attribute(entity.id, "hp")
        self.assertEqual(updated_hp, 90)

        self.manager.update_attribute(entity.id, "status", "weary")
        status = self.manager.get_attribute(entity.id, "status")
        self.assertEqual(status, "weary")

    def test_list_entities(self):
        print("Running test: test_list_entities")
        self.manager.create_entity("character", {"name": "Aragorn"})
        self.manager.create_entity("character", {"name": "Gimli"})
        self.manager.create_entity("npc", {"name": "Orc"})

        all_entities = self.manager.list_entities()
        self.assertEqual(len(all_entities), 3)

        characters = self.manager.list_entities("character")
        self.assertEqual(len(characters), 2)

        npcs = self.manager.list_entities("npc")
        self.assertEqual(len(npcs), 1)

        monsters = self.manager.list_entities("monster")
        self.assertEqual(len(monsters), 0)

if __name__ == '__main__':
    unittest.main()
