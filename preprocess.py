import re
import spacy


def save_to_plaintext(text):
    with open("countries/italy_clean.txt", "w") as out_file:
        out_file.write(text)


if __name__ == "__main__":
    # Open the HTML version of the page
    with open("countries/italy.html", "r") as html:
        text = html.read().strip()
    # Remove latest notes
    text = text.split('<h2 id="see_also">See also</h2>')[0]
    clean = re.compile("<.*?>")
    clean = re.sub(clean, "", text.strip())
    # Save the plaintext version of the Wikipedia page
    save_to_plaintext(clean)
    # Load SpaCy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(clean)
    for entity in doc.ents:
        print(entity.text, entity.label_)
