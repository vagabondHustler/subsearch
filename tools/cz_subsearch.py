from pathlib import Path

from commitizen.cz.conventional_commits.conventional_commits import ConventionalCommitsCz
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
    def changelog_message_builder_hook(self, message: dict, commit) -> dict:  # type: ignore[override]
        sha = commit.rev
        message["message"] += f" - [{sha[:7]}]({REPO}/commit/{sha})"
        return message
