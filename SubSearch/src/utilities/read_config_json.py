from src.utilities.local_paths import root_directory
from src.utilities.read_parameters import read_data


# get said value(s) from config.json
def get(output: str):
    config_json = read_data(root_directory("data", "config.json"))

    def languages():
        return config_json.languages

    def oter_language():
        language = config_json.language
        lang, lang_abbr = language.split(", ")
        return lang, lang_abbr
    
    def other_languages():
        return config_json.other_languages

    def hearing_impaired():
        return config_json.hearing_impaired

    def percentage():
        return config_json.percentage_pass

    def cm_icon():
        return config_json.context_menu_icon

    def download_window():
        return config_json.show_download_window

    def terminal_focus():
        return config_json.terminal_focus

    def video_ext():
        return config_json.video_ext

    if output == "language":
        return oter_language()
    if output == "languages":
        return languages()
    if output == "other_languages":
        return other_languages()
    if output == "hearing_impaired":
        return hearing_impaired()
    if output == "percentage":
        return percentage()
    if output == "cm_icon":
        return cm_icon()
    if output == "show_download_window":
        return download_window()
    if output == "terminal_focus":
        return terminal_focus()
    if output == "video_ext":
        return video_ext()
