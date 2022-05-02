import random
import json
import numpy as np

from src.agents.agent import MASAgent, MASPeriodicBehaviour, MASReceivingBehaviour
from src.utils.messages import create_message, create_template
import src.utils.constants as const

# currently unused (for visualization)
student_moving = {'from': [],
                  'to': []}


class StudentAgent(MASAgent):
    """
    StudentAgent class, extends MASAgent
    """

    def __init__(self, jid, password, start_delay, is_international, is_female, sim):
        super().__init__(jid)

        self.start_delay = start_delay
        self.waiting_time = 0
        self.total_waiting_time = 0
        self.num_applications = 0
        self.num_rooms_obtained = 0
        self.started = False
        self.has_room = False
        self.is_searching = True
        self.contract_almost_ends = False
        self.house_jid = None
        self.house_score = None
        self.house_attractiveness = 0
        self.has_applied = False
        self.applied_rooms = [

        ]
        self.questionnaire = {
            'personality_vector': [],
            'international': is_international,
            'is_female': is_female
        }
        self.sim = sim

    class RequestRoomListing(MASPeriodicBehaviour):
        """
        requests open room listings from listing agent and updates students waiting-time accordingly
        """
        def run(self):
            if self.agent.has_room and (self.agent.sim.ticks_passed % const.CHECK_COMP_EVERY_X == 0):
                msg = create_message(self.agent.house_jid, "request", {"student_jid": self.agent.identifier},
                                     {'request-type': 'house-score'})
                self.send(msg)
                return
            if not self.agent.is_searching:
                return
            if not self.agent.has_applied:
                msg = create_message("listing_agent@localhost",
                                     "request",
                                     "Do you have rooms available?",
                                     {"request-type": "listings"})
                self.send(msg)

            self.agent.waiting_time += 1
            self.agent.total_waiting_time += 1

    class ReceiveRoomContractProposal(MASReceivingBehaviour):
        """
        handles incoming contract proposals
        """
        def run(self, received_msg):
            proposal = json.loads(received_msg.body)
            proposal['questionnaire'] = self.agent.questionnaire

            if self.agent.has_room:
                msg = create_message(self.agent.house_jid, "request", {"student_jid": self.agent.identifier},
                                     {'request-type': 'contract-end'})
                self.send(msg)

            student_moving['from'].append(self.agent.house_jid)
            student_moving['to'].append(proposal['house_jid'])

            # accept contract proposal
            msg = create_message(str(received_msg.sender), "accept-proposal", proposal)
            self.send(msg)
            self.agent.has_room = True
            self.agent.is_searching = False
            self.agent.house_jid = proposal['house_jid']
            self.agent.house_attractiveness = proposal['house_attractiveness']
            self.agent.has_applied = False

            # cancel other applications
            for (house, room_id) in self.agent.applied_rooms:
                if proposal['room_id'] is room_id:
                    continue
                msg = create_message(house, "cancel-application", {'room_id': room_id})
                self.send(msg)
            self.agent.applied_rooms = []

            self.agent.num_rooms_obtained += 1
            template = create_template("inform", {"inform-type": "contract-ended"})
            self.agent.add_behaviour(self.ReceiveContractEnd(), template)

            template = create_template("inform", {"inform-type": "contract-almost-ends"})
            self.agent.add_behaviour(self.ReceiveAlmostContractEnd(), template)

        class ReceiveContractEnd(MASReceivingBehaviour):
            """
            handles incoming notice that rental contract has ended,
            updates own values accordingly
            """
            def run(self, received_msg):
                self.agent.has_room = False
                self.agent.is_searching = True
                self.agent.has_applied = False
                self.agent.waiting_time = 0
                self.agent.contract_almost_ends = False
                self.kill()

        class ReceiveAlmostContractEnd(MASReceivingBehaviour):
            """
            handles incoming notice that rental contract nears end,
            prompts student to start searching for new accommodation
            """
            def run(self, received_msg):
                self.agent.is_searching = True
                self.agent.contract_almost_ends = True
                self.kill()

    class ReceiveApplicationRejection(MASReceivingBehaviour):
        """
        handle the rejection of application
        """
        def run(self, received_msg):
            self.agent.has_applied = False
            received_rejection = json.loads(received_msg.body)
            self.agent.applied_rooms.remove((str(received_msg.sender), received_rejection['room_id']))

    class ReceiveHouseScore(MASReceivingBehaviour):
        """
        calculate matching score with current house,
        if below threshold, start searching for new room
        """
        def run(self, received_msg):
            proposal = json.loads(received_msg.body)
            self.agent.house_score = proposal['house_score']
            compatibility = const.calculate_dist(self.agent.questionnaire['personality_vector'], self.agent.house_score)
            if compatibility < .95:
                self.agent.is_searching = True

    class ReceiveRoomListings(MASReceivingBehaviour):
        """
        class to handle requested listings
        """

        def calc_compatibility(self, pers_vector, house_score):
            """
            function to calculate matching score with listed house
            :param pers_vector: student personality
            :param house_score: averaged house personality
            :return: calculated score
            """
            if house_score is not None:
                return const.calculate_dist(pers_vector, house_score)
            return 0

        def run(self, received_msg):

            # delay start of agent
            if self.agent.sim.ticks_passed <= self.agent.start_delay:
                self.agent.started = False
                return

            self.agent.started = True
            if not self.agent.is_searching:
                return
            received_listings = json.loads(received_msg.body)

            # currently unused, only apply to suitable houses (nationality)
            if self.agent.questionnaire['international']:
                received_listings = list(
                    filter(lambda listing: listing['accept_internationals'], received_listings))

            received_listings.sort(reverse=True, key=lambda listing: listing['attractiveness'] +
                                                                     self.calc_compatibility(
                                                                         self.agent.questionnaire['personality_vector'],
                                                                         listing["house_score"]))

            # do not move to less attractive house
            if self.agent.has_room and self.agent.is_searching and not self.agent.contract_almost_ends:
                received_listings = list(
                    filter(lambda listing: self.calc_compatibility(self.agent.questionnaire['personality_vector'],
                                                                   listing["house_score"]) > .96 and listing[
                                               'attractiveness'] >= self.agent.house_attractiveness + .05,
                           received_listings))

            # apply to houses/rooms
            applications_done = 0
            while applications_done < 3 and len(self.agent.applied_rooms) < 10 and len(received_listings) > 0:
                applications_done += 1
                room_nr = random.randint(0, int(len(received_listings) / 2))
                room = received_listings[room_nr]
                application = {"id": room["id"],
                               "housing_method": room["housing_method"],
                               "questionnaire": self.agent.questionnaire,
                               "waiting_time": self.agent.waiting_time}

                msg = create_message(room["house_jid"], "inform", json.dumps(application),
                                     {'inform-type': 'room_application'})
                self.agent.num_applications += 1
                self.agent.has_applied = True
                self.agent.applied_rooms.append((room["house_jid"], room["id"]))
                self.send(msg)

    def setup(self):
        """
        setup of student agent, add defined behaviours
        :return:
        """

        # values based on OCEAN-statistics for the Netherlands
        # Extraversion(M: 49.75 SD: 9.22)
        # Agreeableness(M: 46.08 SD: 8.77)
        # Conscientiousness(M: 43.91 SD: 10.90)
        # Neuroticism(M: 48.61 SD: 9.71)
        # Openness(M: 49.94 SD: 9.21)

        num_samples = 1
        desired_means = [49.75, 46.08, 43.91, 48.61, 49.94]
        desired_std_dev = [9.22, 8.77, 10.9, 9.71, 9.21]

        for i in range(5):
            samples = np.random.normal(loc=0.0, scale=desired_std_dev[i], size=1)
            final_samples = samples + desired_means[i]
            self.questionnaire['personality_vector'].append(final_samples[0] / 100)

        self.started = True
        self.has_room = False
        self.has_applied = False
        self.waiting_time = 0
        self.total_waiting_time = 0
        self.num_applications = 0

        self.add_behaviour(self.RequestRoomListing())

        template = create_template("inform", {"inform-type": "listing"})
        self.add_behaviour(self.ReceiveRoomListings(), template)

        template = create_template("propose", {"propose-type": "room-contract"})
        self.add_behaviour(self.ReceiveRoomContractProposal(), template)

        template = create_template("inform", {"inform-type": "application-rejection"})
        self.add_behaviour(self.ReceiveApplicationRejection(), template)

        template = create_template("inform", {"inform-type": "house-score"})
        self.add_behaviour(self.ReceiveHouseScore(), template)
