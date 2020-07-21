import bz2
import pickle
import _pickle as cPickle
import json
from pathlib import Path
import math
import file_utilities as fut
import metrics

users_aut = {}
docs_quality = {}


def gen_random():
    value = random()
    value = f"{value:.3f}"
    value = float(value)

    return value


def init_doc_quality(data):
    for country in data:
        docs_quality[country] = gen_random()

def init_users_aut(data):
    for country in data:
        for user in data[country]:
            if user not in users_aut:
                users_aut[user] = gen_random()


def new_check_diff(added, revisions, i):
    
    last_rev = revisions[0]
    
    if len(added) > 0:
        
        good_words = [w for w in added if w in last_rev['text'] ]
        score = len(good_words) / len(added) * (len(revisions) - i) # più tempo è passato da quando ho fatto la revisione e più vuol dire che quello che ho scritto era buono
            
    else:
        score = 0
    
    return score


def calculate_scores(differences, users_score, revisions):
    list_of_users = []
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
            
            score = new_check_diff(added, revisions, i)

            # mi salvo anche il numero di parole rimosse, magari
            # un utente con una buona autorità si vede anche da quante revisioni sistema

            if user in users_score:
                users_score[user]['added'].append(score)
            else:
                users_score[user] = {'added': [score], 'removed': []}

           
            list_of_users.append(user) #lista di utenti che hanno revisionato il paese

        except Exception as e:
            print(e)
            pass

        i += 1

    return users_score, list_of_users


if __name__ == "__main__":

    
    
    f = open("ranked_countries.json", "r", encoding="utf-8")
    data = json.load(f)
    
    
    countries = fut.get_countries()
    users_score = {}
    countries_score = {}

    for country in countries:
        print("Processing "+ country)
        
        try:
            path_rev = path = f"countries/{country.lower()}/revisions.pbz2"
            revisions = fut.decompress_pickle(path_rev)

            path_diff = f"countries/{country.lower()}/differences.pbz2"
            differences = fut.decompress_pickle(path_diff)


            users_score, list_of_users = calculate_scores(differences, users_score, path_rev)
            countries_score[country] = list_of_users

        except Exception as e:
            print(e)
            pass
        
   

    fut.save_as_json(f"users_score", users_score)
    fut.save_as_json(f"countries_score", countries_score)
    
    users_auth = calculate_auth()
    docs_quality = calculate_quality(users_auth)

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
    

    
    
