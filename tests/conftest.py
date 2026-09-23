from __future__ import annotations

from collections.abc import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from studylog.app import create_app
from studylog.db import NoteRepository


@pytest.fixture
def app() -> Iterator[Flask]:
    app = create_app({"TESTING": True, "DB_PATH": ":memory:", "SEED": False})
    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def repo(app: Flask) -> NoteRepository:
    r: NoteRepository = app.extensions["repo"]
    return r
