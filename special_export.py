"""
from typing import Tuple, List
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import word_tokenize
"""
import json
from io import StringIO
import requests
import xml.etree.ElementTree as ET
import mwparserfromhell
import bz2
import pickle
import _pickle as cPickle
from pathlib import Path

# Pickle a file and then compress it into a file with extension
def compressed_pickle(title, data):
    with bz2.BZ2File(title + ".pbz2", "wb") as f:
        cPickle.dump(data, f)


# Load any compressed pickle file
def decompress_pickle(file):
    data = bz2.BZ2File(file, "rb")
    return cPickle.load(data)


def get_countries():
    with open("list_of_countries.txt", "r", encoding="utf-8") as fo:
        countries = [country.strip() for country in fo]
    return countries


def download_revisions(country: str, revision_no: int, path: str) -> None:
    # API Parameters: https://www.mediawiki.org/wiki/Manual:Parameters_to_Special:Export
    try:
        url = f"https://en.wikipedia.org/w/index.php?title=Special:Export&pages={country}&dir=desc&limit={revision_no}"
        response = requests.post(url=url)
        if response.status_code == 200:
            revisions_json = parse_xml(response.text)
            compressed_pickle(f"{path}/revisions", revisions_json)
        else:
            print(response.status_code)
    except:
        pass


def parse_xml(xml: str):
    # TODO: Parse <revision>s elements in XML https://stackoverflow.com/questions/1912434/how-do-i-parse-xml-in-python
    it = ET.iterparse(StringIO(xml))
    for _, el in it:
        _, _, el.tag = el.tag.rpartition("}")  # strip ns
    root = it.root[1]
    revisions = root.findall("revision")
    texts = list()
    rev_object = {}
    for revision in revisions:
        timestamp = revision.find("timestamp").text
        revid = revision.find("id").text
        user = revision.find("contributor").find("username").text
        raw_mediawiki = revision.find("text").text
        text = mwparserfromhell.parse(raw_mediawiki)
        # TODO: filter() https://mwparserfromhell.readthedocs.io/en/latest/_modules/mwparserfromhell/wikicode.html#Wikicode.filter
        rev_object["user"] = user
        rev_object["timestamp"] = timestamp
        rev_object["revid"] = revid
        rev_object["text"] = text
        texts.append(rev_object)
    return texts


if __name__ == "__main__":
    # Get the list of countriess
    countries = get_countries()

    # Number of revision to download
    REVNO = 1000
    for country in countries:
        try:
            path = f"countries/{country.lower()}"
            Path(path).mkdir(parents=True, exist_ok=True)
            exists = Path.exists(Path(f"{path}/revisions.pbz2"))
            if exists:
                print("Revisions file found!")
                # diff(path)
            else:
                print(f"Revisions not found, downloading: {country}...")
                download_revisions(country=country, revision_no=REVNO, path=path)
                # diff(path)

        except Exception as e:
            print(e)
            pass
