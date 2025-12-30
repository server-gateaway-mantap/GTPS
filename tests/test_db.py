import os
import unittest
from src.data.database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_name = "test_data.db"
        self.db = Database(self.db_name)

    def tearDown(self):
        self.db.close()
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def test_create_get_player(self):
        # Create
        success = self.db.create_player("jules", "pass123")
        self.assertTrue(success)

        # Duplicate create should fail
        success_dup = self.db.create_player("jules", "pass123")
        self.assertFalse(success_dup)

        # Get
        player = self.db.get_player("jules")
        self.assertIsNotNone(player)
        self.assertEqual(player[0], "jules")
        self.assertEqual(player[1], "pass123")

    def test_save_player(self):
        self.db.create_player("tester", "123")
        self.db.save_player("tester", 100.0, 200.0, "START", [1, 2, 3])

        player = self.db.get_player("tester")
        self.assertEqual(player[2], 100.0) # x
        self.assertEqual(player[3], 200.0) # y
        self.assertEqual(player[4], "START") # world
        self.assertIn("1", player[5]) # inventory json string

if __name__ == '__main__':
    unittest.main()
