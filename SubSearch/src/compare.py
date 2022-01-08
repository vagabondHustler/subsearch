from dataclasses import dataclass


@dataclass
class Precentage:
    precentage: int


# compare two strings with each other and return match in %
def check(searched: str or int, against: str or int) -> Precentage:
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


# create list from string
def mk_lst(release: str or int) -> list:
    new: list = []
    qualities = ["720p", "1080p", "1440p", "2160p"]

    temp: list = release.split(".")

    for item in temp:
        if item not in qualities:
            new.append(item)
    return new


# check if strings are equal length
def is_bigger(searched: str or int, against: str or int) -> int:
    if len(searched) > len(against):
        answer = len(searched) - len(against)
        return answer
    elif len(searched) < len(against):
        answer = len(against) - len(searched)
        return answer


# compare two items
def compare(itemx: str or int, itemy: str or int) -> bool:
    if itemx.lower() == itemy.lower():
        return True
    return False
