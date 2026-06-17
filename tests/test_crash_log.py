from subsearch.runtime.logging import log_sanitizer, logger


def test_append_crash_session_writes_session_delimited_block(monkeypatch, tmp_path) -> None:
    crash_path = tmp_path / "crash.log"
    monkeypatch.setattr(logger.FILE_PATHS, "crash", crash_path)

    logger._append_crash_session("first crash session\nTraceback ...")
    logger._append_crash_session("second crash session\nTraceback ...")

    contents = crash_path.read_text(encoding="utf-8")
    assert contents.count(log_sanitizer.SESSION_SEPARATOR) == 2
    assert "first crash session" in contents
    assert "second crash session" in contents


def test_append_crash_session_skips_empty(monkeypatch, tmp_path) -> None:
    crash_path = tmp_path / "crash.log"
    monkeypatch.setattr(logger.FILE_PATHS, "crash", crash_path)

    logger._append_crash_session("   \n  ")

    assert not crash_path.exists()


def test_append_crash_session_is_size_capped(monkeypatch, tmp_path) -> None:
    crash_path = tmp_path / "crash.log"
    monkeypatch.setattr(logger.FILE_PATHS, "crash", crash_path)
    monkeypatch.setattr(logger, "LOG_MAX_BYTES", 200)

    for index in range(50):
        logger._append_crash_session(f"crash session {index} " + "x" * 50)

    assert crash_path.stat().st_size <= 200


def test_read_sanitized_prefers_crash_log(monkeypatch, tmp_path) -> None:
    crash_path = tmp_path / "crash.log"
    log_path = tmp_path / "log.log"
    crash_path.write_text("recorded crash with Traceback", encoding="utf-8")
    log_path.write_text("\x1c\nclean current session", encoding="utf-8")
    monkeypatch.setattr(log_sanitizer.FILE_PATHS, "crash", crash_path)
    monkeypatch.setattr(log_sanitizer.FILE_PATHS, "log", log_path)

    assert "recorded crash" in log_sanitizer.read_sanitized_crash_sessions()


def test_read_sanitized_falls_back_to_current_session(monkeypatch, tmp_path) -> None:
    crash_path = tmp_path / "crash.log"
    log_path = tmp_path / "log.log"
    log_path.write_text("\x1c\nolder session\x1c\ncurrent session", encoding="utf-8")
    monkeypatch.setattr(log_sanitizer.FILE_PATHS, "crash", crash_path)
    monkeypatch.setattr(log_sanitizer.FILE_PATHS, "log", log_path)

    result = log_sanitizer.read_sanitized_crash_sessions()
    assert "current session" in result
    assert "older session" not in result
