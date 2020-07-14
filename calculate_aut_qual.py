import json
from random import random

users_aut = {}
docs_quality = {}


def gen_random():
    value = random()
    value = f"{value:.3f}"
    value = float(value)

    return value


# Initialize the quality of the documents with random number
def init_doc_quality(data):
    for country in data:
        docs_quality[country] = gen_random()


# initialize the autorites of the users with random number
def init_users_aut(data):
    for country in data:
        for user in data[country]:
            if user not in users_aut:
                users_aut[user] = gen_random()


def calc_user_aut(data):

    users_score = {}

    for country in data:
        for user in data[country]:
            for score in data[country][user]:
                try:
                    if user in users_score:
                        if str(score[1]) != "null":
<<<<<<< HEAD
                            #users_score[user].append((score[0] * users_aut[str(score[1])]))
                            users_score[user].append(score[0])
=======
                            users_score[user].append(
                                (score[0] * users_aut[str(score[1])])
                            )
>>>>>>> 0fe95418884aa20aaab916986769d80f5d170353

                    else:
                        if str(score[1]) != "null":
                            #users_score[user] = [(score[0] * users_aut[str(score[1])])]
                            users_score[user] = [score[0]]
                except:
                    pass

    norm_value = -1000000000

    for user in users_score:
        avg_score = round((sum(users_score[user]) / len(users_score[user])), 2)
        if user != "null":
            users_aut[user] = avg_score
        if norm_value < avg_score:
            norm_value = avg_score

    # normalizzo le authorities
    for user in users_aut:
        users_aut[user] = users_aut[user] / norm_value
        if users_aut[user] < 0:
            users_aut[user] = 0


def calc_doc_quality(data):
    max_quality = -1000000
    for country in data:
        quality = 0
        for user in data[country]:
            if user != "null":
                quality += users_aut[user] * len(data[country][user])

        docs_quality[country] = quality

        if max_quality < quality:
            max_quality = quality

    for country in docs_quality:

        docs_quality[country] = docs_quality[country] / max_quality


# MAIN

f = open("users_scores.json",)
data = json.load(f)

init_users_aut(data)
init_doc_quality(data)


<<<<<<< HEAD

for _ in range(10):
=======
for _ in range(100):
>>>>>>> 0fe95418884aa20aaab916986769d80f5d170353

    calc_user_aut(data)
    calc_doc_quality(data)


rank_countries = sorted(docs_quality.items(), key=lambda x: x[1], reverse=True)

for i in rank_countries:
    print(i[0], i[1])

