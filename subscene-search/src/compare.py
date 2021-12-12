from dataclasses import dataclass

@dataclass
class Precentage:
    precentage: int


def check(searched: str, search_result: str) -> Precentage:
    match = 0
    searched: list = mk_lst(searched)
    search_result: list = mk_lst(search_result)
    greater_answer = is_bigger(searched, search_result)

    if len(searched) < len(search_result):
        for _ga in range(greater_answer):
            searched.append("_None")
    elif len(searched) > len(search_result):
        for _ga in range(greater_answer):
            search_result.append("_None")

    for item_x, item_y in zip(searched, search_result):
        if compare(item_x, item_y):
            match += 1

    tot = len(searched)
    precentage = round((match / tot) * 100)

    return Precentage(precentage)


def mk_lst(release: str) -> list:
    new: list = []
    qualities = ["720p", "1080p", "1440p", "2160p"]

    temp: list = release.split(".")

    for item in temp:
        if item not in qualities:
            new.append(item)
    return new


def is_bigger(searched, search_result) -> int:
    if len(searched) > len(search_result):
        answer = len(searched) - len(search_result)
        return answer
    elif len(searched) < len(search_result):
        answer = len(search_result) - len(searched)
        return answer


def compare(item_x, item_y) -> bool:
    if item_x.lower() == item_y.lower():
        return True
    return False
