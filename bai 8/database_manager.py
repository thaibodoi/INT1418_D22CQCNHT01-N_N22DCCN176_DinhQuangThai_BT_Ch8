import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_path="audio_index.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audio_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                loudness REAL,
                pitch REAL,
                brightness REAL,
                bandwidth REAL,
                harmonicity REAL
            )
        """)
        conn.commit()
        conn.close()

    def add_audio(self, filename, features):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO audio_index 
            (filename, loudness, pitch, brightness, bandwidth, harmonicity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            filename,
            features["loudness"],
            features["pitch"],
            features["brightness"],
            features["bandwidth"],
            features["harmonicity"]
        ))
        conn.commit()
        conn.close()

    def get_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audio_index")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def search_by_property(self, prop_name, min_val, max_val):
        """Search for sounds within a specific property range."""
        valid_props = ["loudness", "pitch", "brightness", "bandwidth", "harmonicity"]
        if prop_name not in valid_props:
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM audio_index WHERE {prop_name} >= ? AND {prop_name} <= ?", (min_val, max_val))
        rows = cursor.fetchall()
        conn.close()
        return rows

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database initialized.")
