from pathlib import Path

from src.subsearch.data.data_classes import AppConfig, ProviderUrls, VideoFile

FAKE_CONFIG_PATH = Path(Path.cwd()) / "tests" / "resources" / "fake_config.json"
FAKE_MOVIE = VideoFile(
    file_name="the.foo.bar.2021.1080p.web.h264-foobar",
    file_hash="",
    file_extension="mp4",
    file_path=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/the.foo.bar.2021.1080p.web.h264-foobar.mp4"),
    file_directory=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar"),
    subs_dir=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/subs"),
    tmp_dir=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/tmp_subsearch"),
)
FAKE_SERIES = VideoFile(
    file_name="the.foo.bar.s01e01.1080p.web.h264-foobar",
    file_hash="",
    file_extension="mp4",
    file_path=Path("/path/to/the.foo.bar.s01e01.1080p.web.h264-foobar/the.foo.bar.s01e01.1080p.web.h264-foobar.mp4"),
    file_directory=Path("/path/to/the.foo.bar.s01e01.1080p.web.h264-foobar"),
    subs_dir=Path("/path/to/the.foo.bar.s01e01.1080p.web.h264-foobar/subs"),
    tmp_dir=Path("/path/to/the.foo.bar.s01e01.1080p.web.h264-foobar/tmp_subsearch"),
)

FAKE_PROVIDER_URLS = ProviderUrls(
    subscene="fake_url", opensubtitles="fake_url", opensubtitles_hash="fake_url", yifysubtitles="fake_url"
)
FAKE_VIDEO_FILE = VideoFile(
    file_name="the.foo.bar.2021.1080p.web.h264-foobar",
    file_hash="",
    file_extension="mp4",
    file_path=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/the.foo.bar.2021.1080p.web.h264-foobar.mp4"),
    file_directory=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar"),
    subs_dir=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/subs"),
    tmp_dir=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/tmp_subsearch"),
)

FAKE_APP_CONFIG = AppConfig(
    current_language="english",
    subtitle_type={
        "hearing_impaired": True,
        "non_hearing_impaired": True,
    },
    foreign_only=False,
    percentage_threshold=90,
    autoload_rename=True,
    autoload_move=True,
    context_menu=True,
    context_menu_icon=True,
    system_tray=True,
    toast_summary=False,
    manual_download_on_fail=True,
    show_terminal=False,
    use_threading=True,
    multiple_app_instances=False,
    log_to_file=False,
    file_extensions={
        ".avi": True,
        ".mp4": True,
        ".mkv": True,
        ".mpg": True,
        ".mpeg": True,
        ".mov": True,
        ".rm": True,
        ".vob": True,
        ".wmv": True,
        ".flv": True,
        ".3gp": True,
        ".3g2": True,
        ".swf": True,
        ".mswmm": True,
    },
    providers={
        "opensubtitles_site": True,
        "opensubtitles_hash": True,
        "subscene_site": True,
        "yifysubtitles_site": True,
    },
    hearing_impaired=True,
    non_hearing_impaired=False,
)
