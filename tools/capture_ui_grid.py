"""Capture a screenshot of each UI tab and arrange them into assets/ui_full.png.

Run with: python -m tools.capture_ui_grid (from the project src directory) or
python src/tools/capture_ui_grid.py.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from subsearch.runtime.config.defaults import ConfigKey  # noqa: E402
from subsearch.ui import warmup  # noqa: E402
from subsearch.ui.core import SettingsWindow, open_settings_window  # noqa: E402

GRID_COLUMNS = 3

MOCK_DOWNLOAD_DIRECTORY = r"C:\Users\example\Downloads\subs"
MOCK_EXTRACTION_DIRECTORY = r"C:\Users\example\AppData\Local\Subsearch\tmp"
MOCK_VALUES_BY_KEY = {
    ConfigKey.PATHS_DOWNLOAD_DIRECTORY: "",
    ConfigKey.PATHS_EXTRACTION_DIRECTORY: "",
    ConfigKey.PATHS_VIDEO_FILE_DIRECTORY: ".",
    ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY: "",
    ConfigKey.CREDENTIALS_SUBSOURCE_API_KEY_EXISTS: False,
}
MOCK_RESOLVED_DIRECTORY_BY_KEY = {
    ConfigKey.PATHS_DOWNLOAD_DIRECTORY: MOCK_DOWNLOAD_DIRECTORY,
    ConfigKey.PATHS_EXTRACTION_DIRECTORY: MOCK_EXTRACTION_DIRECTORY,
}
TILE_GAP = 0
GRID_BACKGROUND = (0, 0, 0, 0)
WINDOW_CORNER_RADIUS = 8
OUTPUT_PATH = PROJECT_ROOT / "assets" / "ui_full.png"
SETTLE_DELAY_MILLISECONDS = 150
DESKTOP_RENDER_DELAY_MILLISECONDS = 120


def _grab_window_from_desktop(window: QWidget) -> Image.Image:
    """Screenshot the desktop region under the window so the compositor-drawn
    Mica backdrop is captured exactly as it appears on screen; widget.grab()
    paints only widget content and never sees the DWM backdrop."""
    from PySide6.QtWidgets import QApplication

    screen = window.windowHandle().screen()
    frame = window.frameGeometry()
    device_pixel_ratio = screen.devicePixelRatio()
    pixmap = screen.grabWindow(0, frame.x(), frame.y(), frame.width(), frame.height())

    qimage = pixmap.toImage().convertToFormat(qimage_rgba_format())
    image = Image.frombytes("RGBA", (qimage.width(), qimage.height()), qimage.constBits().tobytes())
    radius = round(WINDOW_CORNER_RADIUS * device_pixel_ratio)
    return _round_corners(image, radius)


def _round_corners(image: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius, fill=255)
    rounded = image.copy()
    rounded.putalpha(mask)
    return rounded


def qimage_rgba_format():
    from PySide6.QtGui import QImage

    return QImage.Format.Format_RGBA8888


def _mask_sensitive_values(window: SettingsWindow) -> None:
    store = window.store
    real_read = store.read
    real_resolved_default = store.resolved_default_directory

    def read_with_mock(key, _real_read=real_read):
        if _is_config_key(key) and ConfigKey(key) in MOCK_VALUES_BY_KEY:
            return MOCK_VALUES_BY_KEY[ConfigKey(key)]
        return _real_read(key)

    def resolved_default_with_mock(key, _real=real_resolved_default):
        if _is_config_key(key) and ConfigKey(key) in MOCK_RESOLVED_DIRECTORY_BY_KEY:
            return MOCK_RESOLVED_DIRECTORY_BY_KEY[ConfigKey(key)]
        return _real(key)

    store.read = read_with_mock  # type: ignore[method-assign]
    store.resolved_default_directory = resolved_default_with_mock  # type: ignore[method-assign]


def _is_config_key(key) -> bool:
    try:
        ConfigKey(key)
        return True
    except ValueError:
        return False


def _navigation_interfaces(window: SettingsWindow) -> list[QWidget]:
    stacked = window.stackedWidget
    return [stacked.widget(index) for index in range(stacked.count())]


def _capture_each_tab(window: SettingsWindow) -> list[Image.Image]:
    window.raise_()
    window.activateWindow()
    _let_compositor_render()

    tab_images: list[Image.Image] = []
    for interface in _navigation_interfaces(window):
        _switch_to_interface(window, interface)
        tab_images.append(_grab_window_from_desktop(window))
    return tab_images


def _switch_to_interface(window: SettingsWindow, interface: QWidget) -> None:
    stacked = window.stackedWidget
    stacked.setCurrentWidget(interface)
    _wait_until(lambda: stacked.currentWidget() is interface)
    window.repaint()
    _let_compositor_render()


def _wait_until(condition, timeout_milliseconds: int = 2000) -> None:
    from PySide6.QtCore import QDeadlineTimer
    from PySide6.QtWidgets import QApplication

    deadline = QDeadlineTimer(timeout_milliseconds)
    while not condition() and not deadline.hasExpired():
        QApplication.processEvents()


def _let_compositor_render() -> None:
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    QApplication.processEvents()
    loop = QEventLoop()
    QTimer.singleShot(DESKTOP_RENDER_DELAY_MILLISECONDS, loop.quit)
    loop.exec()


def _arrange_into_grid(tab_images: list[Image.Image]) -> Image.Image:
    tile_width = max(image.width for image in tab_images)
    tile_height = max(image.height for image in tab_images)
    row_count = (len(tab_images) + GRID_COLUMNS - 1) // GRID_COLUMNS

    grid_width = GRID_COLUMNS * tile_width + (GRID_COLUMNS + 1) * TILE_GAP
    grid_height = row_count * tile_height + (row_count + 1) * TILE_GAP
    grid = Image.new("RGBA", (grid_width, grid_height), GRID_BACKGROUND)

    for tile_index, image in enumerate(tab_images):
        column = tile_index % GRID_COLUMNS
        row = tile_index // GRID_COLUMNS
        x = TILE_GAP + column * (tile_width + TILE_GAP)
        y = TILE_GAP + row * (tile_height + TILE_GAP)
        grid.paste(image, (x, y))
    return grid


def _capture_and_save() -> None:
    from PySide6.QtWidgets import QApplication

    window = next(w for w in QApplication.topLevelWidgets() if isinstance(w, SettingsWindow))
    _mask_sensitive_values(window)
    tab_images = _capture_each_tab(window)
    grid = _arrange_into_grid(tab_images)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    grid.save(OUTPUT_PATH)
    print(f"Saved {len(tab_images)} tabs to {OUTPUT_PATH}")
    window.close()


def main() -> None:
    warmup.start_warmup()

    def on_window_shown() -> None:
        QTimer.singleShot(SETTLE_DELAY_MILLISECONDS, _capture_and_save)

    open_settings_window(on_window_shown=on_window_shown)


if __name__ == "__main__":
    main()
