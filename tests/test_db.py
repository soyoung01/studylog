import sqlite3
from pathlib import Path

from studylog.db import NoteRepository


def test_add_and_get(repo: NoteRepository) -> None:
    note = repo.add("강의", "제목", "내용", ["a", "b"])
    fetched = repo.get(note.id)
    assert fetched is not None
    assert fetched.title == "제목"
    assert fetched.tags == ["a", "b"]


def test_filter_by_tag_and_query(repo: NoteRepository) -> None:
    repo.add("강의", "plan mode 정리", "읽기 전용", ["plan"])
    repo.add("강의", "worktree 정리", "병렬 작업", ["git"])
    assert [n.title for n in repo.list_notes(tag="git")] == ["worktree 정리"]
    assert [n.title for n in repo.list_notes(query="읽기")] == ["plan mode 정리"]


def test_all_tags_counts(repo: NoteRepository) -> None:
    repo.add("강의", "1", "x", ["a", "b"])
    repo.add("강의", "2", "y", ["a"])
    assert repo.all_tags() == [("a", 2), ("b", 1)]


def test_update(repo: NoteRepository) -> None:
    note = repo.add("강의", "원래 제목", "원래 내용", ["a"])
    updated = repo.update(note.id, "새 강의", "새 제목", "새 내용", ["b", "c"])
    assert updated is not None
    assert updated.course == "새 강의"
    assert updated.title == "새 제목"
    assert updated.body == "새 내용"
    assert updated.tags == ["b", "c"]
    fetched = repo.get(note.id)
    assert fetched is not None
    assert fetched.title == "새 제목"


def test_update_missing_note_returns_none(repo: NoteRepository) -> None:
    assert repo.update(999, "강의", "제목", "내용", []) is None


def test_delete(repo: NoteRepository) -> None:
    note = repo.add("강의", "삭제", "x", [])
    assert repo.delete(note.id) is True
    assert repo.get(note.id) is None
    assert repo.delete(note.id) is False


def test_new_note_is_not_favorite(repo: NoteRepository) -> None:
    note = repo.add("강의", "제목", "내용", [])
    assert note.favorite is False


def test_set_favorite(repo: NoteRepository) -> None:
    note = repo.add("강의", "제목", "내용", [])
    assert repo.set_favorite(note.id, True) is True
    fetched = repo.get(note.id)
    assert fetched is not None and fetched.favorite is True
    assert repo.set_favorite(note.id, False) is True
    fetched = repo.get(note.id)
    assert fetched is not None and fetched.favorite is False


def test_set_favorite_missing_note_returns_false(repo: NoteRepository) -> None:
    assert repo.set_favorite(999, True) is False


def test_list_favorites_only(repo: NoteRepository) -> None:
    a = repo.add("강의", "a", "x", ["t"])
    repo.add("강의", "b", "y", ["t"])
    repo.set_favorite(a.id, True)
    assert [n.title for n in repo.list_notes(favorites_only=True)] == ["a"]
    assert [n.title for n in repo.list_notes(tag="t", favorites_only=True)] == ["a"]


def test_migrates_db_without_favorite_column(tmp_path: Path) -> None:
    db_path = str(tmp_path / "old.db")
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, course TEXT NOT NULL, "
        "title TEXT NOT NULL, body TEXT NOT NULL, tags TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL)"
    )
    conn.execute("INSERT INTO notes (course, title, body, tags, created_at) VALUES ('강의', '옛 노트', 'x', '', '2026-01-01 00:00')")
    conn.commit()
    conn.close()

    repo = NoteRepository(db_path)
    [note] = repo.list_notes()
    assert note.favorite is False
    assert repo.set_favorite(note.id, True) is True
