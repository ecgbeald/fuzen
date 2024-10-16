from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def similarity_sum(a: str, bs: list[str]):
    return sum([similarity(a, b) for b in bs])

def add_to_error_list(error):
    current_errors = []
    if current_errors < 20:
        current_errors.append(error)
        return
    all_errors = current_errors.copy().append(error)
    # calculate the most similar
    similarites = sorted([(similarity_sum(error, all_errors), error) for error in all_errors], key=lambda x: x[0])
    similarites.pop()
    current_errors = similarites
