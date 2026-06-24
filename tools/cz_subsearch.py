from pathlib import Path

from commitizen.cz.conventional_commits.conventional_commits import (
    ConventionalCommitsCz,
)
from jinja2 import FileSystemLoader

REPO = "https://github.com/vagabondHustler/subsearch"
_TEMPLATE_DIR = Path(__file__).parent


class SubsearchCz(ConventionalCommitsCz):
    template_loader = FileSystemLoader(str(_TEMPLATE_DIR))

    change_type_map = {
        "feat": "✨ Features:",
        "fix": "🐛 Fixes:",
        "docs": "📚 Docs:",
        "build": "⚙️ Other:",
        "ci": "⚙️ Other:",
        "perf": "⚙️ Other:",
        "refactor": "⚙️ Other:",
        "style": "⚙️ Other:",
        "test": "⚙️ Other:",
        "BREAKING CHANGE": "‼️ Breaking changes:",
    }
    change_type_order = [
        "‼️ Breaking changes:",
        "✨ Features:",
        "🐛 Fixes:",
        "📚 Docs:",
        "⚙️ Other:",
    ]

    @property
    def template_extras(self) -> dict:
        section_labels = {key: self._strip_section_label(key) for key in self.change_type_order}
        return {"change_type_order": self.change_type_order, "section_labels": section_labels}

    @staticmethod
    def _strip_section_label(key: str) -> str:
        return "".join(char for char in key if char.isalpha() or char.isspace()).strip()

    def changelog_message_builder_hook(self, message: dict, commit) -> dict:  # type: ignore[override]
        message["sha"] = commit.rev[:7]
        body = commit.body or ""
        last_line = body.strip().splitlines()[-1] if body.strip() else ""
        message["important"] = last_line.strip() == "ㅤ"
        return message
