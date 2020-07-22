import metrics
import file_utilities as fut
import statistics as stat
import metrics
import json

def naive_classifier():
    countries = fut.get_countries()
    country_list = []
    country_dict = dict()
    for country in countries[:5]:
        print(f"{country}")
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
    ordered_list = naive_classifier()
    metrics.NDCG_score(data,ordered_list,81)
    f.close()