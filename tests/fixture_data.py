from pathlib import Path

from subsearch.runtime.models import ProviderUrls, SearchSubject

FAKE_SEARCH_SUBJECT_MOVIE = SearchSubject(
    file_exists=True,
    search_term="the.foo.bar.2021.1080p.web.h264-foobar",
    file_hash="",
    file_extension="mp4",
    file_path=Path("/path/to/the.foo.bar.2021.1080p.web.h264-foobar/the.foo.bar.2021.1080p.web.h264-foobar.mp4"),
)
FAKE_SEARCH_SUBJECT_SERIES = SearchSubject(
    file_exists=True,
    search_term="the.foo.bar.s01e01.1080p.web.h264-foobar",
    file_hash="",
    file_extension="mp4",
    file_path=Path("/path/to/the.foo.bar.s01e01.1080p.web.h264-foobar/the.foo.bar.s01e01.1080p.web.h264-foobar.mp4"),
)

FAKE_PROVIDER_URLS = ProviderUrls(
    opensubtitles=["fake_url"],
    opensubtitles_hash=["fake_url"],
    yifysubtitles=["fake_url"],
    subsource=["fake_url"],
    tvsubtitles=["fake_url"],
)
