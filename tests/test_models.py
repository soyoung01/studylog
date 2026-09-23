from studylog.models import parse_tags


def test_parse_tags_normalizes_and_dedupes() -> None:
    assert parse_tags("#ClaudeCode, plan mode ,#CLI, claudecode") == ["claudecode", "plan mode", "cli"]


def test_parse_tags_empty() -> None:
    assert parse_tags("  , ,") == []
