from pathlib import Path

from commitizen.cz.conventional_commits import ConventionalCommitsCz
from jinja2 import FileSystemLoader

REPO = "https://github.com/vagabondHustler/subsearch"
_TEMPLATE_DIR = Path(__file__).parent


class SubsearchCz(ConventionalCommitsCz):
    """Conventional-commits changelog with subsearch's emoji sections and
    per-commit links. Sections mirror the old changelog_builder.json so the
    GitHub release body keeps the same shape, minus PR references."""

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
    }
    change_type_order = [
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
        message["message"] += f" - [{sha[:7]}]({REPO}/commit/{sha})"
        return message
