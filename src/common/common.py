import json
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def open_text(file):
    with open(file, 'r') as fp:
        lines = fp.readlines()
    lines_stripped = [line.rstrip() for line in lines]
    return lines_stripped

def open_json(file):
    with open(file, "r") as fp:
        output = json.load(fp)
    return output

def save_json(file, dictionary):
    with open(file, "w") as fp:
        json.dump(dictionary, fp, indent=4)

def info(text):
    logging.info(text)