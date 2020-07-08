import wikipedia
from bs4 import BeautifulSoup

# CRAWL ALL THE NAMES OF THE COUNTRIES FROM THE WIKIPEDIA PAGE LIST OF COUNTRIES AND SAVE THEM IN A FILE

countries_page = wikipedia.page("List of sovereign states")
countries_page = countries_page.html()

soup = BeautifulSoup(countries_page)
table = soup.find_all('table')[0] 

#create a file and insert all the name of the continent in that file

f = open("list_of_countries", 'w')
for table_row in table.findAll('tr'):

    columns = table_row.findAll('td')
    for column in columns:

        try:
            
            title = column.findAll('a')[0]
            country_name = title.get('title')
            if country_name != None and country_name != "Member states of the United Nations":
                f.write(country_name)
                f.write("\n")
            
            
        except:
            pass

        break

f.close()

    
    






