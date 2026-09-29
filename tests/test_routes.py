from flask.testing import FlaskClient

from studylog.db import NoteRepository


def test_index_renders(client: FlaskClient) -> None:
    res = client.get("/")
    assert res.status_code == 200
    assert "새 노트" in res.get_data(as_text=True)


def test_create_note_redirects_and_saves(client: FlaskClient, repo: NoteRepository) -> None:
    res = client.post("/notes", data={"course": "강의", "title": "t", "body": "b", "tags": "x, y"})
    assert res.status_code == 302
    assert repo.count() == 1
    assert repo.list_notes()[0].tags == ["x", "y"]


def test_create_note_requires_title_and_body(client: FlaskClient, repo: NoteRepository) -> None:
    client.post("/notes", data={"title": "", "body": ""})
    assert repo.count() == 0


def test_note_detail_404(client: FlaskClient) -> None:
    assert client.get("/notes/999").status_code == 404


def test_edit_note_form_renders(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "원래 제목", "원래 내용", ["a"])
    res = client.get(f"/notes/{note.id}/edit")
    assert res.status_code == 200
    assert "원래 제목" in res.get_data(as_text=True)


def test_edit_note_form_404(client: FlaskClient) -> None:
    assert client.get("/notes/999/edit").status_code == 404


def test_edit_note_updates_and_redirects(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "원래 제목", "원래 내용", ["a"])
    res = client.post(
        f"/notes/{note.id}/edit",
        data={"course": "새 강의", "title": "새 제목", "body": "새 내용", "tags": "b, c"},
    )
    assert res.status_code == 302
    assert res.headers["Location"] == f"/notes/{note.id}"
    updated = repo.get(note.id)
    assert updated is not None
    assert updated.title == "새 제목"
    assert updated.tags == ["b", "c"]


def test_edit_note_requires_title_and_body(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "원래 제목", "원래 내용", ["a"])
    client.post(f"/notes/{note.id}/edit", data={"title": "", "body": ""})
    unchanged = repo.get(note.id)
    assert unchanged is not None
    assert unchanged.title == "원래 제목"


def test_edit_note_404(client: FlaskClient) -> None:
    res = client.post("/notes/999/edit", data={"title": "t", "body": "b"})
    assert res.status_code == 404


def test_api_notes_filters_by_tag(client: FlaskClient, repo: NoteRepository) -> None:
    repo.add("강의", "a", "x", ["one"])
    repo.add("강의", "b", "y", ["two"])
    data = client.get("/api/notes?tag=two").get_json()
    assert [n["title"] for n in data] == ["b"]


def test_health(client: FlaskClient) -> None:
    assert client.get("/health").get_json()["status"] == "ok"


def test_favorite_adds_and_redirects_to_next(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    res = client.post(f"/notes/{note.id}/favorite", data={"favorite": "1", "next": "/?tag=x"})
    assert res.status_code == 302
    assert res.headers["Location"] == "/?tag=x"
    fetched = repo.get(note.id)
    assert fetched is not None and fetched.favorite is True


def test_favorite_removes(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    repo.set_favorite(note.id, True)
    client.post(f"/notes/{note.id}/favorite", data={"favorite": "0"})
    fetched = repo.get(note.id)
    assert fetched is not None and fetched.favorite is False


def test_favorite_is_idempotent(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    client.post(f"/notes/{note.id}/favorite", data={"favorite": "1"})
    client.post(f"/notes/{note.id}/favorite", data={"favorite": "1"})
    fetched = repo.get(note.id)
    assert fetched is not None and fetched.favorite is True


def test_favorite_rejects_unsafe_next(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    for bad in ("https://evil.example", "//evil.example", "javascript:alert(1)"):
        res = client.post(f"/notes/{note.id}/favorite", data={"favorite": "1", "next": bad})
        assert res.headers["Location"] == f"/notes/{note.id}"


def test_favorite_invalid_value_400(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    assert client.post(f"/notes/{note.id}/favorite", data={"favorite": "yes"}).status_code == 400
    assert client.post(f"/notes/{note.id}/favorite").status_code == 400


def test_favorite_404(client: FlaskClient) -> None:
    assert client.post("/notes/999/favorite", data={"favorite": "1"}).status_code == 404


def test_favorite_requires_post(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    assert client.get(f"/notes/{note.id}/favorite").status_code == 405


def test_index_favorites_filter(client: FlaskClient, repo: NoteRepository) -> None:
    a = repo.add("강의", "즐겨찾기 노트", "x", [])
    repo.add("강의", "일반 노트", "y", [])
    repo.set_favorite(a.id, True)
    html = client.get("/?favorites=1").get_data(as_text=True)
    assert "즐겨찾기 노트" in html
    assert "일반 노트" not in html
    assert "즐겨찾기 해제" in html


def test_note_detail_shows_favorite_button(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    assert "즐겨찾기에 추가" in client.get(f"/notes/{note.id}").get_data(as_text=True)


def test_api_notes_favorites(client: FlaskClient, repo: NoteRepository) -> None:
    a = repo.add("강의", "a", "x", [])
    repo.add("강의", "b", "y", [])
    repo.set_favorite(a.id, True)
    data = client.get("/api/notes?favorites=1").get_json()
    assert [(n["title"], n["favorite"]) for n in data] == [("a", True)]
