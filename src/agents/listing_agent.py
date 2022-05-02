from src.agents.agent import MASReceivingBehaviour, MASAgent
from src.utils.messages import *


class ListingAgent(MASAgent):
    """
    ListingAgent class, extends general MASAgent
    """

    listings = {}

    class ReceiveListingRequest(MASReceivingBehaviour):
        """
        handles incoming requests to publish listings
        responds with up-to date room listings
        """
        def run(self, received_msg):
            msg = create_message(str(received_msg.sender), "inform", json.dumps(list(self.agent.listings.values())),
                                 {'inform-type': 'listing'})
            self.send(msg)

    class ReceiveListingRemovalRequest(MASReceivingBehaviour):
        """
        handles requests to remove listings
        """
        def run(self, received_msg):
            room_id = json.loads(received_msg.body)['room_id']
            if room_id in self.agent.listings.keys():
                del self.agent.listings[room_id]

    class ReceiveListing(MASReceivingBehaviour):
        """
        handles incoming new listings, addsa them to list
        """
        def run(self, received_msg):
            received_listing = json.loads(received_msg.body)
            received_listing['house_jid'] = str(received_msg.sender)
            self.agent.listings[received_listing['id']] = received_listing

    def setup(self):
        """
        setup of listing agent with defined behaviours
        :return:
        """
        print("ListingAgent: ListingAgent started")
        template = create_template("request", {"request-type": "listings"})
        self.add_behaviour(self.ReceiveListingRequest(), template)

        template = create_template("inform", {"inform-type": "listing"})
        self.add_behaviour(self.ReceiveListing(), template)

        template = create_template("request", {"request-type": "remove-listing"})
        self.add_behaviour(self.ReceiveListingRemovalRequest(), template)
