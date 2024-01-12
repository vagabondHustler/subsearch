from pathlib import Path

from subsearch.globals.dataclasses import ProviderUrls, VideoFile

FAKE_VIDEO_FILE_MOVIE = VideoFile(
    filename="the.foo.bar.2021.1080p.web.h264-foobar",
    file_hash="",
    file_extension="mp4",
    file_path=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/the.foo.bar.2021.1080p.web.h264-foobar.mp4"),
    file_directory=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar"),
    subs_dir=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/subs"),
    tmp_dir=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/tmp_subsearch"),
)
FAKE_VIDEO_FILE_SERIES = VideoFile(
    filename="the.foo.bar.s01e01.1080p.web.h264-foobar",
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
