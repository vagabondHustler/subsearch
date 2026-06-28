from unittest.mock import MagicMock

import pytest

from subsearch.core.flows import (
    FLOW_BY_APP_MODE,
    ManualSearchFlow,
    PipelineSearchFlow,
    SettingsFlow,
    create_flow,
)
from subsearch.runtime.models import AppMode


def make_pipeline(app_mode: AppMode) -> MagicMock:
    pipeline = MagicMock()
    pipeline.bootstrap.app_mode = app_mode
    pipeline.bootstrap.all_providers_disabled.return_value = False
    pipeline.bootstrap.app_config.providers = {
        "opensubtitles": True,
        "yifysubtitles": False,
        "subsource": False,
        "tvsubtitles": False,
        "gestdown": False,
    }
    return pipeline


@pytest.mark.parametrize("app_mode", [AppMode.SEARCH_HYBRID, AppMode.SEARCH_AUTOMATIC])
def test_pipeline_flow_runs_steps_in_order(app_mode: AppMode) -> None:
    pipeline = make_pipeline(app_mode)
    recorded: list[str] = []
    for step in (
        "init_search",
        "subtitle_workspace",
        "download_files",
        "subtitle_post_processing",
        "run_provider_diagnostics",
        "clean_up",
        "finish_notification",
    ):
        getattr(pipeline, step).side_effect = lambda *_, _name=step: recorded.append(_name)

    PipelineSearchFlow(pipeline).run()

    assert recorded == [
        "init_search",
        "subtitle_workspace",
        "download_files",
        "subtitle_post_processing",
        "run_provider_diagnostics",
        "clean_up",
        "finish_notification",
    ]


@pytest.mark.parametrize("app_mode", [AppMode.SEARCH_HYBRID, AppMode.SEARCH_AUTOMATIC])
def test_pipeline_flow_opens_workspace_before_downloading(app_mode: AppMode) -> None:
    pipeline = make_pipeline(app_mode)

    PipelineSearchFlow(pipeline).run()

    method_calls = [name for name, _, _ in pipeline.method_calls]
    assert method_calls.index("subtitle_workspace") < method_calls.index("download_files")


def test_create_flow_selects_flow_class_by_app_mode() -> None:
    assert create_flow(make_pipeline(AppMode.SETTINGS)).__class__ is SettingsFlow
    assert create_flow(make_pipeline(AppMode.SEARCH_MANUAL)).__class__ is ManualSearchFlow
    assert create_flow(make_pipeline(AppMode.SEARCH_HYBRID)).__class__ is PipelineSearchFlow
    assert create_flow(make_pipeline(AppMode.SEARCH_AUTOMATIC)).__class__ is PipelineSearchFlow


def test_flow_by_app_mode_covers_every_mode() -> None:
    assert set(FLOW_BY_APP_MODE) == set(AppMode)
