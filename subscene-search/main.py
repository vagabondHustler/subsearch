import time

from src import registry
from src.current_user import got_key
from src.config import get
from src import log
from src.data import get_parameters
from src.sos import cwd
from src.scraper import subscene
from src import file_manager as fm


def main() -> None:
    # initialising
    start = time.perf_counter()
    if got_key() is False:
        registry.add_context_menu()
        return exit(0)

    language, lang_abbr = get("language")
    precentage = get("percentage")
    param = get_parameters(cwd().lower(), lang_abbr)

    # log parameters
    log.parameters(param, language, lang_abbr, precentage)

    log.output("\n[Searching]")
    download_info = subscene.scrape(param, language, lang_abbr, precentage)
    if download_info is None:
        elapsed = time.perf_counter() - start
        log.output(f"Finished in {elapsed} seconds.\n\n")
        return

    # download results from scraper
    log.output("\n[Downloading]")
    for items in download_info:
        file_path, root_dl_url, current_num, total_num = items
        fm.download_zip(file_path, root_dl_url, current_num, total_num)

    # procsess downloaded files
    log.output("\n[Procsessing files]")
    fm.extract_zips(cwd(), ".zip")
    fm.clean_up(cwd(), ".zip")
    fm.rename_srts(f"{param.release}.srt", cwd(), f"{param.group}.srt", ".srt")
    fm.move_files(cwd(), f"{param.group}.srt", ".srt")
    print("\n\n")

    # finnishing up
    elapsed = time.perf_counter() - start
    log.output(f"Finished in {elapsed} seconds")


if __name__ == "__main__":
    main()
