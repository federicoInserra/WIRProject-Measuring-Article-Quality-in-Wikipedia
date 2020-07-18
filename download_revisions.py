import diff_match_patch as dmp_module
import bz2
import pickle
import _pickle as cPickle
import json
from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import word_tokenize

# import asyncio
# import aiohttp
# from aiohttp import ClientSession, ClientConnectorError
# TODO: Async download https://stackoverflow.com/a/57689101


nltk.download("stopwords")
nltk.download("punkt")


@dataclass
class Change:
    revid: int
    added: str
    removed: str

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


@dataclass
class Revision:
    revid: int
    user: str
    text: str


# Pickle a file and then compress it into a file with extension
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


def download_revisions(data, country, path):

    S = requests.Session()
    print(f"Downloading revisions for country: {country}")
    URL = "https://en.wikipedia.org/w/api.php"
    revisions_json = []
    for revision in data[country][-200:]:

        rev_object = {}
        revid = revision["id"]
        print(f"Downloading rev {revid}")
        params = {"action": "parse", "oldid": revid, "format": "json"}
        R = S.get(url=URL, params=params)
        DATA = R.json()
        clear_text = clean_html(DATA["parse"]["text"]["*"])
        rev_object["user"] = revision["user"]["name"]
        rev_object["timestamp"] = revision["timestamp"]
        rev_object["revid"] = revid
        rev_object["text"] = clear_text

        revisions_json.append(rev_object)

    compressed_pickle(f"{path}/revisions", revisions_json)


def construct_text(words):
    new_text = ""
    for w in words:
        new_text += w + " "
    return new_text


def diff(path):

    print("Computing the diff between revisions")
    differences = []
    diff = {}
    revisions = decompress_pickle(f"{path}/revisions.pbz2")

    i = len(revisions) - 1
    old_rev = revisions[i]
    i -= 1
    diff["revid"] = old_rev["revid"]
    diff["timestamp"] = old_rev["timestamp"]
    diff["user"] = old_rev["user"]
    diff["added"] = []
    diff["removed"] = []
    differences.append(diff)

    while i >= 0:
        diff = {}
        new_rev = revisions[i]
        new_text = construct_text(new_rev["text"])
        old_text = construct_text(old_rev["text"])

        removed_text, added_text = find_diff(old_text, new_text)

        diff["revid"] = new_rev["revid"]
        diff["timestamp"] = new_rev["timestamp"]
        diff["user"] = new_rev["user"]
        diff["added"] = added_text
        diff["removed"] = removed_text

        differences.append(diff)
        old_rev = new_rev
        i -= 1

    compressed_pickle(f"{path}/differences", differences)


def find_diff(document1, document2):
    dmp = dmp_module.diff_match_patch()
    changes = dmp.diff_main(document1, document2, checklines=True, deadline=20)
    dmp.diff_cleanupSemantic(changes)
    removed_text = ""
    added_text = ""

    for op, change in changes:
        if op == -1:
            removed_text += change

        if op == 1:
            added_text += change

    return word_tokenize(removed_text), word_tokenize(added_text)


def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding="utf-8")
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2, sort_keys=False, ensure_ascii=False)
    # Close the output file
    out_file.close()


def clean_html(raw_html):

    # Clean the text from the html sintax
    cleantext = BeautifulSoup(raw_html, "html.parser").text

    cleantext = filter_text(cleantext)

    return cleantext


def filter_text(text):
    # Remove puntuaction
    tokenizer = RegexpTokenizer(r"\w+")
    cleantext = tokenizer.tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    filtered_text = [w for w in cleantext if not w in stop_words]

    return filtered_text


if __name__ == "__main__":
    # TODO: Il codice raccoglie tutte le differenze tra le revisioni e se le salva,
    # manca la parte finale, in cui calcolare i punteggi degli utenti e dei documenti
    try:
        with open("all_revisions.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    except Exception as e:
        print("Error: 'all_revisions.json' file not present")
        exit(-1)

    countries = get_countries()
    for country in countries:
        try:

            path = f"countries/{country.lower()}"
            Path(path).mkdir(parents=True, exist_ok=True)
            exists = Path.exists(Path(f"{path}/revisions.pbz2"))
            if exists:
                print("Revisions file found!")
                diff(path)
            else:
                print("Revisions not found, downloading...")
                download_revisions(data, country, path)
                diff(path)
        
        except Exception as e:
            print(e)
            pass

