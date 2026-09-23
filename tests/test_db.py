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


def test_delete(repo: NoteRepository) -> None:
    note = repo.add("강의", "삭제", "x", [])
    assert repo.delete(note.id) is True
    assert repo.get(note.id) is None
    assert repo.delete(note.id) is False
