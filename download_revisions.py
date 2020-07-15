import pywikibot
import pypandoc
import difflib
import bz2
import pickle
import _pickle as cPickle
import re
import json
from dataclasses import dataclass
from pathlib import Path

NUMBER_OF_REVISIONS = 10


@dataclass
class Change:
    _added: str
    _removed: str

    @property
    def added(self) -> str:
        return self._added

    @added.setter
    def added(self, v: str) -> None:
        self._added = v

    @property
    def removed(self) -> str:
        return self._removed

    @added.setter
    def removed(self, v: str) -> None:
        self._removed = v

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


def converto_to_html(file):
    text = pypandoc.convert_text(file, format="mediawiki", to="html5")
    text = text.split('<h2 id="see_also">See also</h2>')[0]
    clean = re.compile("<.*?>")
    clean = re.sub(clean, "", text.strip())
    return clean


def find_difference(file1, file2):
    change = Change(None, None)
    diff = [li for li in difflib.ndiff(file1, file2) if li[0] != " "]
    removed = [elem for elem in diff if elem[0] == "-"]
    added = [elem for elem in diff if elem[0] == "+"]
    if removed:
        removed_words = [elem[2] for elem in removed]
        change.removed = "".join(removed_words)
    if added:
        added_words = [elem[2] for elem in added]
        change.added = "".join(added_words)
    return change


def download_revisions(path):
    # The site we want to run our bot on
    site = pywikibot.Site("en", "wikipedia")
    page = pywikibot.Page(site, country)
    revs = list(page.revisions(content=True, total=NUMBER_OF_REVISIONS))
    elements = list()
    for elem in revs:
        # text = converto_to_html(elem.text)
        revision = Revision(elem.revid, elem.user, elem.text)
        elements.append(revision)
    compressed_pickle(f"{path}/revisions", elements)


def diff(path):
    print("Computing the diff between revisions")
    differences = dict()
    revs: list(Revision) = decompress_pickle(f"{path}/revisions.pbz2")
    latest_revision = revs[0].text
    for rev in revs[1:]:
        change = find_difference(latest_revision, rev.text)
        differences[rev.revid] = change.toJson()
        latest_revision = rev.text
    with open(f"{path}/changes.json", "w", encoding="utf-8") as output:
        json.dump(differences, output, indent=2, sort_keys=False, ensure_ascii=False)


if __name__ == "__main__":
    country = "Italy"
    path = f"countries/{country.lower()}"
    Path(path).mkdir(parents=True, exist_ok=True)
    exists = Path.exists(Path(f"{path}/revisions.pbz2"))
    if exists:
        print("Revisions file found!")
        diff(path)
    else:
        print("Revisions not found, downloading...")
        download_revisions(path)
        diff(path)
