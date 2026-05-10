"""SQLite store for users, chats, messages."""
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash BLOB NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    role TEXT NOT NULL,            -- 'user' or 'assistant'
    content TEXT NOT NULL,
    agents TEXT,                   -- comma-separated subagent names (assistant only)
    cost_usd REAL,
    duration_ms INTEGER,
    created_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id, id);
"""


def init():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with conn() as c:
        c.executescript(SCHEMA)


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    try:
        yield c
        c.commit()
    finally:
        c.close()


def now() -> int:
    return int(time.time())


# ---------- Users ----------
def create_user(email: str, password_hash: bytes) -> int:
    with conn() as c:
        cur = c.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email.lower(), password_hash, now()),
        )
        return cur.lastrowid


def get_user_by_email(email: str):
    with conn() as c:
        return c.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email.lower(),),
        ).fetchone()


def get_user(user_id: int):
    with conn() as c:
        return c.execute(
            "SELECT id, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()


# ---------- Chats ----------
def create_chat(user_id: int, title: str) -> int:
    t = now()
    with conn() as c:
        cur = c.execute(
            "INSERT INTO chats (user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, title, t, t),
        )
        return cur.lastrowid


def list_chats(user_id: int):
    with conn() as c:
        rows = c.execute(
            "SELECT id, title, created_at, updated_at FROM chats "
            "WHERE user_id = ? ORDER BY updated_at DESC LIMIT 100",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_chat(user_id: int, chat_id: int):
    with conn() as c:
        return c.execute(
            "SELECT id, title FROM chats WHERE id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()


def touch_chat(chat_id: int):
    with conn() as c:
        c.execute("UPDATE chats SET updated_at = ? WHERE id = ?", (now(), chat_id))


def delete_chat(user_id: int, chat_id: int) -> bool:
    with conn() as c:
        cur = c.execute(
            "DELETE FROM chats WHERE id = ? AND user_id = ?", (chat_id, user_id)
        )
        return cur.rowcount > 0


# ---------- Messages ----------
def add_message(chat_id: int, role: str, content: str,
                agents: str | None = None, cost_usd: float | None = None,
                duration_ms: int | None = None) -> int:
    with conn() as c:
        cur = c.execute(
            "INSERT INTO messages (chat_id, role, content, agents, cost_usd, duration_ms, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (chat_id, role, content, agents, cost_usd, duration_ms, now()),
        )
        return cur.lastrowid


def list_messages(chat_id: int):
    with conn() as c:
        rows = c.execute(
            "SELECT id, role, content, agents, cost_usd, duration_ms, created_at "
            "FROM messages WHERE chat_id = ? ORDER BY id",
            (chat_id,),
        ).fetchall()
        return [dict(r) for r in rows]
