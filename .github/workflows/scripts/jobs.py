import os
import subprocess
import sys
from pathlib import Path
from typing import Protocol

sys.path.insert(0, str(Path(__file__).parent))

import actions
from actions import (
    ArtifactHasher,
    BinaryTester,
    BinaryTestReport,
    Build,
    Changelog,
    Commitizen,
    Git,
    LicenseYear,
    StepSummary,
)
from config import CHANGELOG_NAME, EXE_NAME, Paths

LICENSE_PATH = Paths.working_directory / "LICENSE"


def release_branch() -> str:
    # On pull_request events GITHUB_REF_NAME is the merge ref (e.g. "925/merge"), not a
    # branch, so the release workflow passes the real target branch via RELEASE_BRANCH.
    return os.environ.get("RELEASE_BRANCH") or os.environ["GITHUB_REF_NAME"]


class Init:
    def run(self) -> None:
        ref_name = release_branch()
        run_id = os.environ["GITHUB_RUN_ID"]

        commitizen = Commitizen()
        step_summary = StepSummary()

        previous_version = commitizen.current_version()
        commitizen.bump_version()
        current_version = commitizen.current_version()

        bumped = current_version != previous_version
        step_summary.set_output("bumped", "true" if bumped else "false")

        if not bumped:
            return

        identifier = actions.artifact_id(current_version, ref_name, run_id)
        step_summary.set_output("current_tag", current_version)
        step_summary.set_output("previous_tag", previous_version)
        step_summary.set_output("msi_name", actions.msi_name(current_version))
        step_summary.set_output("artifact_id", identifier)

        Git().push_with_tags(ref_name)


class MakeMsi:
    _VERSION_FILE = Paths.working_directory / "src" / "subsearch" / "runtime" / "config" / "version.py"

    def run(self) -> None:
        dry_run_version = os.environ.get("DRY_RUN_VERSION")
        if dry_run_version:
            self._patch_version(dry_run_version)
        Build().make_msi()

    def _patch_version(self, version: str) -> None:
        self._VERSION_FILE.write_text(f'__version__ = "{version}"\n')


class BuildBinaries:
    def run(self) -> None:
        hasher = ArtifactHasher(StepSummary())
        hasher.write_to_hashes()
        hasher.prepare_build_artifacts()


class TestBinaries:
    def run(self) -> None:
        tester = BinaryTester()
        report = BinaryTestReport(StepSummary())
        tester.test_msi_package("install", tester.msi_artifact_path())
        report.add_stage_card("install")
        tester.test_executable(30)
        report.add_stage_card("executable")
        tester.test_msi_package("uninstall", tester.msi_artifact_path())
        report.add_stage_card("uninstall")


class BuildChangelog:
    def _read_env(self) -> tuple[str, str, str, str, str, str]:
        return (
            release_branch(),
            os.environ["CURRENT_TAG"],
            os.environ["PREVIOUS_TAG"],
            os.environ["MSI_NAME"],
            os.environ["MSI_HASH"],
            os.environ["EXE_HASH"],
        )

    def _generate_changelog(self, commitizen: Commitizen, ref_name: str, current_tag: str) -> None:
        Paths.artifacts.mkdir(parents=True, exist_ok=True)
        Git().fetch(ref_name, with_tags=True)
        commitizen.render_changelog_for_tag(current_tag, Paths.artifacts / CHANGELOG_NAME)

    def run(self) -> None:
        ref_name, current_tag, previous_tag, msi_name, msi_hash, exe_hash = self._read_env()
        commitizen = Commitizen()
        changelog = Changelog(StepSummary())
        self._generate_changelog(commitizen, ref_name, current_tag)
        changelog.append_release_links(
            current_tag=current_tag,
            previous_tag=previous_tag,
            msi_name=msi_name,
            msi_hash=msi_hash,
            exe_name=EXE_NAME,
            exe_hash=exe_hash,
        )


class Prepare:
    def _resolve_versions(self, commitizen: Commitizen, step_summary: StepSummary) -> tuple[str, str] | None:
        predicted_version = commitizen.predicted_next_version()
        step_summary.set_output("releasable", "true" if predicted_version else "false")
        if predicted_version is None:
            return None
        current_version = commitizen.current_version()
        step_summary.set_output("predicted_version", predicted_version)
        return current_version, predicted_version

    def _generate_changelog(self, commitizen: Commitizen, ref_name: str, predicted_version: str) -> None:
        Paths.artifacts.mkdir(parents=True, exist_ok=True)
        Git().fetch(ref_name, with_tags=True)
        commitizen.render_unreleased_changelog(predicted_version, Paths.artifacts / CHANGELOG_NAME)

    def _append_comparison_link(self, changelog: Changelog, previous_version: str, next_version: str) -> None:
        from datetime import datetime

        comparison = changelog.compare_link(previous_tag=previous_version, current_tag=next_version)
        username = (
            subprocess.run(["git", "config", "user.name"], capture_output=True, text=True).stdout.strip()
            or os.environ.get("GITHUB_ACTOR")
            or "unknown"
        )
        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        with open(Paths.artifacts / CHANGELOG_NAME, "a") as changelog_file:
            changelog_file.write(f"###### Full changelog: {comparison}\n")
            changelog_file.write(f"###### _last edited {timestamp} by @{username}_\n")

    def run(self) -> None:
        ref_name = os.environ["GITHUB_REF_NAME"]
        commitizen = Commitizen()
        step_summary = StepSummary()
        changelog = Changelog(step_summary)

        versions = self._resolve_versions(commitizen, step_summary)
        if versions is None:
            return

        current_version, predicted_version = versions
        step_summary.card(f"Preparing release Subsearch {predicted_version} ({current_version} → {predicted_version})")
        self._generate_changelog(commitizen, ref_name, predicted_version)
        self._append_comparison_link(changelog, current_version, predicted_version)


class OpenMainPullRequest:
    RELEASE_LABEL = "release"
    SOURCE_BRANCH = "dev"
    TARGET_BRANCH = "main"
    OWNER = "vagabondHustler"

    def _read_pr_content(self) -> tuple[str, str]:
        predicted_version = os.environ["PREDICTED_VERSION"]
        title = f"chore(release): {predicted_version}"
        body = (Paths.artifacts / CHANGELOG_NAME).read_text()
        return title, body

    def _edit_pull_request(self, number: str, title: str, body: str) -> None:
        subprocess.run(
            [
                "gh",
                "pr",
                "edit",
                number,
                "--title",
                title,
                "--body",
                body,
                "--add-assignee",
                self.OWNER,
                "--add-reviewer",
                self.OWNER,
            ],
            check=True,
        )

    def _create_pull_request(self, title: str, body: str) -> None:
        subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--base",
                self.TARGET_BRANCH,
                "--head",
                self.SOURCE_BRANCH,
                "--title",
                title,
                "--body",
                body,
                "--label",
                self.RELEASE_LABEL,
                "--assignee",
                self.OWNER,
                "--reviewer",
                self.OWNER,
            ],
            check=True,
        )

    def _existing_pull_request_number(self) -> str | None:
        completed = subprocess.run(
            [
                "gh",
                "pr",
                "list",
                "--base",
                self.TARGET_BRANCH,
                "--head",
                self.SOURCE_BRANCH,
                "--state",
                "open",
                "--json",
                "number",
                "--jq",
                ".[0].number",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        number = completed.stdout.strip()
        return number or None

    def run(self) -> None:
        title, body = self._read_pr_content()
        existing_number = self._existing_pull_request_number()
        if existing_number:
            self._edit_pull_request(existing_number, title, body)
        else:
            self._create_pull_request(title, body)


class DryRunInit:
    def run(self) -> None:
        ref_name = os.environ["GITHUB_REF_NAME"]
        run_id = os.environ["GITHUB_RUN_ID"]

        commitizen = Commitizen()
        step_summary = StepSummary()

        previous_version = commitizen.current_version()
        predicted_version = commitizen.predicted_next_version()

        if predicted_version is None:
            step_summary.set_output("bumped", "false")
            return

        identifier = actions.artifact_id(predicted_version, ref_name, run_id)
        step_summary.set_output("bumped", "true")
        step_summary.set_output("current_tag", predicted_version)
        step_summary.set_output("previous_tag", previous_version)
        step_summary.set_output("msi_name", actions.msi_name(predicted_version))
        step_summary.set_output("artifact_id", identifier)
        step_summary.card(f"Dry run of Subsearch {predicted_version} ({previous_version} → {predicted_version})")


class SyncDev:
    def run(self) -> None:
        Git().fast_forward_branch(source_branch=release_branch(), target_branch="dev")


class UpdateLicenseYear:
    def run(self) -> None:
        release_branch = os.environ["GITHUB_REF_NAME"]
        license_year = LicenseYear()
        git = Git()

        year = license_year.current_year()
        if not license_year.update_license_file(LICENSE_PATH, year):
            return

        git.commit_all(f"chore(license): renew copyright year to {year}")
        git.push(release_branch)
        git.fast_forward_branch(source_branch=release_branch, target_branch="dev")


class _Job(Protocol):
    def run(self) -> None: ...


JOBS: dict[str, type[_Job]] = {
    "init": Init,
    "dry_run_init": DryRunInit,
    "make_msi": MakeMsi,
    "build_binaries": BuildBinaries,
    "test_binaries": TestBinaries,
    "changelog": BuildChangelog,
    "prepare": Prepare,
    "open_main_pr": OpenMainPullRequest,
    "sync_dev": SyncDev,
    "update_license_year": UpdateLicenseYear,
}


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in JOBS:
        available = ", ".join(sorted(JOBS))
        raise SystemExit(f"usage: jobs.py <job>\navailable jobs: {available}")
    JOBS[sys.argv[1]]().run()


if __name__ == "__main__":
    main()
