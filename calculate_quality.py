import bz2
import pickle
import _pickle as cPickle
import json
from pathlib import Path
import math


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




def reward_users(survived_words, i, users_score, score):

    while i < len(differences):
        try:
            next_rev = differences[i+1]
            user = next_rev['user']
            removed = next_rev['removed']
            not_to_remove = [w for w in survived_words if w in removed ] # se avevo rimosso una parola che poi è stata rimessa vengo penalizzato

            reward = score / (len(not_to_remove) + 1) # più parole ho rimosso meno ottengo come punteggio 

            if user in users_score:
                users_score[user]['rewards'].append(reward)
            else:
                users_score[user] = {'added': [], 'rewards': [reward]}

        except Exception as e:
            
            pass
        i += 1
    
    return users_score

    


def distributed_score(differences, users_score, path):
    list_of_users = []
    i = 0
    revisions = decompress_pickle(path)
    
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
            last_rev = revisions[0]

            # check the words that are survived      
            survived_words = [w for w in added if w in last_rev['text'] ]
            score = len(survived_words) * (len(revisions) - i)
            if len(survived_words) > 0 and score > 0:
                users_score = reward_users(survived_words, i, users_score, score)



            if user in users_score:
                users_score[user]['added'].append(score)
            else:
                users_score[user] = {'added': [score], 'rewards': []}

        
            list_of_users.append(user) #lista di utenti che hanno revisionato il paese

        except Exception as e:
            print(e)
            pass

        i += 1

    return users_score, list_of_users



    pass
def new_check_diff(added, revisions, i):
    
    last_rev = revisions[0]
    
    if len(added) > 0:
        
        good_words = [w for w in added if w in last_rev['text'] ]
        score = len(good_words) / len(added) * (len(revisions) - i) # più tempo è passato da quando ho fatto la revisione e più vuol dire che quello che ho scritto era buono
            
    else:
        score = 0
    
    return score


def calculate_scores(differences, users_score, path):
    list_of_users = []
    i = 0
    revisions = decompress_pickle(path)
    
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
            next_user = next_rev['user']
            removed = next_rev['removed']

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

    f = open("users_score.json", "r", encoding="utf-8")
    data = json.load(f)
    users_auth = {}
    max_authority = 0

    for user in data:
        
        score_add = sum(data[user]['added']) / (len(data[user]['added']) +1)
        """
        score_rew = sum(data[user]['rewards']) / (len(data[user]['rewards']) +1)
        authority = score_add + score_rew + 1
        """
        authority = score_add
        if authority > max_authority:
            max_authority = authority
        
        users_auth[user] = authority
    
    # normalize
    for user in users_auth:
        users_auth[user] = users_auth[user] / max_authority
    
    return users_auth

def calculate_quality(users_auth):
    #la qualità di un articolo è data dalla somma delle autorità di chi ha partecipato
    # alla revisione dell articolo
    f = open("countries_score.json", "r", encoding="utf-8")
    data = json.load(f)
    docs_quality = {}
    for country in data:
        docs_quality[country] = 0
        for user in data[country]:
            docs_quality[country] += users_auth[user]
    
    return docs_quality


def calculate_Z(topK, real_rank):
    labels = {'FA': [], 'GA':[], 'B': [], 'C': [], 'NOL': []}
    for country in real_rank:
        label = real_rank[country]
        labels[label].append(country)

    perfect_rank = labels['FA'] + labels['GA'] + labels['B'] + labels['C'] + labels['NOL']
    perfect_score = 0
    for i in range(topK):
        country = perfect_rank[i]
        p = i + 1
        if real_rank[country] == 'FA':
            score = (pow(2,4) - 1) / math.log(1+p)
        
        elif real_rank[country] == 'GA':
            score = (pow(2,3) - 1) / math.log(1+p)
        
        elif real_rank[country] == 'B':
            score = (pow(2,2) - 1) / math.log(1+p)
        
        elif real_rank[country] == 'C':
            score = (pow(2,1) - 1) / math.log(1+p)
        
        else:
            score = 0
        
        perfect_score += score
    
    return perfect_score


def NDCG_score(real_rank, predict_rank , topK):

    # FA = 12, GA = 10, B = 59, C = 123, NOL = 2

    total = 0
    
    for i in range(topK):
        
        try:
            p = i + 1
            country = predict_rank[i][0]
            if real_rank[country] == 'FA':
                score = (pow(2,4) - 1) / math.log(1+p)
            
            elif real_rank[country] == 'GA':
                score = (pow(2,3) - 1) / math.log(1+p)
            
            elif real_rank[country] == 'B':
                score = (pow(2,2) - 1) / math.log(1+p)
            
            elif real_rank[country] == 'C':
                score = (pow(2,1) - 1) / math.log(1+p)
            
            else:
                score = 0
        except:
            score = 0
            pass
        
        total += score
    
    Z = calculate_Z(topK, real_rank)   
    print("THIS IS PERFECT SCORE",Z)
    return total/Z

if __name__ == "__main__":

    
    
    f = open("ranked_countries.json", "r", encoding="utf-8")
    data = json.load(f)
    
    
    countries = get_countries()
    users_score = {}
    countries_score = {}

    for country in countries:
        print("Processing "+ country)
        
        try:
            path_rev = path = f"countries/{country.lower()}/revisions.pbz2"
            

            path_diff = f"countries/{country.lower()}/differences.pbz2"

            differences = decompress_pickle(path_diff)

            users_score, list_of_users = calculate_scores(differences, users_score, path_rev)
            #users_score, list_of_users = distributed_score(differences, users_score, path_rev)

            countries_score[country] = list_of_users
        except Exception as e:
            print(e)
            pass
        
   

    save_as_json(f"users_score", users_score)
    save_as_json(f"countries_score", countries_score)
    
    users_auth = calculate_auth()
    docs_quality = calculate_quality(users_auth)

    rank_countries = sorted(docs_quality.items(), key=lambda x: x[1], reverse=True)
    
    print("\n")
    print("-----------------  NDCG score  -------------")
    print("\n")
    print("TOP 12")
    print(NDCG_score(data, rank_countries, 12))
    print("\n")

    print("TOP 22")
    print(NDCG_score(data, rank_countries, 22))
    print("\n")

    print("TOP 81")
    print(NDCG_score(data, rank_countries, 81))
    print("\n")

    print("TOP 206")
    print(NDCG_score(data, rank_countries, 206))
    print("\n")
    

    
    
