import subprocess
from datetime import datetime
from pathlib import Path

from commitizen.cz.conventional_commits.conventional_commits import ConventionalCommitsCz
from jinja2 import FileSystemLoader

REPO = "https://github.com/vagabondHustler/subsearch"
_TEMPLATE_DIR = Path(__file__).parent


def _git_user() -> str:
    result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
    return result.stdout.strip() or "unknown"


class SubsearchCz(ConventionalCommitsCz):
    # The custom template (named via [tool.commitizen] template in
    # pyproject.toml) renders these as h4 headings, so the titles themselves
    # carry no leading '#'. Overriding the loader to this package's own
    # directory makes the template resolvable regardless of working directory.
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

    # commitizen reads this off the instance and calls it as hook(message, commit),
    # so the bound method receives (message, commit). The base annotates it as a
    # plain callable attribute, hence the override ignore.
    def changelog_message_builder_hook(self, message: dict, commit) -> dict:  # type: ignore[override]
        sha = commit.rev
        username = _git_user()
        message["message"] += f" - [{username}@{sha[:7]}]({REPO}/commit/{sha})"
        return message

    def changelog_hook(self, full_changelog: str, _release_tag: str | None) -> str:  # type: ignore[override]
        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        username = _git_user()
        footer = f"\n###### _last edited {timestamp} by @{username}_\n"
        return full_changelog + footer
