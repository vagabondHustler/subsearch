import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).parent.parent / ".github" / "workflows" / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from actions import ReleaseValidation  # pyright: ignore[reportMissingImports] # noqa: E402
from jobs import OpenMainPullRequest  # pyright: ignore[reportMissingImports] # noqa: E402


@pytest.fixture
def validation() -> ReleaseValidation:
    return ReleaseValidation()


def test_block_inserted_into_empty_body(validation: ReleaseValidation) -> None:
    block = validation._body_block("abc123", "passed", "999")
    body = validation._replace_body_block("", block)
    assert body.startswith(validation.BODY_BLOCK_START)
    assert "passed" in body


def test_block_prepended_above_existing_body(validation: ReleaseValidation) -> None:
    existing = "#### Features:\n- thing"
    body = validation._replace_body_block(existing, validation._body_block("abc123", "passed", "999"))
    assert body.startswith(validation.BODY_BLOCK_START)
    assert body.rstrip().endswith("- thing")


def test_block_replaced_in_place_without_duplication(validation: ReleaseValidation) -> None:
    first = validation._replace_body_block("- thing", validation._body_block("abc123", "passed", "999"))
    second = validation._replace_body_block(first, validation._body_block("def456", "failed", "1000"))
    assert second.count(validation.BODY_BLOCK_START) == 1
    assert "def456" in second and "failed" in second
    assert "abc123" not in second
    assert second.rstrip().endswith("- thing")


def test_jobs_preserves_validation_block_across_regeneration(validation: ReleaseValidation) -> None:
    pull_request = OpenMainPullRequest()
    existing = validation._replace_body_block("old changelog", validation._body_block("abc123", "passed", "999"))
    regenerated = pull_request._pr_body("#### NEW CHANGELOG", existing)
    assert regenerated.startswith(pull_request.VALIDATION_BLOCK_START)
    assert regenerated.count(pull_request.VALIDATION_BLOCK_START) == 1
    assert "abc123" in regenerated
    assert "#### NEW CHANGELOG" in regenerated


def test_jobs_body_without_block_is_unchanged_shape() -> None:
    pull_request = OpenMainPullRequest()
    body = pull_request._pr_body("#### CL", "")
    assert pull_request.VALIDATION_BLOCK_START not in body
