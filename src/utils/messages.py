import json

from spade.template import Template
from spade.message import Message

"""
Messaging implementation to avoid external messaging as needed by SPADE
"""


def create_template(performative, meta_data=None):
    """
    function to define messaging templates
    :param performative: performative identifier
    :param meta_data: additional metadata
    :return: template
    """
    if meta_data is None:
        meta_data = {}

    template = Template()
    template.set_metadata("performative", performative)
    template.set_metadata("ontology", "studentHousing")  # Set the ontology of the message content
    template.set_metadata("language", "OWL-S")  # Set the language of the message content
    for key in meta_data:
        template.set_metadata(key, meta_data[key])

    return template


def create_message(to, performative, body, meta_data=None):
    """
    function for creating a message
    :param to: receiving agent
    :param performative: template, such as inform, request etc
    :param body: message content
    :param meta_data: additional metadata
    :return: created message
    """
    if meta_data is None:
        meta_data = {}

    if type(body) != str:
        body = json.dumps(body)

    msg = Message(to=to)  # Instantiate the message
    msg.set_metadata("performative", performative)  # Set the "inform" FIPA performative
    msg.set_metadata("ontology", "studentHousing")  # Set the ontology of the message content
    msg.set_metadata("language", "OWL-S")  # Set the language of the message content

    for key in meta_data:
        msg.set_metadata(key, meta_data[key])

    msg.body = body  # Set the message content
    return msg
