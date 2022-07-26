import ctypes
import time

from src.utilities.version import current_version
from src.utilities.local_paths import cwd
from src.scraper import opensubtitles, subscene
from src.utilities import edit_config, edit_registry
from src.utilities import file_manager as ufm
from src.utilities import log
from src.utilities.current_user import got_key
from src.utilities.read_config_json import get
from src.utilities.read_parameters import get_parameters


def main() -> None:
    # initializing
    start = time.perf_counter()
    version = current_version()
    ctypes.windll.kernel32.SetConsoleTitleW(f"SubSearch - {version}")
    if got_key() is False:
        edit_config.set_default_values()
        edit_registry.add_context_menu()
        return

    language, lang_abbr = get("language")
    hearing_impaired = get("hearing_impaired")
    pct = get("percentage")
    show_download_window = get("show_download_window")
    focus = get("terminal_focus")
    video_ext: list = get("video_ext")
    video = ufm.find_video(cwd(), video_ext, False)
    video_with_ext = ufm.find_video(cwd(), video_ext, True)
    if video_with_ext is not None:
        file_hash = ufm.get_hash(video_with_ext)
    elif video_with_ext is None:
        file_hash = None

    try:
        param = get_parameters(cwd().lower(), lang_abbr, file_hash, video)
    except IndexError as err:
        log.output(err)
        if focus == "True":
            return input()
        return

    # log parameters
    log.parameters(param, language, lang_abbr, hearing_impaired, pct)

    # scrape with parameters
    log.output("")
    log.output("[Searching opensubtitles]")
    scrape_opensubtitles = opensubtitles.scrape(param, language, hearing_impaired) if file_hash is not None else None
    log.output("")
    log.output("[Searching subscene]")
    scrape_subscene = subscene.scrape(param, language, lang_abbr, hearing_impaired, pct, show_download_window)
    if scrape_opensubtitles is None and scrape_subscene is None:
        if show_download_window == "True":
            import src.gui.download_window

        elapsed = time.perf_counter() - start
        log.output(f"Finished in {elapsed} seconds.")
        if focus == "True":
            return input()
        return

    # download files from scrape results
    if scrape_opensubtitles is not None:
        log.output("")
        log.output("[Downloading from Opensubtitles]")
        for item in scrape_opensubtitles:
            ufm.download_zip_auto(item)
    if scrape_subscene[0] is not None:
        log.output("")
        log.output("[Downloading from Subscene]")
        for item in scrape_subscene:
            ufm.download_zip_auto(item)

    # process downloaded files
    log.output("")
    log.output("[Procsessing files]")
    ufm.extract_zips(cwd(), ".zip")
    ufm.clean_up(cwd(), ".zip")
    ufm.clean_up(cwd(), ").nfo")
    ufm.rename_srts(f"{param.release}.srt", cwd(), f"{param.group}.srt", ".srt")
    ufm.move_files(cwd(), f"{param.release}.srt", ".srt")
    log.output("")

    # finishing up
    elapsed = time.perf_counter() - start
    log.output(f"Finished in {elapsed} seconds")

    if focus == "True":
        input()
