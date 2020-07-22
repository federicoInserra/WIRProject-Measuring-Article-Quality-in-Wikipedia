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


def init_doc_quality(countries):
    
    for country in countries:
        docs_quality[country] = gen_random()

def init_users_aut(users):
    
    for user in users:   
        users_aut[user] = gen_random()


def check_words(added, revisions, i, reviewers):
    
    
    
    current_text = fut.filter_text(revisions[0]['text'])
    review = {}
         
    survived_words = [ w for w in added if w in current_text ]
        
    
    review["from"] = i
    review["survived_words"] = survived_words
    review['contrib'] = len(survived_words) / len(current_text)
    
    return review


def calculate_scores(differences, users_score, revisions, country):
    
    reviewers = []
    for i in range(len(differences)):
        
        try:
            reviewers.append(revisions[-i - 1]['user'])
        except Exception as e:
            print(e)
            pass
    
    i = 0
    while i < len(differences):
        
        try:
            rev = differences[i]
            next_rev = differences[i+1]
            added = rev['added']
            while(rev['user'] == next_rev['user']): #se lo user fa più revisioni di fila
                                                    #le unisco e la considero come unica
                
                added += next_rev['added']
                i += 1
                rev = next_rev
                next_rev = differences[i+1]

            
            user = rev['user']
            
            review = check_words(added, revisions, i, reviewers)
            review['country'] = country

            

            if len(review['survived_words']) > 0:
                
                if user in users_score:
                    users_score[user].append(review)
                else:
                    users_score[user] = [review]


        except Exception as e:
            print(e)
            pass

        i += 1
        

    return users_score, reviewers



def calculate_auth(users_score, countries_score):
    
    max_auth = 0
    auth = 0
    for user in users_score:
        for review in users_score[user]:
            i = review['from']
            country = review['country']
            contrib = review['contrib']

            while i < len(countries_score[country]):
                try:
                    auth += users_aut[countries_score[country][i]]
                    
                except Exception as e:
                    
                    pass
                i+= 1
            
            auth = ((auth/len(countries_score[country])) * contrib)

        if auth > max_auth:
            max_auth = auth
        
        users_aut[user] = auth

    
    for user in users_aut:
        users_aut[user] = users_aut[user]/ max_auth
    
    

def calculate_quality(countries_score, users_score):
    
    contributions = {}
    max_quality = 0
    for user in users_score:
        for review in users_score[user]:
            country = review['country']
            contrib = review['contrib']

            if country in contributions:
                contributions[country].append((user,contrib))
            else:
                contributions[country] = [(user,contrib)]
    
            

    for country in contributions:
        quality =  0
        for contrib in contributions[country]:
            quality += users_aut[contrib[0]] * contrib[1] 
        

        if quality > max_quality:
            max_quality = quality
        
        docs_quality[country] = quality
    
    for country in docs_quality:
        docs_quality[country] = docs_quality[country] / max_quality


if __name__ == "__main__":

    
    
    f = open("ranked_countries.json", "r", encoding="utf-8")
    data = json.load(f)
    
    
    countries = fut.get_countries()
    """
    users_score = {}
    countries_score = {}

    for country in countries:
        print("Processing "+ country)
        
        try:
            path_rev = path = f"countries/{country.lower()}/revisions.pbz2"
            revisions = fut.decompress_pickle(path_rev)
            

            path_diff = f"countries/{country.lower()}/differences.pbz2"
            differences = fut.decompress_pickle(path_diff)

            
            users_score, reviewers = calculate_scores(differences, users_score, revisions, country)
            countries_score[country] = reviewers
            

        except Exception as e:
            print(e)
            pass
        
   

    fut.save_as_json(f"users_score", users_score)
    fut.save_as_json(f"countries_score", countries_score)
    """
    with open("users_score.json", "r", encoding="utf-8") as f:
        users_score = json.load(f)
    
    with open("countries_score.json", "r", encoding="utf-8") as f:
        countries_score = json.load(f)

    init_users_aut(users_score)
    init_doc_quality(countries_score)

    for _ in range(10):
        calculate_auth(users_score, countries_score)
        calculate_quality(countries_score, users_score)

    rank_countries = sorted(docs_quality.items(), key=lambda x: x[1], reverse=True)
    
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