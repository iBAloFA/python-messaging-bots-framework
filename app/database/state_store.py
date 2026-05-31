import sqlite3
import json
import logging

logger = logging.getLogger(__name__)

class BotStateStore:
    def __init__(self, db_path: str = "bot_memory.db"):
        # Remove sqlite+aiosqlite prefix if passed from env for standard sqlite compatibility
        self.db_path = db_path.replace("sqlite+aiosqlite:///", "")
        self._init_db()

    def _init_db(self):
        """Initializes the database schema if it does not exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id TEXT PRIMARY KEY,
                    current_state TEXT,
                    chat_history TEXT
                )
            """)
            conn.commit()

    def get_session(self, user_id: str) -> dict:
        """Retrieves user state and conversation history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_state, chat_history FROM user_sessions WHERE user_id = ?", (str(user_id),))
            row = cursor.fetchone()
            if row:
                return {
                    "current_state": row[0],
                    "chat_history": json.loads(row[1])
                }
            return {"current_state": "START", "chat_history": []}

    def update_session(self, user_id: str, state: str, history: list, max_history: int = 10):
        """Saves current state and truncates history to prevent payload bloating."""
        truncated_history = history[-max_history:]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_sessions (user_id, current_state, chat_history)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    current_state = excluded.current_state,
                    chat_history = excluded.chat_history
            """, (str(user_id), state, json.dumps(truncated_history)))
            conn.commit()

    def clear_session(self, user_id: str):
        """Resets the state engine for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_sessions WHERE user_id = ?", (str(user_id),))
            conn.commit()

# Instantiate global state store
state_store = BotStateStore()
