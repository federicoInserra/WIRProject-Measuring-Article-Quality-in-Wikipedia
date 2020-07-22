import bz2
import pickle
import _pickle as cPickle
import json
from pathlib import Path
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk import word_tokenize
from bs4 import BeautifulSoup
import diff_match_patch as dmp_module

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



def clean_html(raw_html):
    # Clean the text from the html sintax
    cleantext = BeautifulSoup(raw_html, "html.parser").text
    return filter_text(cleantext)


def filter_text(text):
    # Remove puntuaction
    tokenizer = RegexpTokenizer(r"\w+")
    cleantext = tokenizer.tokenize(text)

    # Remove stop words
    stop_words = set(stopwords.words("english"))
    filtered_text = [w for w in cleantext if not w in stop_words]

    return filtered_text