# Studylog

강의 노트를 기록하고 태그로 찾아보는 작은 Flask 웹앱입니다.
Claude Code 실습용으로 만들었으며, 로컬에서 실행하면 바로 브라우저에서 확인할 수 있습니다.

## 빠른 시작

```bash
# 1. 가상환경
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. 설치 (개발 도구 포함)
pip install -e ".[dev]"

# 3. 환경 변수
cp .env.example .env               # Windows: copy .env.example .env

# 4. 실행
python -m studylog
```

브라우저에서 http://127.0.0.1:5000 을 열면 샘플 노트 3개가 들어 있는 화면이 나옵니다.

## 검사

```bash
pytest     # 테스트
mypy       # 타입 체크 (strict)
```

GitHub에 올리면 `.github/workflows/ci.yml`이 push와 PR마다 두 검사를 실행합니다.

## 기능

- 노트 작성 (강의명, 제목, 내용, 태그)
- 태그 필터, 제목·내용 검색
- 노트 상세 보기, 삭제
- JSON API: `GET /api/notes?tag=...&q=...`
- 헬스 체크: `GET /health`

## 구조

```
studylog/
├── CLAUDE.md                 # Claude Code가 읽는 프로젝트 안내
├── .worktreeinclude          # 워크트리로 복사할 git-ignored 파일 (.env)
├── .env.example
├── .github/workflows/ci.yml
├── pyproject.toml
├── src/studylog/
│   ├── __init__.py           # __version__
│   ├── __main__.py           # python -m studylog 진입점
│   ├── app.py                # create_app(), 라우트
│   ├── db.py                 # NoteRepository (SQLite)
│   ├── models.py             # Note, parse_tags()
│   ├── seed.py               # 샘플 데이터
│   ├── templates/
│   └── static/style.css
└── tests/
```

## 실습 과제 목록

Claude Code 기능을 연습할 때 골라 쓰세요. 난이도 순입니다.

| 과제 | 연습하기 좋은 기능 |
|---|---|
| `python -m studylog --version` 플래그 추가 | Plan mode, /compact |
| 노트 수정 기능 (`/notes/<id>/edit`) | Plan mode, Rewind |
| 노트 본문 Markdown 렌더링 | Rewind (라이브러리 선택 되돌리기) |
| 목록 페이지네이션 (10개씩) | /goal (테스트·mypy 통과 조건) |
| 강의별 필터와 강의 목록 사이드바 | /goal |
| 노트 전체를 Markdown 파일로 내보내기 | Worktree (다른 과제와 병렬) |
| 다크 모드 | Worktree (UI 작업 분리) |
| CI 실패 시 원인 분석 | /loop |
