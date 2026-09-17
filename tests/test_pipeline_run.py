from unittest.mock import MagicMock

from subsearch.core.pipeline import SearchPipeline

PIPELINE_STEPS = (
    "init_search",
    "download_files",
    "subtitle_workspace",
    "subtitle_post_processing",
    "run_provider_diagnostics",
    "present_pending_notifications",
    "clean_up",
    "finish_notification",
)


def make_pipeline(should_run_headless_search: bool = True) -> SearchPipeline:
    pipeline = SearchPipeline.__new__(SearchPipeline)
    pipeline.bootstrap = MagicMock()
    pipeline.bootstrap.all_providers_disabled.return_value = True
    pipeline.call_conditions = MagicMock()
    pipeline.call_conditions.should_run_headless_search = should_run_headless_search
    for step in PIPELINE_STEPS:
        setattr(pipeline, step, MagicMock())
    return pipeline


def test_run_calls_every_step_in_order() -> None:
    pipeline = make_pipeline()
    order = MagicMock()
    for step in PIPELINE_STEPS:
        getattr(pipeline, step).side_effect = lambda *_, _name=step: order(_name)

    pipeline.run()

    assert [call.args[0] for call in order.call_args_list] == list(PIPELINE_STEPS)


def test_run_downloads_before_opening_the_workspace() -> None:
    pipeline = make_pipeline()

    pipeline.run()

    assert pipeline.download_files.call_count == 1
    assert pipeline.subtitle_workspace.call_count == 1


def test_run_skips_search_banner_when_search_runs_in_ui() -> None:
    # manual / always search in the UI; no headless search means no pre-search banner work.
    pipeline = make_pipeline(should_run_headless_search=False)

    pipeline.run()

    for step in PIPELINE_STEPS:
        getattr(pipeline, step).assert_called_once()
