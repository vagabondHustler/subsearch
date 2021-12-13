from dataclasses import dataclass

@dataclass
class Precentage:
    precentage: int


def check(searched: str, against: str) -> Precentage:
    match = 0
    searched: list = mk_lst(searched)
    against: list = mk_lst(against)
    greater_answer = is_bigger(searched, against)

    if len(searched) < len(against):
        for _ga in range(greater_answer):
            searched.append("_None")
    elif len(searched) > len(against):
        for _ga in range(greater_answer):
            against.append("_None")

    for item_x, item_y in zip(searched, against):
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


def is_bigger(searched, against) -> int:
    if len(searched) > len(against):
        answer = len(searched) - len(against)
        return answer
    elif len(searched) < len(against):
        answer = len(against) - len(searched)
        return answer


def compare(searched, against) -> bool:
    if searched.lower() == against.lower():
        return True
    return False
