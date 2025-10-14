# logic/scoring.py

mountain_categories = {
    "cat3": {"points": {1: 3, 2: 2, 3: 1, 0: 0}},
    "cat2": {"points": {1: 5, 2: 3, 3: 1, 0: 0}},
    "cat1": {"points": {1: 10, 2: 7, 3: 5, 4: 3, 5: 1, 0: 0}},
    "HC":   {"points": {1: 20, 2: 14, 3: 10, 4: 7, 5: 3, 6: 1, 0: 0}},
}

sprint_categories = {
    "S":  {1: 10, 2: 7, 3: 5, 4: 3, 5: 1, 0: 0},
    "SF": {1: 20, 2: 14, 3: 10, 4: 6, 5: 2, 0: 0},
    "MF": {1: 10, 2: 7, 3: 5, 4: 3, 5: 1, 0: 0},
}

def calculate_points(segment_category, placement):
    if segment_category in mountain_categories:
        return mountain_categories[segment_category]["points"].get(placement, 0)
    if segment_category in sprint_categories:
        return sprint_categories[segment_category].get(placement, 0)
    return 0
