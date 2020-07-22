import metrics
import file_utilities as fut
import statistics as stat
import metrics
import json

def naive_classifier():
    countries = fut.get_countries()
    country_list = []
    country_dict = dict()
    for country in countries:
        #print(f"{country}")
        revisions = fut.get_revisions(country)
        max_length = 0
        for revision in revisions[:50]:
            text_len = len(fut.parse_text(revision["text"]).split())
            if(text_len > max_length):
                max_length = text_len
        country_dict[country] = max_length
        finale = sorted(country_dict, key=country_dict.get, reverse=True)
    return finale


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
