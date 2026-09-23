# Studylog

강의 노트를 기록하고 태그로 찾아보는 Flask 웹앱.

## 명령어
- 설치: `pip install -e ".[dev]"`
- 실행: `python -m studylog` → http://127.0.0.1:5000
- 테스트: `pytest`
- 타입 체크: `mypy` (strict 모드)

## 구조
- `src/studylog/app.py`: `create_app()` 팩토리와 라우트
- `src/studylog/db.py`: SQLite 기반 `NoteRepository`
- `src/studylog/models.py`: `Note` 데이터클래스, `parse_tags()`
- `src/studylog/templates/`, `static/`: Jinja 템플릿과 CSS
- `tests/`: pytest (인메모리 DB 사용, `SEED=False`)

## 규칙
- 모든 함수에 타입 힌트를 붙이고 mypy strict를 통과시킨다.
- 새 기능에는 테스트를 함께 추가한다.
- 작업을 마치면 `pytest`와 `mypy`를 실행해 결과를 출력으로 남긴다.
- UI 문구는 한국어, 버튼은 동작을 그대로 설명하는 문구로 쓴다.
