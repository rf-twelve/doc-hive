# utils/db_init.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "db", "document_store.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # ✅ Enable WAL mode
        cursor.execute("PRAGMA journal_mode=WAL;")

        # ✅ Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                doc_class TEXT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                sender TEXT,
                recipient TEXT,
                file_path TEXT NOT NULL
            )
        ''')
        conn.commit()

    print("✅ Database initialized at:", DB_PATH)