# -*- coding: utf-8 -*-
import pandas as pd
import json


# File to convert
FILENAME = "user_scores.txt"


def get_name(filename):
    return filename.strip().split(".")[0]


def convert_to_json(filename):
    # List of all the country in the file
    country_names = list()
    # Dictionary representing our JSON object
    json_object = dict()
    # Starting index
    index = -1
    with open(f'{filename}.txt', 'r', encoding='utf-8') as fh:
        for line in fh:
            # Avoid blank lines
            if len(line) > 1:
                splitted_line = line.split(":")
                # Get the country name
                if splitted_line[0] == "COUNTRY":
                    user_ids = dict()
                    country_names.append(splitted_line[1].strip())
                    index += 1
                # Get the scores
                else:
                    scores = splitted_line[2].strip().split(";")
                    scores.remove("")
                    scores = [float(score.strip()) for score in scores]
                # Get the user ids
                if splitted_line[0] == "User ID":
                    user_ids[(splitted_line[1].strip().split()[0])] = scores
                # Update the dictionarty with
                json_object[country_names[index]] = user_ids
    return json_object


def save_as_json(filename, json_object):
    out_file = open(f"{filename}.json", "w", encoding='utf-8')
    # Dump the dictionary as JSON object in the file
    json.dump(json_object, out_file, indent=2,
              sort_keys=False,  ensure_ascii=False)
    # Close the output file
    out_file.close()


def save_as_csv(filename):
    # Open the JSON file
    df = pd.read_json(f'{filename}.json')
    # Save the pd.DataFrame as .csv file
    df.to_csv(f'{filename}.csv', index=None)


if __name__ == "__main__":
    # Remove the extension from the filename
    filename = get_name(FILENAME)
    # From .txt to a JSON object using a dict()
    json_object = convert_to_json(filename)
    # From a dict() to a .json file
    save_as_json(filename, json_object)
    # From a .json file to a .csv file
    save_as_csv(filename)
