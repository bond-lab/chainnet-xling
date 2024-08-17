import csv
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

def save_csv(file, all_lines, encoding=None):
    ftype = file[-4:]
    delimiter = ''
    if ftype == '.tsv':
        delimiter = '\t'
    elif ftype == '.csv':
        delimiter = ','
    else:
        # update
        print("Invalid file extension: {}".format(file))
        exit()
    with open(file, 'w', encoding=encoding) as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=all_lines[0].keys(), delimiter=delimiter,
                                     quoting=csv.QUOTE_NONE, escapechar='\\')
        dict_writer.writeheader()
        dict_writer.writerows(all_lines)
    return


def info(text):
    logging.info(text)