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
from src.scraper import subscene
from src.scraper import opensubtitles
from src import file_manager as fm


def main() -> None:
    # initialising
    start = time.perf_counter()
    if got_key() is False:
        set_default_values()
        registry.add_context_menu()
        return exit(0)

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
        file_hash = 0000000000000000

    # TODO fix this so no try is needed
    try:
        param = get_parameters(cwd().lower(), lang_abbr, file_hash, video)
    except IndexError as err:
        log.output(err)
        fm.copy_log_to_cwd()
        if focus == "True":
            return exit(1)
        return

    # log parameters
    log.parameters(param, language, lang_abbr, hearing_impaired, precentage)

    # scrape with parameters
    print("\n")
    log.output("[Searching opensubtitles]")
    dios = opensubtitles.scrape(param, language, hearing_impaired)
    print("\n")
    log.output("[Searching subscene]")
    diss = subscene.scrape(param, language, lang_abbr, hearing_impaired, precentage)
    print(dios, diss)
    if dios is None and diss is None:
        elapsed = time.perf_counter() - start
        log.output(f"Finished in {elapsed} seconds.")
        fm.copy_log_to_cwd()
        if focus == "True":
            return exit(1)
        return

    # download files from scrape result
    print("\n")
    log.output("[Downloading]")
    if dios is not None:
        for item in dios:
            file_path, root_dl_url, current_num, total_num = item
            fm.download_zip(file_path, root_dl_url, current_num, total_num)
    if diss is not None:
        for item in diss:
            if item is not None:
                file_path, root_dl_url, current_num, total_num = item
                fm.download_zip(file_path, root_dl_url, current_num, total_num)

    # procsess downloaded files
    print("\n")
    log.output("[Procsessing files]")
    fm.extract_zips(cwd(), ".zip")
    fm.clean_up(cwd(), ".zip")
    fm.clean_up(cwd(), ").nfo")
    fm.rename_srts(f"{param.release}.srt", cwd(), f"{param.group}.srt", ".srt")
    fm.move_files(cwd(), f"{param.release}.srt", ".srt")
    print("\n\n")

    # finnishing up
    elapsed = time.perf_counter() - start
    log.output(f"Finished in {elapsed} seconds")

    if focus == "True":
        exit(1)


if __name__ == "__main__":
    main()
