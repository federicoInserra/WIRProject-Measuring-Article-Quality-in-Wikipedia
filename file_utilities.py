import bz2
import pickle
import _pickle as cPickle
import json
from pathlib import Path
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import word_tokenize
import mwparserfromhell


def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding="utf-8")
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2, sort_keys=False, ensure_ascii=False)
    # Close the output file
    out_file.close()



def compressed_pickle(title, data):
    with bz2.BZ2File(title + ".pbz2", "wb") as f:
        cPickle.dump(data, f, protocol=4)

# Load any compressed pickle file
def decompress_pickle(file):
    data = bz2.BZ2File(file, "rb")
    return cPickle.load(data)


def get_countries():
    with open("list_of_countries.txt", "r") as fo:
        countries = [country.strip() for country in fo]

    return countries


def parse_text(text):
    return mwparserfromhell.parse(text).strip_code()


def get_revisions(country: str):
    path = f"countries/{country.lower()}"
    Path(path).mkdir(parents=True, exist_ok=True)
    return decompress_pickle(f"{path}/revisions.pbz2")


def filter_text(text):
    # Remove puntuaction
    tokenizer = RegexpTokenizer(r"\w+")
    string_text = "".join(text)
    cleantext = tokenizer.tokenize(string_text)
    # Remove stop words
    stop_words = set(stopwords.words("english"))
    filtered_text = [w for w in cleantext if not w in stop_words]
    return " ".join(filtered_text)
