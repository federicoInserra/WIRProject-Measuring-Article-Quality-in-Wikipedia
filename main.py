from file_utilities import decompress_pickle, get_countries
from pathlib import Path


if __name__ == "__main__":
    countries = get_countries()
    for country in countries:
        path = f"countries/{country.lower()}"
        Path(path).mkdir(parents=True, exist_ok=True)
        revisions = decompress_pickle(f"{path}/revisions.pbz2")
        authors = set()
        for revision in revisions:
            authors.add(revision["user"])
        print(
            f"Country: {country} has {len(revisions)} revisions from {len(authors)} authors"
        )
