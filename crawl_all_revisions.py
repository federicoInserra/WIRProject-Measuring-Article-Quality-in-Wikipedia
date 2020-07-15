import requests
import json


def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding="utf-8")
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2, sort_keys=False, ensure_ascii=False)
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
        try:
            page = name.strip("\n")
            print("Processing " + page)
            print("\n")

            # get the history of the page

            url = "https://en.wikipedia.org/w/rest.php/v1/page/{page_name}/history"
            url = url.format(page_name=page)

            headers = {
                "User-Agent": "MediaWiki REST API docs examples/0.1 (https://meta.wikimedia.org/wiki/User:APaskulin_(WMF))"
            }
            revisions_list = []

            # call the api to get the history of the page
            response = requests.get(url, headers=headers)
            response = json.loads(response.text)
            revisions_list += response["revisions"]

            while True:
                try:
                    response = requests.get(response["older"], headers=headers)
                    response = json.loads(response.text)
                    revisions_list += response["revisions"]

                except Exception as e:
                    print(e)
                    break

            json_object[name] = revisions_list
        except Exception as e:
            print(e)
            pass

        count += 1
        if count > 4:
            save_as_json("all_revisions", json_object)
            count = 0

    save_as_json("all_revisions", json_object)

