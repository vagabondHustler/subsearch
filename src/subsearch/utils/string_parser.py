# compare two lists  with each other and return match in %
def pct_value(from_pc: str | int, from_browser: str | int) -> int:
    max_percentage = 100
    pc_list: list = mk_lst(from_pc)
    browser_list: list = mk_lst(from_browser)
    not_matching = list(set(pc_list) - set(browser_list))
    not_matching_value = len(not_matching)
    number_of_items = len(pc_list)
    percentage_to_remove = round(not_matching_value / number_of_items * max_percentage)
    pct = round(max_percentage - percentage_to_remove)

    return pct


# create list from string
def mk_lst(release: str | int):
    new: list = []
    qualities = ["720p", "1080p", "1440p", "2160p"]
    temp: list = release.split(".")

    for item in temp:
        if item not in qualities:
            new.append(item.lower())
    return new
