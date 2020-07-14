import wikipedia
from bs4 import BeautifulSoup

# Crawl all the names of the countries from the Wikipedia page
# "List of sovereign states"s and save them in a file.
countries_page = wikipedia.page("List of sovereign states")
countries_page = countries_page.html()

soup = BeautifulSoup(countries_page)
table = soup.find_all("table")[0]

# create a file and insert all the name of the continent in that file
f = open("list_of_countries.txt", "w", encoding="utf-8")
for table_row in table.findAll("tr"):
    columns = table_row.findAll("td")
    for column in columns:
        try:
            title = column.findAll("a")[0]
            country_name = title.get("title")
            if (
                country_name is not None
                and country_name != "Member states of the United Nations"
            ):
                f.write(f"{country_name}\n")
        except Exception as e:
            print(e)
        break
f.close()
