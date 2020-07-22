from file_utilities import decompress_pickle, get_countries
from pathlib import Path
from typing import Dict


def average(lst):
    return sum(lst) / len(lst)


def get_revisions(country: str):
    path = f"countries/{country.lower()}"
    Path(path).mkdir(parents=True, exist_ok=True)
    return decompress_pickle(f"{path}/revisions.pbz2")


def authors_per_article(countries: list):
    avg_authors = list()
    for country in countries:
        revisions = get_revisions(country)
        authors = list()
        for revision in revisions:
            user = revision["user"]
            if user == "Anonimous":
                authors.append(user)
            else:
                if user not in authors:
                    authors.append(user)
        avg_authors.append(len(authors))
        print(
            f"Country: {country} has {len(revisions)} revisions from {len(authors)} authors"
        )
    print(
        f"Authors per article: min {min(avg_authors)} max: {max(avg_authors)} avg: {average(avg_authors)}"
    )


def articles_per_author(countries: list):
    authors: Dict[str, int] = dict()
    for country in countries:
        print(country)
        revisions = get_revisions(country)
        for revision in revisions:
            user = revision["user"]
            if user in authors:
                authors[user] += 1
            else:
                authors[user] = 1
    all_values = authors.values()
    avg_value = average(all_values)
    max_value = max(all_values)
    min_value = min(all_values)
    print(max_value, min_value, avg_value)
    print("No Anon")
    del authors["Anonimous"]
    all_values = authors.values()
    avg_value = average(all_values)
    max_value = max(all_values)
    min_value = min(all_values)
    print(max_value, min_value, avg_value)


if __name__ == "__main__":
    countries = get_countries()
    # authors_per_article(countries)
    # articles_per_author(countries)
