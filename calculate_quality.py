import bz2
import pickle
import _pickle as cPickle
import json
from pathlib import Path


def compressed_pickle(title, data):
    with bz2.BZ2File(title + ".pbz2", "wb") as f:
        cPickle.dump(data, f)


# Load any compressed pickle file
def decompress_pickle(file):
    data = bz2.BZ2File(file, "rb")
    return cPickle.load(data)

def get_countries():
    with open("list_of_countries.txt", "r") as fo:
        countries = [country.strip() for country in fo]

    return countries
def check_differences(added, removed):

    if len(added) > 0:
        
        good_words = [w for w in added if w not in removed ]
        score = len(good_words)
            
    else:
        score = 0
    
    return score


def calculate_scores(differences, users_score):
    list_of_users = []
    
    for i in range(len(differences)):
        try:
            rev = differences[i]
            next_rev = differences[i+1]

            added = rev['added']
            user = rev['user']
            next_user = next_rev['user']
            removed = next_rev['removed']

            score = check_differences(added, removed)

            if user in users_score:
                users_score[user]['added'].append(score)
            else:
                users_score[user] = {'added': [score], 'removed': []}

            next_user = next_rev['user']
            if next_user in users_score:
                users_score[next_user]['removed'].append(len(removed))
            else:
                users_score[next_user] = {'added': [], 'removed': [len(removed)]}
            
            list_of_users.append(user)

        except:
            pass

    return users_score, list_of_users
        
def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding="utf-8")
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2, sort_keys=False, ensure_ascii=False)
    # Close the output file
    out_file.close()

    

if __name__ == "__main__":

    #TODO scrivere la funzione che calcola la qualità del documento in base ai punteggi degli utenti
    # Implementare il fatto che se un utente fa tante revisioni di fila, va interpretata come un unica revisione

    countries = get_countries()
    users_score = {}
    countries_score = {}

    for country in countries:
        print("Processing "+ country)
        try:
            path = f"countries/{country.lower()}/differences.pbz2"

            differences = decompress_pickle(path)

            users_score, list_of_users = calculate_scores(differences, users_score)
        except Exception as e:
            print(e)
            pass
        
        countries_score[country] = list_of_users

    save_as_json(f"users_score", users_score)
    save_as_json(f"countries_score", countries_score)
    

    
