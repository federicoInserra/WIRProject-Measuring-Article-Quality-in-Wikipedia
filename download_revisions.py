import diff_match_patch as dmp_module
import bz2
import pickle
import _pickle as cPickle
import json
from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# import asyncio
# import aiohttp
# from aiohttp import ClientSession, ClientConnectorError
# TODO: Async download https://stackoverflow.com/a/57689101


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
    for revision in data[country][-5:]:

        revid = revision['id']
        print(f"Downloading rev {revid}")
        params = {"action": "parse", "oldid": revid, "format": "json"}
        R = S.get(url=URL, params=params)
        DATA = R.json()
        clear_text = clean_html(DATA['parse']['text']['*'])
        

    # TODO: Accertarsi che salvi correttamente quello che ci serve
    #compressed_pickle(f"{path}/revisions", elements)


def diff(path):
    # TODO: Da aggiornare per la nuova versione
    # TODO: Apire il file .rev per ogni country
    #       Fare il diff tra due revisoni
    #       Salvare in un file (changes.json ?) autore, parole aggiunte, parole rimosse
    pass
    """
    print("Computing the diff between revisions")
    differences = list()
    revs: list(Revision) = decompress_pickle(f"{path}/revisions.pbz2")
    latest_revision = revs[0].text
    for rev in revs[1:]:
        change = new_find_diff(rev.revid, latest_revision, rev.text)
        differences.append(change.toJson())
        latest_revision = rev.text
    with open(f"{path}/changes.json", "w", encoding="utf-8") as output:
        json.dump(differences, output, indent=2, sort_keys=False, ensure_ascii=False)
    """


def new_find_diff(cid, document1, document2):
    dmp = dmp_module.diff_match_patch()
    changes = dmp.diff_main(document1, document2, checklines=True, deadline=20)
    dmp.diff_cleanupSemantic(changes)
    a_changes = []
    b_changes = []

    for op, change in changes:
        if op == -1:
            a_changes.append(change)

        if op == 1:
            b_changes.append(change)

    a_changes = "".join(a_changes)
    b_changes = "".join(b_changes)
    return Change(cid, b_changes, a_changes)

def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding="utf-8")
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2, sort_keys=False, ensure_ascii=False)
    # Close the output file
    out_file.close()



def clean_html(raw_html):
    # Ritorna il testo pulito dal html 
    # TODO ora bisogna tokenizzarlo
    cleantext = BeautifulSoup(raw_html, "html.parser").text
    return cleantext

if __name__ == "__main__":
    # TODO: Forse `pandas` gestisce meglio file enormi


    with open("all_revisions.json", "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    countries = get_countries()
    for country in countries:
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

    
