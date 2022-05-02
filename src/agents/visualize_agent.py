from matplotlib import pyplot as plt
import src.utils.constants as const
import json
import time
import numpy as np
from PIL import Image

from src.agents.agent import MASAgent, MASPeriodicBehaviour

imgs = []


class VisualizeAgent(MASAgent):
    """
    Visualization Agent that extends MASAgent
    construct to allow integration into setup and time-management of simulation
    """
    class Visualize(MASPeriodicBehaviour):
        def run(self):
            students = self.agent.students
            houses = self.agent.houses

            student_data = []
            house_data = []
            time_t = time.time()

            # Create a 1024x1024x3 array of 8 bit unsigned integers
            im = Image.new('RGB', (len(students) + 10, 50))

            i = 0
            for student in students:
                if student.started:
                    color = (255, 0, 0) if student.questionnaire['international'] else (0, 255, 0)
                    if not student.has_room:
                        color = (int(color[0] / 3), int(color[1] / 3), int(color[2] / 3))
                    im.putpixel((i, 5), color)

                    # (255, 255, 255) - white - International and a room
                    # (255, 0, 255) - purple - Non-internation and a room
                    # (255, 0, 0) - red - Non-internation and a room
                i += 1
                serialized_data = {
                    "wt": student.waiting_time,
                    "s": student.started,
                    "hr": student.has_room,
                    "twt": student.total_waiting_time,
                    "na": student.num_applications,
                    "nro": student.num_rooms_obtained,
                    "q": student.questionnaire
                }
                student_data.append(serialized_data)

            i = 0
            houses.sort(reverse=True, key=lambda h: h.attractiveness)

            for house in houses:
                rooms = []
                i += 1
                residents = 0
                sum_avg_personality = [0] * 5

                for room in house.rooms.values():
                    color = (255, 255, 255) if room["resident_jid"] is not None else (100, 100, 100)
                    if room["listed"]:
                        color = (140, 140, 0)
                    im.putpixel((i * 2, 10 + len(rooms)), color)
                    serialized_data = {
                        "id": room["id"],
                        "q": room["questionnaire"]
                    }
                    rooms.append(serialized_data)

                    if room["questionnaire"] is None:
                        continue

                    sum_avg_personality = np.add(sum_avg_personality, room["questionnaire"]['personality_vector'])
                    residents += 1

                house_matching_score = const.calculate_house_matching_score(house)
                avg_personality = None
                if residents > 0:
                    avg_personality = np.true_divide(sum_avg_personality, residents).tolist()

                house_data.append({
                    'ms': house_matching_score,
                    'at': house.appl_type,
                    'a': house.attractiveness,
                    'ai': house.accept_internationals,
                    'avg_p': avg_personality})

            imgs.append(im)

            # with open('test.png', 'wb') as f:
            #     im.save(f)
            #     f.close()

            if self.agent.sim.ticks_passed % const.SAVE_DATA_EVERY_X == 0 and self.agent.sim.ticks_passed >= const.WARM_UP_TICKS:
                with open("data-" + self.agent.sim.id + ".json", 'a+') as f:
                    tick = self.agent.sim.ticks_passed
                    if tick == const.WARM_UP_TICKS:
                        f.write("[")
                    # indent=2 is not needed but makes the file human-readable
                    json.dump({'tick': tick, 'students': student_data, 'houses': house_data}, f, indent=2)
                    if tick == const.SIMULATION_DURATION:
                        f.write("]")
                        with open('data-' + self.agent.sim.id + '.gif', 'wb') as f:
                            im.save(f, save_all=True, append_images=imgs, optimize=False, duration=100, loop=0)
                            f.close()
                    else:
                        f.write(",")

    def __init__(self, jid, password, sim, students, houses, list_agent):
        super().__init__(jid)
        self.step = 0
        self.students = students
        self.houses = houses
        self.list_agent = list_agent
        self.sim = sim
        self.all_data = []

    def setup(self):
        plt.axis()
        self.add_behaviour(self.Visualize())

