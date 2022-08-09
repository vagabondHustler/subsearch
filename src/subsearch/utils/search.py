import ctypes
import os
import time

from gui import widget_download
from scraper import opensubtitles, subscene

from . import (
    current_user,
    file_manager,
    file_parser,
    local_paths,
    log,
    raw_config,
    raw_registry,
    version,
)


def run_search(video_file_path: str) -> None:
    # initializing
    start = time.perf_counter()
    current_version = version.current()
    ctypes.windll.kernel32.SetConsoleTitleW(f"SubSearch - {current_version}")
    if current_user.got_key() is False:
        raw_config.set_default_json()
        raw_registry.add_context_menu()
        return

    language, lang_abbr = raw_config.get("language")
    hearing_impaired = raw_config.get("hearing_impaired")
    pct = raw_config.get("percentage")
    show_download_window = raw_config.get("show_download_window")
    show_terminal = raw_config.get("show_terminal")
    video_file_name_ext = video_file_path.lower().split("\\")[-1]
    video_file_name, video_file_ext = video_file_name_ext.rsplit(".", 1)
    video_file_name_ext = f"{video_file_name}.{video_file_ext}"
    file_hash = file_manager.get_hash(video_file_name_ext)

    try:
        param = file_parser.get_parameters(video_file_name, file_hash, lang_abbr)
    except IndexError as err:
        log.output(err)
        if show_terminal == "True":
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
        dl_data = f"{local_paths.cwd()}\\__subsearch__dl_data.tmp"
        if show_download_window == "True" and os.path.exists(dl_data):
            widget_download.show_widget()
            file_manager.clean_up(local_paths.cwd(), dl_data)

        elapsed = time.perf_counter() - start
        log.output(f"Finished in {elapsed} seconds.")
        if show_terminal == "True":
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

    if show_terminal == "True":
        input()
