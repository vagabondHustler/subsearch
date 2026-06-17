import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import operations
from operations import (
    ARTIFACTS_PATH,
    CHANGELOG_NAME,
    CWD_PATH,
    EXE_NAME,
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

LICENSE_PATH = CWD_PATH / "LICENSE"


class Init:
    def run(self) -> None:
        ref_name = os.environ["GITHUB_REF_NAME"]
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

        identifier = operations.artifact_id(current_version, ref_name, run_id)
        step_summary.set_output("current_tag", current_version)
        step_summary.set_output("previous_tag", previous_version)
        step_summary.set_output("msi_name", operations.msi_name(current_version))
        step_summary.set_output("artifact_id", identifier)

        Git().push_with_tags(ref_name)


class MakeMsi:
    def run(self) -> None:
        Build().make_msi()


class BuildBinaries:
    def run(self) -> None:
        hasher = ArtifactHasher(StepSummary())
        hasher.write_to_hashes()
        hasher.prepare_build_artifacts()


class TestBinaries:
    def run(self) -> None:
        tester = BinaryTester()
        report = BinaryTestReport(StepSummary())
        self._run_msi(tester, report, "install")
        self._run_exe(tester, report)
        self._run_msi(tester, report, "uninstall")

    def _run_msi(self, tester: BinaryTester, report: BinaryTestReport, flag: str) -> None:
        tester.test_msi_package(flag, tester.msi_artifact_path())
        report.add_stage_card(flag)

    def _run_exe(self, tester: BinaryTester, report: BinaryTestReport) -> None:
        tester.test_executable(30)
        report.add_stage_card("executable")


class BuildChangelog:
    def run(self) -> None:
        ref_name = os.environ["GITHUB_REF_NAME"]
        current_tag = os.environ["CURRENT_TAG"]
        previous_tag = os.environ["PREVIOUS_TAG"]
        msi_name = os.environ["MSI_NAME"]
        msi_hash = os.environ["MSI_HASH"]
        exe_hash = os.environ["EXE_HASH"]

        commitizen = Commitizen()
        changelog = Changelog(StepSummary())

        ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
        Git().fetch(ref_name, with_tags=True)
        commitizen.render_changelog_for_tag(current_tag, ARTIFACTS_PATH / CHANGELOG_NAME)

        changelog.append_release_links(
            current_tag=current_tag,
            previous_tag=previous_tag,
            msi_name=msi_name,
            msi_hash=msi_hash,
            exe_name=EXE_NAME,
            exe_hash=exe_hash,
        )


class Prepare:
    def run(self) -> None:
        ref_name = os.environ["GITHUB_REF_NAME"]

        commitizen = Commitizen()
        changelog = Changelog(StepSummary())
        step_summary = StepSummary()

        predicted_version = commitizen.predicted_next_version()
        step_summary.set_output("releasable", "true" if predicted_version else "false")

        if predicted_version is None:
            return

        current_version = commitizen.current_version()
        step_summary.set_output("predicted_version", predicted_version)

        ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
        Git().fetch(ref_name, with_tags=True)
        commitizen.render_unreleased_changelog(predicted_version, ARTIFACTS_PATH / CHANGELOG_NAME)

        with open(ARTIFACTS_PATH / CHANGELOG_NAME, "a") as changelog_file:
            comparison = changelog.compare_link(previous_tag=current_version, current_tag=predicted_version)
            changelog_file.write(f"###### Full changelog: {comparison}")


class OpenMainPullRequest:
    RELEASE_LABEL = "release"
    SOURCE_BRANCH = "dev"
    TARGET_BRANCH = "main"
    OWNER = "vagabondHustler"

    def run(self) -> None:
        import subprocess

        predicted_version = os.environ["PREDICTED_VERSION"]
        title = f"Release {predicted_version}"
        body = (ARTIFACTS_PATH / CHANGELOG_NAME).read_text()

        pull_request_number = self._existing_pull_request_number()
        if pull_request_number:
            subprocess.run(
                [
                    "gh",
                    "pr",
                    "edit",
                    pull_request_number,
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
            return

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
        import subprocess

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

        identifier = operations.artifact_id(predicted_version, ref_name, run_id)
        step_summary.set_output("bumped", "true")
        step_summary.set_output("current_tag", predicted_version)
        step_summary.set_output("previous_tag", previous_version)
        step_summary.set_output("msi_name", operations.msi_name(predicted_version))
        step_summary.set_output("artifact_id", identifier)


class SyncDev:
    def run(self) -> None:
        release_branch = os.environ["GITHUB_REF_NAME"]
        Git().fast_forward_branch(source_branch=release_branch, target_branch="dev")


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


JOBS = {
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
        raise SystemExit(f"usage: workflows.py <job>\navailable jobs: {available}")
    JOBS[sys.argv[1]]().run()


if __name__ == "__main__":
    main()
