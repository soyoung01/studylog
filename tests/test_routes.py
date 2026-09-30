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


def test_export_returns_markdown_attachment(client: FlaskClient, repo: NoteRepository) -> None:
    repo.add("강의A", "첫 노트", "첫 내용", ["one", "two"])
    repo.add("강의B", "둘째 노트", "둘째 내용", [])
    res = client.get("/export")
    assert res.status_code == 200
    assert res.mimetype == "text/markdown"
    assert "attachment" in res.headers["Content-Disposition"]
    assert "studylog-notes.md" in res.headers["Content-Disposition"]
    text = res.get_data(as_text=True)
    assert "## 첫 노트" in text
    assert "- 강의: 강의A" in text
    assert "- 태그: #one #two" in text
    assert "첫 내용" in text
    assert "## 둘째 노트" in text


def test_index_links_to_export(client: FlaskClient) -> None:
    text = client.get("/").get_data(as_text=True)
    assert 'href="/export"' in text
    assert "노트 전체 Markdown으로 내보내기" in text


def test_export_empty(client: FlaskClient) -> None:
    res = client.get("/export")
    assert res.status_code == 200
    assert res.get_data(as_text=True).startswith("# Studylog 노트")

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


def test_favorite_adds_and_redirects_to_detail(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    res = client.post(f"/notes/{note.id}/favorite", data={"favorite": "1"})
    assert res.status_code == 302
    assert res.headers["Location"] == f"/notes/{note.id}"
    fetched = repo.get(note.id)
    assert fetched is not None and fetched.favorite is True


def test_favorite_redirects_to_next(client: FlaskClient, repo: NoteRepository) -> None:
    note = repo.add("강의", "t", "b", [])
    res = client.post(f"/notes/{note.id}/favorite", data={"favorite": "1", "next": "/?tag=x"})
    assert res.headers["Location"] == "/?tag=x"


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
