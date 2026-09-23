from __future__ import annotations

from .db import NoteRepository

SAMPLE_NOTES = [
    (
        "Claude Code in action",
        "긴 세션은 범위를 정하고 방향을 잡는다",
        "Plan mode로 먼저 계획을 받고 꼼꼼히 검토한다.\n"
        "/compact 뒤에는 남길 내용을 지시로 적는다.\n"
        "빈 입력창에서 Esc 두 번이면 rewind 메뉴가 열린다.",
        ["claudecode", "plan mode", "compact", "rewind"],
    ),
    (
        "Claude Code in action",
        "goal과 loop로 자율 실행하기",
        "/goal은 완료 조건을 정하고, 평가기는 대화 기록만 읽는다.\n"
        "/loop는 CI나 배포 상태를 주기적으로 확인할 때 쓴다.",
        ["claudecode", "goal", "loop"],
    ),
    (
        "Claude Code in action",
        "병렬 작업은 worktree로 분리",
        "세션마다 독립된 파일 트리를 준다.\n"
        ".worktreeinclude에 .env 같은 git-ignored 파일을 적는다.",
        ["claudecode", "worktree", "git"],
    ),
]


def seed_if_empty(repo: NoteRepository) -> None:
    if repo.count() == 0:
        for course, title, body, tags in SAMPLE_NOTES:
            repo.add(course, title, body, tags)
