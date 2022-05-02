import random

import src.utils.constants as const
from datetime import datetime

all_agents = {}
periodic_behaviours = []


class MASAgent:
    """
    general agent implementation
    """

    def __init__(self, identifier):
        """
        constructor for agent class
        :param identifier: identifying string
        """
        self.behaviours = []
        self.templates = []
        self.identifier = identifier
        self.sim = None

    def setup(self):
        pass

    def add_behaviour(self, behavior, template=None):
        """
        function to add behaviours to the agent
        :param behavior: behaviour to be added
        :param template: the used messaging/behaviour template
        """
        self.behaviours.append(behavior)
        if template is not None:
            self.templates.append((template, behavior))
        behavior.agent = self

    def remove_behaviour(self, behavior):
        """
        function to remove an agent behaviour
        :param behavior: behaviour to be removed
        :return:
        """
        self.behaviours.remove(behavior)
        for index, (template, behav) in enumerate(self.templates):
            if behavior == behav:
                del self.templates[index]
                return

    def send(self, message):
        """
        function for sending messages to facilitate agent-to-agent communication
        :param message: message to be sent
        """
        sent = False
        to = str(message.to)
        message.sender = self.identifier
        if to in self.sim.all_agents.keys():
            agent = self.sim.all_agents[to]
            for template, behavior in agent.templates:
                if template.match(message):
                    sent = True
                    behavior.run(message)
            if sent is False:
                print("Didn't send message to '" + to + "' no behaviour with a match")
        else:
            print("Can't send message to '" + to + "' it doesn't exist")


class MASBehaviour:
    """
    class for general agent behaviour
    """

    def __init__(self):
        self.agent = None
        self.exit_code = ""
        self.periodic = False

    def send(self, msg):
        self.agent.send(msg)

    def kill(self):
        self.agent.remove_behaviour(self)


# currently unused
class MASReceivingBehaviour(MASBehaviour):
    def __init__(self):
        super().__init__()

    def run(self, msg):
        raise NotImplementedError("Please Implement this method")


class MASPeriodicBehaviour(MASBehaviour):
    """
    extends MASBehaviour, implements basic periodic behaviour
    """

    def __init__(self):
        super().__init__()
        self.periodic = True


class MASSimulation:
    """
    Simulation class, manages agents and timed behaviour (ticks)
    """

    def __init__(self):
        self.ticks_passed = 0
        self.periodic_behaviours = []
        self.all_agents = {}
        self.id = datetime.now().strftime('%Y%m%d-%H%M%S')

    def add_agent(self, agent):
        """
        function to add an exiting agent to the simulation
        :param agent: agent to be added
        """
        self.all_agents[agent.identifier] = agent
        agent.sim = self

    def simulate(self):
        """
        main simulation function:
            starts up agents and runs simulation with defined parameters
            manages tick-time for periodic behaviours
        """
        print("Setting up agents")
        for agent in self.all_agents.values():
            agent.setup()

        print("Simulation started")
        while self.ticks_passed < const.SIMULATION_DURATION:  # ticks

            self.ticks_passed += 1
            print("TICK", self.ticks_passed)
            agents = list(self.all_agents.values())
            random.shuffle(agents)
            for agent in agents:
                for behaviour in agent.behaviours:
                    if not behaviour.periodic:
                        continue
                    behaviour.run()
                    if behaviour.exit_code is not "":
                        behaviour.agent.remove_behaviour(behaviour)
