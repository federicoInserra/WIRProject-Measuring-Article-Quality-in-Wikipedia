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
    # La funzione controlla le differenze tra ciò che è stato aggiunto e ciò che è
    # stato rimosso nella revisione successiva
    # la lunghezza delle parole rimaste dopo la revisione è il mio score per quella revisione

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
            while(rev['user'] == next_rev['user']): #se lo user fa più revisioni di fila
                                                    #le unisco e la considero come unica
                
                added += next_rev['added']
                i += 1
                rev = next_rev
                next_rev = differences[i+1]

            
            user = rev['user']
            next_user = next_rev['user']
            removed = next_rev['removed']

            score = check_differences(added, removed)

            # mi salvo anche il numero di parole rimosse, magari
            # un utente con una buona autorità si vede anche da quante revisioni sistema

            if user in users_score:
                users_score[user]['added'].append(score)
            else:
                users_score[user] = {'added': [score], 'removed': []}

            next_user = next_rev['user']
            if next_user in users_score:
                users_score[next_user]['removed'].append(len(removed))
            else:
                users_score[next_user] = {'added': [], 'removed': [len(removed)]}
            
            list_of_users.append(user) #lista di utenti che hanno revisionato il paese

        except:
            pass

    return users_score, list_of_users
        
def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding="utf-8")
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2, sort_keys=False, ensure_ascii=False)
    # Close the output file
    out_file.close()

    
def calculate_auth():
    #calcolo l'autorità come la somma tra la media degli score delle revisioni
    # sul contenuto aggiunto e quella di quello rimosso
    # a e b sono due costanti per dare peso diverso ai due punteggi (forse il contenuto
    # aggiunto è più importante di quello rimosso)

    f = open("users_score.json", "r")
    data = json.load(f)
    users_auth = {}
    a = 0.6
    b = 0.4

    for user in data:
        
        score_add = sum(data[user]['added']) / (len(data[user]['added']) +1)
        score_rm = sum(data[user]['removed']) / (len(data[user]['removed']) +1)
        users_auth[user] = (a * score_add) + (b * score_rm)
    
    return users_auth

def calculate_quality(users_auth):
    #la qualità di un articolo è data dalla somma delle autorità di chi ha partecipato
    # alla revisione dell articolo
    f = open("countries_score.json", "r")
    data = json.load(f)
    docs_quality = {}
    for country in data:
        docs_quality[country] = 0
        for user in data[country]:
            docs_quality[country] += users_auth[user]
    
    return docs_quality

    
if __name__ == "__main__":

    

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

    users_auth = calculate_auth()
    docs_quality = calculate_quality(users_auth)

    rank_countries = sorted(docs_quality.items(), key=lambda x: x[1], reverse=True)

    for i in rank_countries:
        print(i[0], i[1])
    

    
