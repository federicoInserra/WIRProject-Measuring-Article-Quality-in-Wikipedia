from file_utilities import decompress_pickle, get_countries
from pathlib import Path


def average(lst):
    return sum(lst) / len(lst)


if __name__ == "__main__":
    countries = get_countries()
    avg_authors = list()
    for country in countries:
        path = f"countries/{country.lower()}"
        Path(path).mkdir(parents=True, exist_ok=True)
        revisions = decompress_pickle(f"{path}/revisions.pbz2")
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
    no_duplicates = set(avg_authors)
    print(
        f"Unique authors per article: min {min(no_duplicates)} max: {max(no_duplicates)} avg: {average(no_duplicates)}"
    )
