from agents.student_agent import *
from agents.listing_agent import *
from agents.house_agent import *
from agents.agent import MASSimulation

from agents.visualize_agent import *

students = []
houses = []


def setup_simulation(num_houses, num_students, percentage_accepting_international, percentage_international,
                     percentage_female, dist=[1, 0, 0]):
    """
    Setup of the Multi-Agent simulation

    :param num_houses: number of houses in simulation
    :param num_students: number of students in simulation
    :param percentage_accepting_international: percentage of houses that accept international students
    :param percentage_international: percentage of international students (currently unused)
    :param percentage_female: percentage of female students (currently unused)
    :param dist: [const.COOP, const.WAIT_LIST, const.RAND]
    list containing percentages of distribution methods (should add up to 1)
    :return: set-up simulation containing running agents
    """

    # initialization
    sim = MASSimulation()
    max_internationals = int(num_students * percentage_international)
    max_female = int(num_students * percentage_female)
    num_internationals = 0
    num_females = 0

    # setup of agents
    for i in range(0, num_students):
        is_female = False
        is_international = False

        if num_internationals < max_internationals:
            if bool(random.getrandbits(1)):
                is_international = True
                num_internationals += 1

        if num_females < max_female:
            if bool(random.getrandbits(1)):
                is_female = True
                num_females += 1

        student_agent = StudentAgent("student" + str(i) + "@localhost", "mas2021",
                                     random.randint(0, const.DEFAULT_RENT_PERIOD),
                                     is_international,
                                     is_female,
                                     sim)
        students.append(student_agent)
        sim.add_agent(student_agent)

    num_international_houses = 0
    houses_dist = [0, 0, 0]
    cur_meth = 0
    meths = [const.COOP, const.WAIT_LIST, const.RAND]

    for i in range(0, num_houses):
        if houses_dist[cur_meth] >= dist[cur_meth] * num_houses:
            cur_meth += 1
        houses_dist[cur_meth] += 1

        international = num_international_houses < percentage_accepting_international * num_houses
        house_agent = HouseAgent("house" + str(i) + "@localhost", "mas2021", random.randint(3, 7), meths[cur_meth],
                                 international)
        if international:
            num_international_houses += 1
        houses.append(house_agent)
        sim.add_agent(house_agent)

    # print setup to console and return simulation
    print(houses_dist)
    print("\n******************** SETUP COMPLETE ********************",
          "\nNum. of students", num_students,
          "\nMax Internationals", max_internationals,
          "\nMax female students", max_female,
          "\nInternationals:", num_internationals,
          "\nFemale students:", num_females,
          "\nHouses: ", num_houses, "(", num_international_houses, "international )",
          "\n********************************************************\n")
    return sim


if __name__ == "__main__":
    """
    Initialization of system and agents
    """

    # create listing agent
    list_agent = ListingAgent("listing_agent@localhost")

    # start simulation
    # num_houses, num_students, percentage_accepting_international, percentage_international, percentage_female
    sim = setup_simulation(8, 80, .6, 0, .5)

    # add listing- an visualization-agent to system
    sim.add_agent(list_agent)
    vis_agent = VisualizeAgent("visualize_agent@localhost", "mas2021", sim, students, houses, list_agent)
    sim.add_agent(vis_agent)

    sim.simulate()
