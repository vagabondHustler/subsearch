from dataclasses import replace
from io import StringIO

from rich.console import Console

from subsearch.runtime.recorder._black_box.standard_out.spinner_display import (
    SpinnerDisplay,
)
from subsearch.runtime.recorder.console_theme import ConsoleTheme


def _terminal_display(window_size: int = 3, theme: ConsoleTheme | None = None) -> SpinnerDisplay:
    console = Console(file=StringIO(), force_terminal=True, width=80)
    return SpinnerDisplay(console, transient_window_size=window_size, log_name="subsearch.log", theme=theme)


def _rendered_text(display: SpinnerDisplay) -> str:
    capture_console = Console(file=StringIO(), force_terminal=False, width=80)
    capture_console.print(display._renderable())
    return capture_console.file.getvalue()  # type: ignore[union-attr]


def _done_marker(display: SpinnerDisplay) -> str:
    return display._theme.done_marker


def test_only_the_active_group_keeps_spinning() -> None:
    display = _terminal_display()
    display.open_group("Initializing")
    display.open_group("Searching")

    assert display._active_group is display._groups[-1]
    rendered = _rendered_text(display)
    marker = _done_marker(display)
    assert f"{marker} Initializing" in rendered  # the previous group is finished, no longer spinning
    assert f"{marker} Searching" not in rendered  # the active group has no done marker yet


def test_transient_window_is_bounded_and_evicts_oldest() -> None:
    display = _terminal_display(window_size=3)
    display.open_group("Searching")
    for index in range(5):
        display.add_line(f"line {index}", "info")

    assert display._active_group is not None
    assert len(display._active_group.transient_lines) == 3
    rendered = _rendered_text(display)
    assert "line 0" not in rendered and "line 1" not in rendered  # oldest two evicted
    assert "line 2" in rendered and "line 3" in rendered and "line 4" in rendered


def test_warning_is_summarized_compactly_not_printed_verbatim() -> None:
    display = _terminal_display(window_size=3)
    display.open_group("Searching")
    for index in range(5):
        display.add_line(f"progress {index}", "info")
    display.add_line("subsource skipped: no API key configured", "warning")

    assert display._active_group is not None
    assert len(display._active_group.transient_lines) == 3  # warnings do not roll in the transient window
    rendered = _rendered_text(display)
    assert "subsource skipped" not in rendered  # the verbose message is never shown
    assert "Searching 1 warning see subsearch.log for details" in rendered


def test_multiple_severities_render_as_one_combined_summary_line() -> None:
    display = _terminal_display()
    display.open_group("Searching")
    display.add_line("first", "warning")
    display.add_line("second", "warning")
    display.add_line("boom", "error")

    rendered = _rendered_text(display)
    assert "Searching 2 warnings, 1 error see subsearch.log for details" in rendered


def test_summary_renders_inline_under_its_phase() -> None:
    display = _terminal_display(theme=replace(ConsoleTheme(), summary_pinned_at_top=False))
    display.open_group("Searching")
    display.add_line("provider skipped", "warning")
    display.open_group("Waiting for user inputs")  # Searching is now a finished group

    rendered = _rendered_text(display)
    searching_position = rendered.index(f"{_done_marker(display)} Searching")
    summary_position = rendered.index("Searching 1 warning see subsearch.log")
    waiting_position = rendered.index("Waiting for user inputs")
    assert searching_position < summary_position < waiting_position  # summary sits under its own phase


def test_add_line_returns_compact_summary_for_reserved_levels_only() -> None:
    display = _terminal_display()
    display.open_group("Searching")
    assert display.add_line("transient detail", "info") is None
    assert display.add_line("provider skipped", "warning") == "Searching 1 warning see subsearch.log for details"


def test_repeated_banner_resumes_group_and_moves_it_to_the_bottom() -> None:
    display = _terminal_display()
    display.open_group("Waiting for user inputs")
    display.open_group("Searching")
    display.open_group("Waiting for user inputs")  # same title resumes; must not stack a duplicate

    titles = [group.title for group in display._groups]
    assert titles == ["Searching", "Waiting for user inputs"]  # resumed group moved to the bottom
    assert display._active_group is display._groups[-1]


def test_resuming_a_group_clears_its_stale_transient_lines() -> None:
    display = _terminal_display()
    display.open_group("Searching")
    display.add_line("old detail", "info")
    display.open_group("Waiting for user inputs")
    display.open_group("Searching")  # resume

    assert display._active_group is not None
    assert display._active_group.title == "Searching"
    assert len(display._active_group.transient_lines) == 0


def test_tick_advances_the_frame_without_a_new_entry() -> None:
    display = _terminal_display()
    display.open_group("Searching")
    before = display._groups[0].spinner.render(0.0)
    display.tick()
    after = display._groups[0].spinner.render(10.0)
    assert str(before) != str(after)  # the spinner glyph advanced on a tick, no new entry needed


def _done_bullet_style(display: SpinnerDisplay, title: str) -> str:
    group = next(group for group in display._groups if group.title == title)
    bullet = group.done_renderable()
    return str(bullet.style)  # the base marker style carries the severity color


def _severity_style(display: SpinnerDisplay, severity: str) -> str:
    return display._theme.done_severity_styles[severity]


def test_clean_phase_done_bullet_is_clean_color() -> None:
    display = _terminal_display()
    display.open_group("Searching")
    display.add_line("progress", "info")
    assert _done_bullet_style(display, "Searching") == _severity_style(display, "clean")


def test_done_bullet_color_tracks_worst_severity_seen() -> None:
    display = _terminal_display()
    display.open_group("Searching")
    display.add_line("a warning", "warning")
    assert _done_bullet_style(display, "Searching") == _severity_style(display, "warning")
    display.add_line("an error", "error")
    assert _done_bullet_style(display, "Searching") == _severity_style(display, "error")
    display.add_line("a critical", "critical")
    assert _done_bullet_style(display, "Searching") == _severity_style(display, "critical")
    display.add_line("late info", "info")
    assert _done_bullet_style(display, "Searching") == _severity_style(display, "critical")  # severity never downgrades


def test_failed_phase_keeps_its_severity_color_after_resuming() -> None:
    display = _terminal_display()
    display.open_group("Searching")
    display.add_line("an error", "error")
    display.open_group("Waiting for user inputs")
    display.open_group("Searching")  # resumed after a failure
    assert _done_bullet_style(display, "Searching") == _severity_style(display, "error")  # still marked failed


def test_snapshot_mirrors_the_rendered_box() -> None:
    display = _terminal_display(window_size=3)
    display.open_group("Initializing")
    display.open_group("Searching")
    for index in range(5):
        display.add_line(f"line {index}", "info")
    display.add_line("provider skipped", "warning")

    snapshot = display.snapshot()
    titles = [group.title for group in snapshot.groups]
    assert titles == ["Initializing", "Searching"]
    active = next(group for group in snapshot.groups if group.active)
    assert active.title == "Searching"
    assert [line.text for line in active.transient_lines] == ["line 2", "line 3", "line 4"]  # bounded, oldest evicted
    assert snapshot.summary_pinned_at_top is True
    assert len(snapshot.pinned_summaries) == 1
    summary = snapshot.pinned_summaries[0]
    assert summary.text == "Searching 1 warning see subsearch.log for details"
    assert summary.color == ConsoleTheme().done_severity_styles["warning"]
    assert not next(group for group in snapshot.groups if group.title == "Initializing").active


def test_close_finalizes_every_group_to_done() -> None:
    display = _terminal_display()
    display.open_group("Initializing")
    display.open_group("Searching")
    display.close()

    capture_console = Console(file=StringIO(), force_terminal=False, width=80)
    capture_console.print(display._final_renderable())
    rendered = capture_console.file.getvalue()  # type: ignore[union-attr]
    marker = _done_marker(display)
    assert f"{marker} Initializing" in rendered
    assert f"{marker} Searching" in rendered
