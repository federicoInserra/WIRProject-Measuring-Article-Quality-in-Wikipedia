import metrics
import file_utilities as fut
import json


def naive_classifier():
    countries = fut.get_countries()
    country_dict = dict()
    for country in countries:
        print(f"{country}")
        revisions = fut.get_revisions(country)
        text_len = len(fut.parse_text(revisions[0]["text"]).split())
        country_dict[country] = text_len
    finale = sorted(country_dict, key=country_dict.get, reverse=True)
    list_of_tuple = list()
    for elem in finale:
        toadd = (elem, 0)
        list_of_tuple.append(toadd)
    return list_of_tuple


if __name__ == "__main__":
    f = open("ranked_countries.json", "r", encoding="utf-8")
    data = json.load(f)
    rank_countries = naive_classifier()
    f.close()
    print("\n")
    print("-----------------  NDCG score  -------------")
    print("\n")
    print("TOP 12")
    print(metrics.NDCG_score(data, rank_countries, 12))
    print("\n")

    print("TOP 22")
    print(metrics.NDCG_score(data, rank_countries, 22))
    print("\n")

    print("TOP 81")
    print(metrics.NDCG_score(data, rank_countries, 81))
    print("\n")

    print("TOP 206")
    print(metrics.NDCG_score(data, rank_countries, 206))
    print("\n")
