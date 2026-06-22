from subsearch.runtime.logging.logger import Logger


def _capture(logger: Logger) -> list[str]:
    captured: list[str] = []
    logger._sinks.clear()
    logger.add_sink(lambda message, **_: captured.append(message))
    return captured


def test_debug_messages_never_reach_console_sinks() -> None:
    logger = Logger()
    captured = _capture(logger)

    logger.debug("diagnostic detail")

    assert captured == []
    assert logger._console_history == []


def test_info_and_above_reach_console_sinks() -> None:
    logger = Logger()
    captured = _capture(logger)

    logger.info("user-facing line")
    logger.warning("heads up")
    logger.error("something failed")

    assert captured == ["user-facing line", "heads up", "something failed"]
