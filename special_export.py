import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import word_tokenize
import json
from io import StringIO
import requests
import xml.etree.ElementTree as ET
import mwparserfromhell
import bz2
import pickle
import _pickle as cPickle
from pathlib import Path
import diff_match_patch as dmp_module

nltk.download("stopwords")
nltk.download("punkt")


# Pickle a file and then compress it into a file with extension
def compressed_pickle(title, data):
    with bz2.BZ2File(title + ".pbz2", "wb") as f:
        cPickle.dump(data, f, -1)


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
            print(f"HTTP ERROR: {response.status_code}")
    except Exception as e:
        print(e)


def parse_xml(xml: str):
    # TODO: Parse <revision>s elements in XML https://stackoverflow.com/questions/1912434/how-do-i-parse-xml-in-python
    it = ET.iterparse(StringIO(xml))
    for _, el in it:
        _, _, el.tag = el.tag.rpartition("}")  # strip namespaces
    root = it.root[1]
    revisions = root.findall("revision")
    texts = []
    for revision in revisions:
        timestamp = revision.find("timestamp").text
        revid = revision.find("id").text
        user = "Anonimous"
        if revision.find("contributor").find("username") != None:
            user = revision.find("contributor").find("username").text
        raw_mediawiki = revision.find("text").text
        text = mwparserfromhell.parse(raw_mediawiki).strip_code()
        rev_object = dict()
        rev_object["user"] = user
        rev_object["timestamp"] = timestamp
        rev_object["revid"] = revid
        rev_object["text"] = text
        texts.append(rev_object)
    return texts


def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding="utf-8")
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2, sort_keys=False, ensure_ascii=False)
    # Close the output file
    out_file.close()


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
        new_text = new_rev["text"]  # or construct_text(new_rev["text"])
        old_text = old_rev["text"]  # or construct_text(old_rev["text"])
        removed_text, added_text = find_diff(old_text, new_text)
        diff["revid"] = new_rev["revid"]
        diff["timestamp"] = new_rev["timestamp"]
        diff["user"] = new_rev["user"]
        diff["added"] = added_text
        diff["removed"] = removed_text
        # save_as_json(f"dif_{i}", diff)
        differences.append(diff)
        old_rev = new_rev
        i -= 1
    compressed_pickle(f"{path}/differences", differences)


def find_diff(document1, document2):
    dmp = dmp_module.diff_match_patch()
    changes = dmp.diff_main(document1, document2, deadline=20)
    removed_text = ""
    added_text = ""
    for op, change in changes:
        if op == -1:
            removed_text += change
        if op == 1:
            added_text += change
    return (
        word_tokenize(removed_text, preserve_line=True),
        word_tokenize(added_text, preserve_line=True),
    )


if __name__ == "__main__":
    # Get the list of countriess
    countries = get_countries()
    # Number of revision to download
    REVNO = 10
    for country in countries:
        try:
            path = f"countries/{country.lower()}"
            Path(path).mkdir(parents=True, exist_ok=True)
            exists = Path.exists(Path(f"{path}/revisions.pbz2"))
            if exists:
                print(f"Revisions file found for country: {country}!")
                diff(path)
            else:
                print(f"Revisions not found, downloading: {country}...")
                download_revisions(country=country, revision_no=REVNO, path=path)
                diff(path)

        except Exception as e:
            print(e)
            pass
