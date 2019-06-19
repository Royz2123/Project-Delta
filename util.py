import json

FILENAME = "./credentials.json"


def get_creds():
    d = json.load(open(FILENAME, "r"))
    return d["username"], d["password"]


def set_creds(username, password):
    d = {
        "username" : username,
        "password" : password,
    }
    json.dump(d, open(FILENAME, "w+"))
