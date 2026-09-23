from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Note:
    id: int
    course: str
    title: str
    body: str
    created_at: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "course": self.course,
            "title": self.title,
            "body": self.body,
            "created_at": self.created_at,
            "tags": self.tags,
        }


def parse_tags(raw: str) -> list[str]:
    """'#ClaudeCode, plan mode ,#CLI' -> ['claudecode', 'plan mode', 'cli']"""
    tags: list[str] = []
    for part in raw.split(","):
        tag = part.strip().lstrip("#").strip().lower()
        if tag and tag not in tags:
            tags.append(tag)
    return tags
