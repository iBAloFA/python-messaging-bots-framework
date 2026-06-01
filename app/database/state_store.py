# app/database/state_store.py
import sqlite3
import json
import logging
from config import settings

logger = logging.getLogger(__name__)

class BotStateStore:
    def __init__(self, db_url: str):
        # Strip sqlite URI formatting to parse simple local filenames
        self.db_path = db_url.replace("sqlite:///", "")
        self._init_db()

    def _init_db(self):
        """Builds state table layers on initial startup cleanly."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id TEXT PRIMARY KEY,
                    current_state TEXT,
                    chat_history TEXT
                )
            """)
            conn.commit()

    def get_session(self, user_id: str) -> dict:
        """Retrieves or builds an empty schema row matrix."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT current_state, chat_history FROM user_sessions WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return {"state": row[0], "chat_history": json.loads(row[1])}
            return {"state": "START", "chat_history": []}

    def update_session(self, user_id: str, state: str, history: list):
        """Updates record rows using non-blocking transactional executions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_sessions (user_id, current_state, chat_history)
                VALUES (?, ?, ?)
            """, (user_id, state, json.dumps(history)))
            conn.commit()

    def clear_session(self, user_id: str):
        """Deletes active cache indexes safely."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM user_sessions WHERE user_id = ?", (user_id,))
            conn.commit()

state_store = BotStateStore(settings.database_url)
