import sqlite3
import os
import json

class Database:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._initialize_db()

    def _initialize_db(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False) # check_same_thread=False untuk akses dari thread ENet/Async
        self.cursor = self.conn.cursor()

        # Buat tabel Players
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                username TEXT PRIMARY KEY,
                password TEXT,
                pos_x REAL DEFAULT 0,
                pos_y REAL DEFAULT 0,
                world TEXT DEFAULT 'EXIT',
                inventory TEXT DEFAULT '[]'
            )
        """)
        self.conn.commit()

    def get_player(self, username):
        self.cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def create_player(self, username, password):
        try:
            self.cursor.execute("INSERT INTO players (username, password) VALUES (?, ?)", (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def save_player(self, username, pos_x, pos_y, world, inventory):
        inv_json = json.dumps(inventory)
        self.cursor.execute("""
            UPDATE players
            SET pos_x=?, pos_y=?, world=?, inventory=?
            WHERE username=?
        """, (pos_x, pos_y, world, inv_json, username))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
