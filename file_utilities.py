import bz2
import pickle
import _pickle as cPickle
import json
from pathlib import Path

def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding="utf-8")
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2, sort_keys=False, ensure_ascii=False)
    # Close the output file
    out_file.close()

def compressed_pickle(title, data):
    with bz2.BZ2File(title + ".pbz2", "wb") as f:
        cPickle.dump(data, f)


# Load any compressed pickle file
def decompress_pickle(file):
    data = bz2.BZ2File(file, "rb")
    return cPickle.load(data)

def get_countries():
    with open("list_of_countries.txt", "r") as fo:
        countries = [country.strip() for country in fo]

    return countries