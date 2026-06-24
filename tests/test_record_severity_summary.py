from collections import Counter

from subsearch.runtime.recorder._black_box.standard_out.severity_summary import severity_summary


def test_no_issues_yields_no_summary() -> None:
    assert severity_summary("Searching", Counter(), "subsearch.log") is None


def test_single_warning_is_singular() -> None:
    summary = severity_summary("Searching", Counter({"warning": 1}), "subsearch.log")
    assert summary == "Searching 1 warning see subsearch.log for details"


def test_counts_pluralize() -> None:
    summary = severity_summary("Searching", Counter({"warning": 2}), "subsearch.log")
    assert summary == "Searching 2 warnings see subsearch.log for details"


def test_multiple_severities_combine_in_order() -> None:
    summary = severity_summary("Searching", Counter({"error": 1, "critical": 2, "warning": 3}), "subsearch.log")
    assert summary == "Searching 3 warnings, 1 error, 2 criticals see subsearch.log for details"
