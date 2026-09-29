from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from .models import Note

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    favorite INTEGER NOT NULL DEFAULT 0
);
"""


class NoteRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)
        self._migrate()

    def _migrate(self) -> None:
        # 즐겨찾기 기능 이전에 만들어진 DB에는 favorite 컬럼이 없다.
        columns = {row["name"] for row in self._conn.execute("PRAGMA table_info(notes)")}
        if "favorite" not in columns:
            self._conn.execute("ALTER TABLE notes ADD COLUMN favorite INTEGER NOT NULL DEFAULT 0")
            self._conn.commit()

    def _row_to_note(self, row: sqlite3.Row) -> Note:
        tags = [t for t in row["tags"].split(",") if t]
        return Note(
            id=row["id"],
            course=row["course"],
            title=row["title"],
            body=row["body"],
            created_at=row["created_at"],
            tags=tags,
            favorite=bool(row["favorite"]),
        )

    def add(self, course: str, title: str, body: str, tags: list[str]) -> Note:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        cur = self._conn.execute(
            "INSERT INTO notes (course, title, body, tags, created_at) VALUES (?, ?, ?, ?, ?)",
            (course, title, body, ",".join(tags), created_at),
        )
        self._conn.commit()
        note = self.get(int(cur.lastrowid or 0))
        assert note is not None
        return note

    def get(self, note_id: int) -> Note | None:
        row = self._conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return self._row_to_note(row) if row else None

    def update(self, note_id: int, course: str, title: str, body: str, tags: list[str]) -> Note | None:
        cur = self._conn.execute(
            "UPDATE notes SET course = ?, title = ?, body = ?, tags = ? WHERE id = ?",
            (course, title, body, ",".join(tags), note_id),
        )
        self._conn.commit()
        if cur.rowcount == 0:
            return None
        return self.get(note_id)

    def set_favorite(self, note_id: int, favorite: bool) -> bool:
        cur = self._conn.execute("UPDATE notes SET favorite = ? WHERE id = ?", (int(favorite), note_id))
        self._conn.commit()
        return cur.rowcount > 0

    def list_notes(
        self, tag: str | None = None, query: str | None = None, favorites_only: bool = False
    ) -> list[Note]:
        rows = self._conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
        notes = [self._row_to_note(r) for r in rows]
        if favorites_only:
            notes = [n for n in notes if n.favorite]
        if tag:
            notes = [n for n in notes if tag in n.tags]
        if query:
            q = query.lower()
            notes = [n for n in notes if q in n.title.lower() or q in n.body.lower()]
        return notes

    def delete(self, note_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self._conn.commit()
        return cur.rowcount > 0

    def all_tags(self) -> list[tuple[str, int]]:
        counts: dict[str, int] = {}
        for note in self.list_notes():
            for t in note.tags:
                counts[t] = counts.get(t, 0) + 1
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0])
