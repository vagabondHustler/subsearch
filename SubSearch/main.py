import time

from src import registry
from src.current_user import got_key
from src.edit_config import set_default_values
from src.config import get
from src.file_manager import find_video
from src.file_manager import get_hash
from src import log
from src.data import get_parameters
from src.sos import cwd
from src.sos import root_directory
from src.scraper import subscene
from src.scraper import opensubtitles
from src import file_manager as fm


def main() -> None:
    # initialising
    start = time.perf_counter()
    if got_key() is False:
        set_default_values()
        registry.add_context_menu()
        return

    language, lang_abbr = get("language")
    hearing_impaired = get("hearing_impaired")
    precentage = get("percentage")
    focus = get("terminal_focus")
    video_ext: list = get("video_ext")
    video = find_video(cwd(), video_ext, False)
    video_with_ext = find_video(cwd(), video_ext, True)
    if video_with_ext is not None:
        file_hash = get_hash(video_with_ext)
    elif video_with_ext is None:
        file_hash = None

    # TODO fix this so no try is needed
    try:
        param = get_parameters(cwd().lower(), lang_abbr, file_hash, video)
    except IndexError as err:
        log.output(err)
        fm.copy_log_to_cwd()
        if focus == "True":
            return input()
        return

    # log parameters
    log.parameters(param, language, lang_abbr, hearing_impaired, precentage)

    # scrape with parameters
    log.output("")
    log.output("[Searching opensubtitles]")
    dios = opensubtitles.scrape(param, language, hearing_impaired) if file_hash is not None else None
    log.output("")
    log.output("[Searching subscene]")
    diss = subscene.scrape(param, language, lang_abbr, hearing_impaired, precentage)
    if dios is None and diss is None:
        elapsed = time.perf_counter() - start
        log.output(f"Finished in {elapsed} seconds.")
        fm.copy_log_to_cwd()
        if focus == "True":
            return input()
        return

    # download files from scrape results
    if dios is not None:
        log.output("")
        log.output("[Downloading from Opensubtitles]")
        for item in dios:
            fm.download_zip(item)
    if diss is not None:
        log.output("")
        log.output("[Downloading from Subscene]")
        for item in diss:
            fm.download_zip(item)

    # procsess downloaded files
    log.output("")
    log.output("[Procsessing files]")
    fm.extract_zips(cwd(), ".zip")
    fm.clean_up(cwd(), ".zip")
    fm.clean_up(cwd(), ").nfo")
    fm.rename_srts(f"{param.release}.srt", cwd(), f"{param.group}.srt", ".srt")
    fm.move_files(cwd(), f"{param.release}.srt", ".srt")
    log.output("")

    # finnishing up
    elapsed = time.perf_counter() - start
    log.output(f"Finished in {elapsed} seconds")

    if focus == "True":
        input()


if __name__ == "__main__":
    if cwd() == root_directory():
        import src.settings

        exit()
    elif cwd() != root_directory():
        main()
