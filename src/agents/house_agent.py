import random
import uuid

import src.utils.constants as const
from src.agents.agent import MASAgent, MASPeriodicBehaviour, MASReceivingBehaviour
from src.utils.messages import *


def get_application_days(housing_method):
    """
    function to return remaining application days
    :param housing_method: applied distribution method
    :return: number of remaining open application days
    """
    return const.DEFAULT_APPLICATION_DAYS + (const.EXTRA_COOP_DAYS if housing_method == const.COOP else 0)


class HouseAgent(MASAgent):
    """
    HouseAgent class, extends general MASAgent
    """
    def __init__(self, jid, password, num_rooms, appl_type, accept_internationals=False):
        super().__init__(jid)
        self.rooms = {}
        self.accept_internationals = accept_internationals
        self.appl_type = appl_type
        self.attractiveness = random.uniform(0, 1)
        self.house_score = None
        for room in range(num_rooms):
            new_room = {
                'id': str(uuid.uuid1()),
                'resident_jid': None,
                'questionnaire': None,
                'listed': False,
                'application_in_process': False,
                'housing_method': appl_type,
                'applicants': [],
                'application_days_left': get_application_days(appl_type),
                'contract_days_left': 0
            }
            self.rooms[new_room['id']] = new_room

    class HouseUpdate(MASPeriodicBehaviour):
        """
        HouseUpdate class to manage periodic behaviours
        """

        def post_listings(self):
            """
            function to post free rooms as listings to the listing agent
            """
            for room_id in self.agent.rooms:
                room = self.agent.rooms[room_id]
                if room['listed'] or room['application_in_process'] or room['resident_jid'] is not None:
                    continue

                self.agent.house_score = const.calc_avg_personality(self.agent)

                msg = create_message("listing_agent@localhost",
                                     "inform",
                                     json.dumps({'id': room_id, 'housing_method': room['housing_method'],
                                                 'accept_internationals': self.agent.accept_internationals,
                                                 'attractiveness': self.agent.attractiveness,
                                                 'house_score': self.agent.house_score}),
                                     {'inform-type': 'listing'})
                self.agent.rooms[room_id]['listed'] = True
                self.send(msg)

        def run(self):
            """
            main house-function to update contracts and listings
            """
            for room_id in self.agent.rooms:
                room = self.agent.rooms[room_id]
                if room['resident_jid'] is not None:
                    room['contract_days_left'] -= 1
                    if room['contract_days_left'] == 4:
                        self.on_warn_student(room)
                    if room['contract_days_left'] <= 0:
                        self.on_rent_period_end(room)
                    continue

                if room['listed'] and not room['application_in_process'] and room['resident_jid'] is None:
                    if room['application_days_left'] == const.EXTRA_COOP_DAYS and len(room['applicants']) > 0 and len(
                            room['applicants']) <= 25:
                        msg = create_message("listing_agent@localhost", "request", {'room_id': room_id},
                                             {'request-type': 'remove-listing'})
                        self.send(msg)
                    room['application_days_left'] -= 1

                    if room['application_days_left'] <= 0:
                        self.on_application_end(room)
            self.post_listings()

        def on_application_end(self, room):
            """
            function to manage the end of application,
            requests a removal of the house listing and picks best applicant according to distribution method,
            sends a rejection ot the remaining applicants
            :param room: the room to be rented
            :return:
            """

            # request removal of listing and manage changed status
            room_id = room['id']
            if len(room['applicants']) == 0:
                return
            room['application_in_process'] = True
            msg = create_message("listing_agent@localhost", "request", {'room_id': room_id},
                                 {'request-type': 'remove-listing'})
            self.send(msg)
            room['listed'] = False
            room['application_days_left'] = get_application_days(room['housing_method'])

            chosen_applicant = room['applicants'][0]
            is_first_coop = room['housing_method'] == const.COOP and len(
                [i for i in self.agent.rooms.values() if i['resident_jid'] is not None]) == 0

            if room['housing_method'] == const.RAND or is_first_coop:
                # if method  is random assignment or if house is empty -> choose rand. applicant
                chosen_applicant = random.choice(room['applicants'])
            elif room['housing_method'] == const.WAIT_LIST:
                # select applicant with highest waiting time
                chosen_applicant = max(room['applicants'], key=lambda x: x['application']['waiting_time'])
            elif room['housing_method'] == const.COOP and len(room['applicants']) > 1:
                # select best-fitting housemate for co-optation
                highest_match_score = 0
                for applicant in room['applicants']:
                    match_score_sum = 0
                    housemates = 0
                    # select matching score with housemates for each applicant
                    for housemate_room in self.agent.rooms.values():
                        if housemate_room['resident_jid'] is None:
                            continue
                        match_score = const.calculate_dist(housemate_room['questionnaire']['personality_vector'],
                                                                  applicant['application']['questionnaire']['personality_vector'])
                        match_score_sum += match_score
                        housemates += 1
                    average_match_score = match_score_sum / housemates
                    # select best fit
                    if average_match_score > highest_match_score:
                        highest_match_score = average_match_score
                        chosen_applicant = applicant

            # send rejection to students that were not chosen
            applicants = list(room['applicants'])
            for applicant in applicants:
                if applicant['student_jid'] is chosen_applicant["student_jid"]:
                    continue
                rejected_msg = create_message(applicant["student_jid"], "inform", {'room_id': room_id},
                                              {'inform-type': 'application-rejection'})
                self.send(rejected_msg)

            # propose a rental contract to chosen student
            if chosen_applicant is not None:
                proposed_contract = {
                    'room_id': room['id'],
                    'rent_period': const.DEFAULT_RENT_PERIOD,
                    'house_jid': self.agent.identifier,
                    'house_attractiveness': self.agent.attractiveness
                }

                proposal_msg = create_message(chosen_applicant["student_jid"], "propose", proposed_contract,
                                              {'propose-type': 'room-contract'})
                self.send(proposal_msg)

        def on_rent_period_end(self, room):
            """
            function to end the rental agreement
            :param room: room to be updated
            """

            # inform tenant that rental period has ended
            rent_ended_msg = create_message(room["resident_jid"], "inform", {},
                                            {'inform-type': 'contract-ended'})

            # remove tenant
            room['resident_jid'] = None
            room['questionnaire'] = None
            room['applicants'] = []
            room['application_days_left'] = get_application_days(room['housing_method'])
            room['contract_days_left'] = 0

            # recalculate the avg. house vector
            self.agent.house_score = const.calc_avg_personality(self.agent)

            self.send(rent_ended_msg)

        def on_warn_student(self, room):
            """
            function to warn tenant that their rental agreement will end soon
            :param room: rented room
            """
            rent_ended_msg = create_message(room["resident_jid"], "inform", {},
                                            {'inform-type': 'contract-almost-ends'})
            self.send(rent_ended_msg)

    class ReceiveAcceptedProposal(MASReceivingBehaviour):
        """
        reacts to students accepted rental contract, updates room accordingly
        """
        def run(self, received_msg):
            proposal = json.loads(received_msg.body)
            self.agent.rooms[proposal['room_id']]['application_in_process'] = False
            self.agent.rooms[proposal['room_id']]['applicants'] = []
            self.agent.rooms[proposal['room_id']]['resident_jid'] = str(received_msg.sender)
            self.agent.rooms[proposal['room_id']]['questionnaire'] = json.loads(received_msg.body)[
                'questionnaire']
            self.agent.rooms[proposal['room_id']]['contract_days_left'] = const.DEFAULT_RENT_PERIOD
            self.agent.house_score = const.calc_avg_personality(self.agent)  # recalculate avg. house vector

    class ReceiveCancelApplication(MASReceivingBehaviour):
        """
        reacts to message of applicants that retract their application
        removes applicant from list
        """
        def run(self, received_msg):
            cancellation = json.loads(received_msg.body)
            room = self.agent.rooms[cancellation['room_id']]
            room['applicants'] = list(
                filter(lambda x: x['student_jid'] != str(received_msg.sender), room['applicants']))

    class ReceiveHouseScore(MASReceivingBehaviour):
        """
        informs residents of current house matching score
        """
        def run(self, received_msg):
            proposal = json.loads(received_msg.body)
            msg = create_message(proposal['student_jid'], "inform", {"house_score": self.agent.house_score},
                                 {'inform-type': 'house-score'})

            self.send(msg)

    class ReceiveContractEnd(MASReceivingBehaviour):
        """
        handles residents moving out
        """
        def run(self, received_msg):
            proposal = json.loads(received_msg.body)

            room = None
            for r in self.agent.rooms.values():
                if r['resident_jid'] == proposal['student_jid']:
                    room = r
            rent_ended_msg = create_message(room["resident_jid"], "inform", {},
                                            {'inform-type': 'contract-ended'})

            room['resident_jid'] = None
            room['questionnaire'] = None
            room['applicants'] = []
            room['application_days_left'] = get_application_days(room['housing_method'])
            room['contract_days_left'] = 0

            self.agent.house_score = const.calc_avg_personality(self.agent)  # recalculate avg. house vector
            self.send(rent_ended_msg)

    class ReceiveRoomApplications(MASReceivingBehaviour):
        """
        handles incoming applications to posted room listings
        """
        def run(self, received_msg):
            received_application = json.loads(received_msg.body)
            room = self.agent.rooms[received_application["id"]]

            if room['resident_jid'] is not None or room['application_in_process']:
                rejected_msg = create_message(str(received_msg.sender), "inform",
                                              {'room_id': received_application['id']},
                                              {'inform-type': 'application-rejection'})
                self.send(rejected_msg)
                return

            # inform students of received application
            room = self.agent.rooms[received_application["id"]]
            room['applicants'].append(
                {'student_jid': str(received_msg.sender), 'application': received_application})

            # request a removal of the listing after more than 25 applications
            if len(room['applicants']) > 25:
                msg = create_message("listing_agent@localhost", "request", {'room_id': received_application["id"]},
                                     {'request-type': 'remove-listing'})
                self.send(msg)
                room['listed'] = False

    def setup(self):
        """
        setup of the house agent, initialization of defined behaviours
        """
        print("HouseAgent: HouseAgent started")

        template = create_template("inform", {"inform-type": "room_application"})
        self.add_behaviour(self.ReceiveRoomApplications(), template)

        template = create_template("accept-proposal")
        self.add_behaviour(self.ReceiveAcceptedProposal(), template)

        template = create_template("cancel-application")
        self.add_behaviour(self.ReceiveCancelApplication(), template)

        template = create_template("request", {"request-type": "house-score"})
        self.add_behaviour(self.ReceiveHouseScore(), template)

        template = create_template("request", {"request-type": "contract-end"})
        self.add_behaviour(self.ReceiveContractEnd(), template)

        self.add_behaviour(self.HouseUpdate())
