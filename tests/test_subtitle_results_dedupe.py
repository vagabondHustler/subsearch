from subsearch.providers.provider_helper import SubtitleResults
from subsearch.runtime.models import Subtitle, SubtitleStatus


def make_subtitle(name: str, download_url: str, status: SubtitleStatus) -> Subtitle:
    return Subtitle(
        token_result=91,
        provider_name="yifysubtitles",
        subtitle_name=name,
        download_url=download_url,
        request_data={},
        status=status,
    )


def test_identical_subtitle_is_added_once() -> None:
    results = SubtitleResults()
    first = make_subtitle("the.matrix.resurrections.2021", "http://example/1.zip", SubtitleStatus.ACCEPTED)
    duplicate = make_subtitle("the.matrix.resurrections.2021", "http://example/1.zip", SubtitleStatus.ACCEPTED)

    assert results.add(first) is True
    assert results.add(duplicate) is False
    assert results.accepted == [first]


def test_same_name_with_different_url_is_kept() -> None:
    results = SubtitleResults()
    first = make_subtitle("the.matrix.resurrections.2021", "http://example/1.zip", SubtitleStatus.ACCEPTED)
    other_upload = make_subtitle("the.matrix.resurrections.2021", "http://example/2.zip", SubtitleStatus.ACCEPTED)

    assert results.add(first) is True
    assert results.add(other_upload) is True
    assert results.accepted == [first, other_upload]
