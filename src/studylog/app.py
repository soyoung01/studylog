from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.wrappers import Response

from . import __version__
from .db import NoteRepository
from .models import parse_tags
from .seed import seed_if_empty

THEME_COOKIE = "theme"
THEMES = ("light", "dark")
THEME_MAX_AGE = 60 * 60 * 24 * 365


def create_app(config: dict[str, Any] | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("STUDYLOG_SECRET_KEY", "dev"),
        DB_PATH=os.getenv("STUDYLOG_DB_PATH", "instance/studylog.db"),
        SEED=True,
    )
    if config:
        app.config.update(config)

    repo = NoteRepository(app.config["DB_PATH"])
    if app.config["SEED"]:
        seed_if_empty(repo)
    app.extensions["repo"] = repo

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        theme = request.cookies.get(THEME_COOKIE)
        return {"version": __version__, "theme": theme if theme in THEMES else None}

    @app.post("/theme")
    def set_theme() -> Response:
        theme = request.form.get("theme", "")
        if theme not in THEMES:
            abort(400)
        next_url = request.form.get("next", "")
        # 같은 사이트 안의 경로로만 돌아간다 (오픈 리다이렉트 방지)
        if not next_url.startswith("/") or next_url.startswith("//"):
            next_url = url_for("index")
        res = redirect(next_url)
        res.set_cookie(THEME_COOKIE, theme, max_age=THEME_MAX_AGE, samesite="Lax", httponly=True)
        return res

    @app.get("/")
    def index() -> str:
        tag = request.args.get("tag") or None
        query = request.args.get("q") or None
        return render_template(
            "index.html",
            notes=repo.list_notes(tag=tag, query=query),
            tags=repo.all_tags(),
            active_tag=tag,
            query=query or "",
            total=repo.count(),
        )

    @app.post("/notes")
    def create_note() -> Response:
        course = request.form.get("course", "").strip()
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not title or not body:
            flash("제목과 내용을 모두 입력해야 저장할 수 있어요.", "error")
            return redirect(url_for("index"))
        repo.add(course or "기타", title, body, parse_tags(request.form.get("tags", "")))
        flash("노트를 저장했어요.", "ok")
        return redirect(url_for("index"))

    @app.get("/notes/<int:note_id>")
    def note_detail(note_id: int) -> str:
        note = repo.get(note_id)
        if note is None:
            abort(404)
        return render_template("note.html", note=note)

    @app.get("/notes/<int:note_id>/edit")
    def edit_note_form(note_id: int) -> str:
        note = repo.get(note_id)
        if note is None:
            abort(404)
        return render_template("edit.html", note=note)

    @app.post("/notes/<int:note_id>/edit")
    def edit_note(note_id: int) -> Response:
        if repo.get(note_id) is None:
            abort(404)
        course = request.form.get("course", "").strip()
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not title or not body:
            flash("제목과 내용을 모두 입력해야 저장할 수 있어요.", "error")
            return redirect(url_for("edit_note_form", note_id=note_id))
        repo.update(note_id, course or "기타", title, body, parse_tags(request.form.get("tags", "")))
        flash("노트를 수정했어요.", "ok")
        return redirect(url_for("note_detail", note_id=note_id))

    @app.post("/notes/<int:note_id>/delete")
    def delete_note(note_id: int) -> Response:
        if not repo.delete(note_id):
            abort(404)
        flash("노트를 삭제했어요.", "ok")
        return redirect(url_for("index"))

    @app.get("/api/notes")
    def api_notes() -> Response:
        notes = repo.list_notes(tag=request.args.get("tag") or None, query=request.args.get("q") or None)
        return jsonify([n.to_dict() for n in notes])

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok", "version": __version__})

    return app
