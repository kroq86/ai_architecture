import sqlite3
from pathlib import Path
from typing import List

from telegram_ai_app.domain.models import ConversationTurn


class SessionStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_db()

    def load_history(self, session_key: str) -> List[ConversationTurn]:
        query = "select role, content from messages where session_key=? order by id asc"
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, (session_key,)).fetchall()
        return [ConversationTurn(role=row[0], content=row[1]) for row in rows]

    def save_turns(self, session_key: str, turns: List[ConversationTurn]) -> None:
        query = "insert into messages(session_key, role, content) values (?, ?, ?)"
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(query, [(session_key, t.role, t.content) for t in turns])
            conn.commit()

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        schema = """
        create table if not exists messages (
            id integer primary key autoincrement,
            session_key text not null,
            role text not null,
            content text not null
        );
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
            conn.commit()
