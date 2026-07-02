# Contributing to Subsearch

Subsearch is a Windows subtitle downloader (PySide6, Python ≥ 3.14). By
participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Reporting

- **Bugs / features:** search existing issues first, then open one with the
  [bug](ISSUE_TEMPLATE/bug_report.md) or
  [feature](ISSUE_TEMPLATE/feature_request.md) template.
- **Security:** never open a public issue. Follow the [Security Policy](SECURITY.md).

For anything non-trivial, open an issue first so the direction can be agreed on.

## Setup

Develop on Windows 10/11 with Python ≥ 3.14.

```
git clone https://github.com/<your-username>/subsearch.git
cd subsearch
python -m venv .venv && .venv\Scripts\activate
pip install -e .[build,lint,tests,tools,type]
pre-commit install
```

Run tooling through the venv (`.venv\Scripts\python.exe -m <tool>`); system Python
lacks the dev deps.

## Making a change

- Create a feature branch off `dev` and target `dev` (not `main`) with the PR.
- Keep each PR to one feature or fix, with tests for what you change.
- Style: full descriptive names (no abbreviations), small single-purpose
  functions, comments only for a non-obvious *why*, log via `recorder.capture()`,
  raise typed exceptions. Don't add license headers.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org)
  (`fix(ui): ...`), enforced by commitizen.

## Before opening a PR

Run these locally. CI runs the same:

| Check | Command |
| --- | --- |
| Format | `black .` |
| Imports | `isort .` |
| Types | `mypy src` |
| Tests | `tox` or `pytest` |

Then open the PR against `dev`, fill in the
[template](PULL_REQUEST_TEMPLATE.md), and link the issue (`Closes #123`).

## License

Contributions are licensed under GPL v3.0 or later, the same as the project.
