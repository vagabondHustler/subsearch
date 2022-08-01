import ctypes
import time
import os

from src.scraper import opensubtitles, subscene
from src.utilities import (
    current_user,
    edit_config,
    edit_registry,
    file_manager,
    local_paths,
    log,
    read_config,
    read_parameters,
    version,
)


def main():
    # initializing
    start = time.perf_counter()
    current_version = version.current()
    ctypes.windll.kernel32.SetConsoleTitleW(f"SubSearch - {current_version}")
    if current_user.got_key() is False:
        edit_config.set_default_values()
        edit_registry.add_context_menu()
        return

    language, lang_abbr = read_config.get("language")
    hearing_impaired = read_config.get("hearing_impaired")
    pct = read_config.get("percentage")
    show_download_window = read_config.get("show_download_window")
    focus = read_config.get("show_terminal")
    video_ext: list = read_config.get("video_ext")
    video = file_manager.find_video(local_paths.cwd(), video_ext, False)
    video_with_ext = file_manager.find_video(local_paths.cwd(), video_ext, True)
    if video_with_ext is not None:
        file_hash = file_manager.get_hash(video_with_ext)
    elif video_with_ext is None:
        file_hash = None

    try:
        param = read_parameters.get_parameters(local_paths.cwd().lower(), lang_abbr, file_hash, video)
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
        file = f"{local_paths.cwd()}\\dl_data.tmp"
        if show_download_window == "True" and os.path.exists(file):
            from src.gui import widget_download

            widget_download.show_widget()
            file_manager.clean_up(local_paths.cwd(), "dl_data.tmp")

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
            file_manager.download_zip_auto(item)
    if scrape_subscene[0] is not None:
        log.output("")
        log.output("[Downloading from Subscene]")
        for item in scrape_subscene:
            file_manager.download_zip_auto(item)

    # process downloaded files
    log.output("")
    log.output("[Procsessing files]")
    file_manager.extract_zips(local_paths.cwd(), ".zip")
    file_manager.clean_up(local_paths.cwd(), ".zip")
    file_manager.clean_up(local_paths.cwd(), ").nfo")
    file_manager.rename_srts(f"{param.release}.srt", local_paths.cwd(), f"{param.group}.srt", ".srt")
    file_manager.move_files(local_paths.cwd(), f"{param.release}.srt", ".srt")
    log.output("")

    # finishing up
    elapsed = time.perf_counter() - start
    log.output(f"Finished in {elapsed} seconds")

    if focus == "True":
        input()
