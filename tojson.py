# -*- coding: utf-8 -*-

import json

# File to convert
filename = 'user_scores.txt'
# List of all the country in the file
country_names = list()
# Dictionary representing our JSON object
json_object = dict()
# Starting index
index = -1

with open(filename, 'r', encoding='utf-8') as fh:
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
                scores = [score.strip() for score in scores]
            # Get the user ids
            if splitted_line[0] == "User ID":
                user_ids[(splitted_line[1].strip().split()[0])] = scores
            # Update the dictionarty with
            json_object[country_names[index]] = user_ids

# Open the output file
out_file = open("user_scores.json", "w", encoding='utf-8')
# Dump the dictionary as JSON object in the file
json.dump(json_object, out_file, indent=2, sort_keys=False,  ensure_ascii=False)
# Close the output file
out_file.close()

