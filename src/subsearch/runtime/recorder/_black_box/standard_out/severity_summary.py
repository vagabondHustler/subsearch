from collections import Counter

_SEVERITY_LABELS = {
    "warning": "warning",
    "error": "error",
    "critical": "critical",
}
_SEVERITY_RENDER_ORDER = ("warning", "error", "critical")


def _pluralize(label: str, count: int) -> str:
    return label if count == 1 else f"{label}s"


def severity_summary(title: str, counts: Counter[str], log_name: str) -> str | None:
    """Compact one-liner of a phase's issue counts, e.g. ``Searching 2 warnings, 1 error see app.log for details``.

    Returns ``None`` when the phase recorded no warnings/errors/criticals.
    """
    parts = [
        f"{counts[severity]} {_pluralize(_SEVERITY_LABELS[severity], counts[severity])}"
        for severity in _SEVERITY_RENDER_ORDER
        if counts.get(severity, 0) > 0
    ]
    if not parts:
        return None
    return f"{title} {', '.join(parts)} see {log_name} for details"
