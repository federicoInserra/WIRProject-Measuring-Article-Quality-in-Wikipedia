import requests
import json
import math


"""


VEDERE PYWIKIBOT che permette di recuperare il testo di una vecchia versione di una pagina passandogli l'id della versione
ho provato ad installarlo ma la documentazione è abbastanza un casino.

IDEA

L'IDEA è QUELLA CHE OGNI UTENTE PER OGNI REVISIONE CHE FA OTTIENE UN PUNTEGGIO CALCOLATO IN BASE ALLA SUCCESSIVA REVISIONE CHE UN UTENTE
FA DELLA SUA
IDEALMENTE SE FACCIO DELLE BUONE REVISIONI (SE L'UTENTE CHE FA LA REVISIONE DOPO LA MIA NON MODIFICA TROPPO LA MIA REVISIONE) OTTENGO UN PUNTEGGIO E QUINDI UN
AUTORITà ALTA.
Potremmo anche pensare di moltiplicare il punteggio di ogni revisione per l'autorità del utente che l'ha fatta, in questo modo se l'utente che fa la revisione
del mio contenuto ha un autorità alta e gran parte del contenuto che ho scritto non viene modificato, vuol dire che il contenuto molto probabilmente è di ottima
qualità e quindi otterrò un punteggio più alto. Al contrario se un utente con poca autorità modifica il mio contenuto, influirà poco sul mio punteggio.

L'idea è quindi quella di crearsi un dizionario degli utenti in cui ad ogni utente per ogni paese di cui fa la review ci salviamo:
punteggio della review calcolato con le funzioni che ho scritto o in altri modi migliori, nome utente che ha fatto la revisione.
In questo modo quando poi faremo il calcolo delle autorità potremo moltiplicare ogni punteggio per l'autorità del utente che ha fatto la revisione.


Oppure altra idea, per ogni utente calcoliamo semplicemente la media dei punteggi per un certo stato e lo moltiplichiamo per la qualità del documento di quello stato.

Ogni documento avrà una qualità che sarà data dalla somma delle autorità degli utenti che ne hanno preso parte, ognuna moltiplicata per il numero di revisioni fatte.

QUALITYj = SUM (Ai * |revAij| )           per ogni utente i che ha revisionato il documento j

mentre l'autorità di ogni utente può essere calcolata facendo:

AUTi = SUM (revAij * Qualityj)            per ogni punteggio delle revisioni del utente ognuna moltiplicata per la qualità del documento corrispondente alla revisione.




CRITICITA':

Va implementato al più presto per sapere se queste equazioni più o meno convergono o comunque arrivano a dei risultati decenti. Finche non lo implementiamo non si può
capire.

Dobbiamo capire quante e quali revisioni usare, io per ora ho usato per ogni documento le ultime 200 revisioni fatte, ma penso siano molto poche. Il problema è che già
cosi va parecchio lenta la computazione, bisogna provare su google.

La cosa migliore da fare probabilmente è calcolarsi i punteggi degli utenti per ogni stato e salvarsi tutto in un file.
Una volta che abbiamo tutto su file, ci calcoliamo l'autority e la quality di utenti e documenti dai dati che abbiamo sul file.
In questo modo calcoliamo una sola volta i punteggi delle revisioni degli utenti e possiamo fare diverse prove.

Se vi vengono in mente idee migliori magariii!!!
"""

users_dict = {}  # contiene come chiavi i nomi degli utenti e come attributi ogni utente ha una lista con i punteggi ottenuti dalle revisioni


def calculate_no_change_score(line):
    # questa deve calcolare se la linea che non è stata toccata era una linea con del contenuto di valore o meno
    # se ad esempio la linea conteneva un pezzo lungo di testo e questo non è stato modificato da una successiva revisione
    # vuol dire che il testo probabilmente era buono e quindi si otterà un punteggio alto
    # al contrario se la linea non conteneva contenuto utile(ad esempio uno spazio o andata a capo) non si ottiene punteggio aggiuntivo
    text = line['text']
    return math.log(1 + len(text))


def calculate_deletion_score(line):
    # questa calcola quanto va penalizzato il contenuto della linea che è stato cancellato. più la linea era grande e conteneva testo, più il peso
    # della penalità sarà grande perchè vuol dire che tutta la quantità di contenuto scritto non è stata ritenuta buona
    text = line['text']
    return math.log(1 + len(text))


def calculate_modification_score(line):
    # Questa calcola la penalità da attribuire alla linea. In base al tipo di contenuto modificato si applicano delle penalità diverse
    # per vedere le modifiche in questo caso si può utilizzare l'attributo "highlightRanges"
    # vedere documentazione: https://www.mediawiki.org/wiki/API:REST_API/Reference#Get_page_history
    results = []
    diffs = line['highlightRanges']
    score = 0
    for diff in diffs:
        if diff['type'] == 1:  # vuol dire che è stato rimosso del contenuto
            # penalizzo in base alla lunghezza del contenuto rimosso
            score -= math.log(1 + diff['length'])
        else:
            score += 1  # è stato solo aggiunto del contenuto, quindi quello scritto precedentemente era ritenuto abbastanza buono
    return 0


def check_differences(old_rev, new_rev, user_id, user_rev):
    url = 'https://en.wikipedia.org/w/rest.php/v1/revision/{old}/compare/{new}'
    url = url.format(old=old_rev, new=new_rev)
    headers = {
        'User-Agent': 'MediaWiki REST API docs examples/0.1 (https://www.mediawiki.org/wiki/API_talk:REST_API)'}
    response = requests.get(url, headers=headers)
    data = response.json()
    differences = data['diff']
    review_score = 0
    for diff in differences:
        if diff['type'] == 0:  # la linea è rimasta la stessa nella nuova revisione, quindi FORSE era buona
            review_score += calculate_no_change_score(diff)
        elif diff['type'] == 2:  # la linea è stata cancellata quindi FORSE non era una buona linea
            review_score -= calculate_deletion_score(diff)
        elif diff['type'] == 3:  # linea modificata
            review_score -= calculate_modification_score(diff)
    if user_id in users_dict:
        users_dict[user_id].append((review_score, user_rev))
    else:
        users_dict[user_id] = [(review_score, user_rev)]

def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding='utf-8')
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2,
              sort_keys=False,  ensure_ascii=False)
    # Close the output file
    out_file.close()


if __name__ == "__main__":
    # open the file with the list of all the names of the countries
    f = open("list_of_countries.txt", "r")
    names = f.readlines()
    f.close()

    page = ""
    json_object = {}
    count = 0
    for name in names:
        page = name.strip('\n')
        print("Processing " + page)
        print("\n")
        

        # get the history of the page

        url = 'https://en.wikipedia.org/w/rest.php/v1/page/{page_name}/history'
        url = url.format(page_name=page)

        headers = {
            'User-Agent': 'MediaWiki REST API docs examples/0.1 (https://meta.wikimedia.org/wiki/User:APaskulin_(WMF))'}
        revisions_list = []

        # call the api to get the history of the page
        response = requests.get(url, headers=headers)
        response = json.loads(response.text)
        revisions_list += response['revisions']

        try:
            for i in range(20):  # accumula le ultime 20 * 10 revisioni
                response = requests.get(response['older'], headers=headers)
                response = json.loads(response.text)
                revisions_list += response['revisions']
        except:
            pass

        # itero in ordine inverso per confrontare ogni review con la sua successiva e vedere quali cambiamenti sono stati fatti
        i = len(revisions_list) - 1
        while i > 0:
            try:
                if (revisions_list[i]['minor'] != True):
                    old_rev = revisions_list[i]['id']
                    new_rev = revisions_list[i-1]['id']
                    user_id = revisions_list[i]['user']['id']
                    user_name = revisions_list[i]['user']['name']
                    # solo se la prossima review non è fatta da se stesso
                    if (user_id != revisions_list[i-1]['user']['id'] and "bot" not in user_name):
                        check_differences(old_rev, new_rev, user_id, revisions_list[i-1]['user']['id'] )
            except:
                pass
            i = i - 1


        json_object[name] = users_dict
        users_dict = {}
        count += 1
        if count > 9:
            break
        

        
    save_as_json("users_scores", json_object)
