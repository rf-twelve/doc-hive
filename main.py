import os
import sqlite3

# Define folder structure
folders = [
    "db",
    "documents/incoming",
    "documents/outgoing",
    "documents/others",
    "utils"
]

def create_directories():
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("📁 Directory structure created.")

def init_db():
    db_path = "db/document_store.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
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
    conn.close()
    print("🗃️ Database initialized at:", db_path)

if __name__ == "__main__":
    create_directories()
    init_db()
