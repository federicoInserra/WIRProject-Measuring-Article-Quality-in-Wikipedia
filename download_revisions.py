import pywikibot
import pypandoc
import diff_match_patch as dmp_module
import bz2
import pickle
import _pickle as cPickle
import re
import json
from dataclasses import dataclass
from pathlib import Path

NUMBER_OF_REVISIONS = 20


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


def converto_to_html(file):
    text = pypandoc.convert_text(file, format="mediawiki", to="html5")
    text = text.split('<h2 id="see_also">See also</h2>')[0]
    clean = re.compile("<.*?>")
    clean = re.sub(clean, "", text.strip())
    return clean


def download_revisions(path):
    # The site we want to run our bot on
    site = pywikibot.Site("en", "wikipedia")
    page = pywikibot.Page(site, country)
    revs = list(page.revisions(content=True, total=NUMBER_OF_REVISIONS))
    elements = list()
    for elem in revs:
        if not elem.minor:
            # TODO: Improve the cleanup process, maybe with a MediaWiki parser
            cleanup = elem.text.strip().split("country_code")
            # text = converto_to_html(cleanup)
            revision = Revision(elem.revid, elem.user, cleanup[1])
            elements.append(revision)
    compressed_pickle(f"{path}/revisions", elements)


def diff(path):
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
