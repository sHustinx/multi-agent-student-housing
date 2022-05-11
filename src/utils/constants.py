import numpy as np

"""
Defines constants and default formulas used in the simulation
"""

COOP = "cooptation"
RAND = "random_assignment"
WAIT_LIST = "waiting_list"

"""
SETUP SIMULATION
"""

NUMBER_STUDENTS = 50
NUMBER_HOUSES = 4
DISTR_METHODS = [1, 0, 0]

DEFAULT_APPLICATION_DAYS = 2
EXTRA_COOP_DAYS = 2
DEFAULT_RENT_PERIOD = 104
SIMULATION_DURATION = 52 * 10
SAVE_DATA_EVERY_X = 1
CHECK_COMP_EVERY_X = 10
WARM_UP_TICKS = 1

"""
FORMULAS
"""


def dist(x, y):
    """
    calculates distance between two vectors
    :param x: vector x
    :param y: vector y
    :return: normalized distance
    """
    squares = [abs(p - q) for p, q in zip(x, y)]
    return sum(squares) / len(squares)


def calculate_dist(questionnaire1, questionnaire2):
    """
        function to calculate distance between two personality vectors
        :param questionnaire1:
        :param questionnaire2:
        :return: normalized distance
        """
    distance = dist(questionnaire1,
                    questionnaire2)
    return 1 - distance


def calculate_house_matching_score(house):
    """
    function ot calculate average distance of all roommates within a house
    :param house: house to be calculated with
    :return: averaged distance for all housemates
    """
    residents = 0
    sum_match_score = 0

    for room in house.rooms.values():
        if room["questionnaire"] is None:
            continue

        residents += 1
        roommates_score = 0
        roommates = 0

        for roommate in house.rooms.values():
            if roommate["id"] is room["id"] or roommate["questionnaire"] is None:
                continue
            roommates += 1
            roommates_score += calculate_dist(room["questionnaire"]["personality_vector"],
                                              roommate["questionnaire"]["personality_vector"])
        if roommates > 0:
            sum_match_score += roommates_score / roommates

    if residents > 1:
        return sum_match_score / residents

    return None


def calc_avg_personality(house):
    """
    function to calculate average personality of roommates
    :param house: house to be calculated with
    :return: average personality vector
    """
    sum_avg_personality = [0] * 5
    residents = 0

    for room in house.rooms.values():
        if room["questionnaire"] is None:
            continue

        sum_avg_personality = np.add(sum_avg_personality, room["questionnaire"]['personality_vector'])
        residents += 1

    avg_personality = None
    if residents > 0:
        avg_personality = np.true_divide(sum_avg_personality, residents).tolist()

    return avg_personality
