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


def test_stylesheet_has_dark_mode(client: FlaskClient) -> None:
    res = client.get("/static/style.css")
    assert res.status_code == 200
    assert "@media (prefers-color-scheme: dark)" in res.get_data(as_text=True)
    res.close()


def test_theme_defaults_to_system(client: FlaskClient) -> None:
    html = client.get("/").get_data(as_text=True)
    assert "data-theme" not in html
    assert "다크 모드로 전환" in html
    assert "라이트 모드로 전환" in html


def test_set_theme_sets_cookie_and_redirects_back(client: FlaskClient) -> None:
    res = client.post("/theme", data={"theme": "dark", "next": "/?tag=x"})
    assert res.status_code == 302
    assert res.headers["Location"] == "/?tag=x"
    assert "theme=dark" in res.headers["Set-Cookie"]
    assert 'data-theme="dark"' in client.get("/").get_data(as_text=True)

    client.post("/theme", data={"theme": "light", "next": "/"})
    assert 'data-theme="light"' in client.get("/").get_data(as_text=True)


def test_set_theme_rejects_unknown_value(client: FlaskClient) -> None:
    assert client.post("/theme", data={"theme": "neon"}).status_code == 400


def test_set_theme_ignores_external_next(client: FlaskClient) -> None:
    res = client.post("/theme", data={"theme": "dark", "next": "//evil.example"})
    assert res.headers["Location"] == "/"


def test_invalid_theme_cookie_is_ignored(client: FlaskClient) -> None:
    client.set_cookie("theme", "neon")
    assert "data-theme" not in client.get("/").get_data(as_text=True)


def test_health(client: FlaskClient) -> None:
    assert client.get("/health").get_json()["status"] == "ok"
