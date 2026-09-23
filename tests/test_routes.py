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


def test_api_notes_filters_by_tag(client: FlaskClient, repo: NoteRepository) -> None:
    repo.add("강의", "a", "x", ["one"])
    repo.add("강의", "b", "y", ["two"])
    data = client.get("/api/notes?tag=two").get_json()
    assert [n["title"] for n in data] == ["b"]


def test_health(client: FlaskClient) -> None:
    assert client.get("/health").get_json()["status"] == "ok"
