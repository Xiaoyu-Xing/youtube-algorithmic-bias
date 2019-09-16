import json


def read_json(path):
    with open(path) as f:
        jfile = json.load(f)
    return jfile, len(jfile), type(jfile)