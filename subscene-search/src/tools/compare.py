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
        for ga in range(greater_answer):
            searched.append("_None")
    elif len(searched) > len(search_result):
        for ga in range(greater_answer):
            search_result.append("_None")
    else:
        pass

    for x, y in zip(searched, search_result):
        if compare(x, y) is True:
            match += 1
        else:
            pass

    tot = len(searched)
    precentage = round((match / tot) * 100)

    return Precentage(precentage)


def mk_lst(x: str) -> list:
    x: list = x.split(".")
    x1 = x[-1].split("-")

    for item in x1:
        x.append(item)
    return x


def is_bigger(searched, search_result) -> int:
    if len(searched) > len(search_result):
        answer = len(searched) - len(search_result)
        return answer
    elif len(searched) < len(search_result):
        answer = len(search_result) - len(searched)
        return answer


def compare(x, y) -> bool:
    if x.lower() == y.lower():
        return True
    else:
        return False
