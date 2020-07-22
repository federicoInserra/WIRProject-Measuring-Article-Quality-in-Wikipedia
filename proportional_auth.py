import bz2
import pickle
import _pickle as cPickle
import json
from pathlib import Path
import math
import file_utilities as fut
import metrics
from random import random

users_aut = {}
docs_quality = {}


def gen_random():
    value = random()
    value = f"{value:.3f}"
    value = float(value)

    return value


def init_doc_quality():
    countries = fut.get_countries()

    for country in countries:
        docs_quality[country] = gen_random()


def init_users_aut(users_contribution):
    for user in users_contribution:
        users_aut[user] = gen_random()


def calculate_contributions(revisions, differences, country, users_contributions):

    i = 0

    while i < len(differences):

        try:
            rev = differences[i]
            next_rev = differences[i + 1]
            added = rev["added"]

            while (
                rev["user"] == next_rev["user"]
            ):  # se lo user fa più revisioni di fila
                # le unisco e la considero come unica

                added += next_rev["added"]
                i += 1
                rev = next_rev
                next_rev = differences[i + 1]

            user = rev["user"]

            # take the actual text
            last_rev = fut.filter_text(revisions[0]["text"])

            # check the words that are survived
            survived_words = [w for w in added if w in last_rev]

            contribution = len(survived_words) / len(last_rev)

            if user in users_contributions:
                if country in users_contributions[user]:
                    users_contributions[user][country] += contribution
                else:
                    users_contributions[user][country] = contribution
            else:
                users_contributions[user] = {country: contribution}

        except Exception as e:
            print(e)
            pass

        i += 1

    return users_contributions


def calculate_authorities(users_contributions):
    auth = 0
    max_auth = 0

    for user in users_contributions:
        for country in users_contributions[user]:
            auth += users_contributions[user][country] * docs_quality[country]

        # save max authority to normalize
        if auth > max_auth:
            max_auth = auth

        users_aut[user] = auth

    # normalize
    for user in users_aut:
        users_aut[user] = users_aut[user] / max_auth


def calculate_qualities(users_contributions):
    quality = 0
    max_quality = 0
    docs = {}

    for user in users_contributions:
        for country in users_contributions[user]:
            if country in docs:
                docs[country] += users_contributions[user][country] * users_aut[user]
            else:
                docs[country] = users_contributions[user][country] * users_aut[user]

            if docs[country] > max_quality:
                max_quality = docs[country]

    for country in docs:
        docs_quality[country] = docs[country] / max_quality


def calculate_rank(users_contributions):

    # initialize authority and quality of documents
    init_doc_quality()
    init_users_aut(users_contributions)

    for _ in range(10):

        calculate_authorities(users_contributions)
        calculate_qualities(users_contributions)

    rank_countries = sorted(docs_quality.items(), key=lambda x: x[1], reverse=True)

    return rank_countries


if __name__ == "__main__":
    
    
    users_contributions = {}
    countries = fut.get_countries()

    for country in countries:
        print("Processing "+ country)
        
        try:
            
            # get entire revisions
            path_rev = path = f"countries/{country.lower()}/revisions.pbz2"
            revisions = fut.decompress_pickle(path)
            

            # get all the differences between revisions
            path_diff = f"countries/{country.lower()}/differences.pbz2"
            differences = fut.decompress_pickle(path_diff)
            

            users_contributions = calculate_contributions(revisions, differences, country, users_contributions)
            
        except Exception as e:
            print(e)
            pass
    
    fut.save_as_json("users_contributions", users_contributions)
    
    f = open("users_contributions.json", "r", encoding="utf-8")
    users_contributions = json.load(f)
    f.close()

    f = open("ranked_countries.json", "r", encoding="utf-8")
    real_rank = json.load(f)
    f.close()

    rank = calculate_rank(users_contributions)

    print("\n")
    print("-----------------  NDCG score  -------------")
    print("\n")
    print("TOP 12")
    print(metrics.NDCG_score(real_rank, rank, 12))
    print("\n")

    print("TOP 22")
    print(metrics.NDCG_score(real_rank, rank, 22))
    print("\n")

    print("TOP 81")
    print(metrics.NDCG_score(real_rank, rank, 81))
    print("\n")

    print("TOP 206")
    print(metrics.NDCG_score(real_rank, rank, 206))
    print("\n")

