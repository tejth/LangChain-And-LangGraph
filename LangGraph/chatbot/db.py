import sqlite3
import uuid
from datetime import datetime

DB_PATH = "chat_history.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    conn.commit()
    conn.close()


def create_conversation(title="New Chat"):
    conn = get_connection()
    c = conn.cursor()
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    c.execute(
        "INSERT INTO conversations (id, title, created_at) VALUES (?, ?, ?)",
        (conv_id, title, now),
    )
    conn.commit()
    conn.close()
    return conv_id


def get_all_conversations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM conversations ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_messages(conversation_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id ASC",
        (conversation_id,),
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_message(conversation_id, role, content):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, now),
    )
    conn.commit()
    conn.close()


def update_conversation_title(conversation_id, title):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE conversations SET title = ? WHERE id = ?",
        (title, conversation_id),
    )
    conn.commit()
    conn.close()


def delete_conversation(conversation_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    c.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()
