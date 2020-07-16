import spacy
import json


def load_changes(country):
    with open(f"countries/{country.lower()}/changes.json", "r") as json_file:
        return json.load(json_file)


if __name__ == "__main__":
    nlp = spacy.load("en_core_web_sm")
    changes = load_changes("Italy")
    # TODO: Handle the JSON file and get the fields of the object
    for change in changes:
        print(change)
    """
    doc = nlp(clean)
    for entity in doc.ents:
        print(entity.text, entity.label_)
    """
