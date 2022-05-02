import json
import requests

"""
Currently unused, messaging via openfire database/service
"""


def create_openfire_user(username, password):
    url = "http://localhost:9090/plugins/restapi/v1/users"

    payload = json.dumps({
      "username": username,
      "password": password
    })
    headers = {
      'Authorization': '',
      'Content-Type': 'application/json'
    }

    requests.request("POST", url, headers=headers, data=payload)
