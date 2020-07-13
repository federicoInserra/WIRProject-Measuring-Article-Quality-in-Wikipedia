'''
import pywikibot
import json

if __name__ == "__main__":
    with open("list_of_countries.txt", "r") as fo:
        countries = [country.strip() for country in fo]
        fo.close()

    # The site we want to run our bot on
    site = pywikibot.Site('en', 'wikipedia')
    memory = dict()
    for country in countries[:1]:
        print(f"Downloading: {country}")
        page = pywikibot.Page(site, country)
        revs = page.revisions(content=True, total=1)
        revisions = list()
        for rev in revs:
            # revisions.append(rev.text.strip().replace("\n", ""))
            revisions.append(rev.text)
        memory[country] = revisions
    out_file = open("revisions.json", "w")
    # Dump the dictionary as JSON object in the file
    json.dump(memory, out_file, indent=2,
              sort_keys=False,  ensure_ascii=False)
    # Close the output file
    out_file.close()

'''

import pywikibot
import pypandoc

if __name__ == "__main__":
    site = pywikibot.Site('en', 'wikipedia')
    page = pywikibot.Page(site, "Italy")
    revs = page.revisions(content=True, total=1)
    out_file = open("italy.html", "w")
    for rev in revs:
        output = pypandoc.convert_text(
            rev.text, format="mediawiki", to="html5")
        out_file.writelines(output)
    out_file.close()
