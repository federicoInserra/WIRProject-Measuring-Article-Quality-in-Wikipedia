"""
from typing import Tuple, List
import json
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import word_tokenize
"""
import requests
import xml.etree.ElementTree as ET
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
    url = f"https://en.wikipedia.org/w/index.php?title=Special:Export&pages={country}&dir=desc$limit={revision_no}"
    response = requests.post(url=url)
    compressed_pickle(f"{path}/revisions", response.text)


def parse_xml(filename: str):
    # TODO: Parse <revision>s elements in XML https://stackoverflow.com/questions/1912434/how-do-i-parse-xml-in-python
    root = ET.parse(filename).getroot()


if __name__ == "__main__":
    # Get the list of countriess
    countries = get_countries()

    # Number of revision to download
    REVNO = 5
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
