import requests
import pandas as pd
page = requests.get("https://en.wikipedia.org/wiki/List_of_Conan_episodes_(2018)")

from bs4 import BeautifulSoup
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())

#soup.find_all('td')
#
#for link in soup.select("td a"):
#    print("{} -- {}".format(link.get('href'), link.get('title')))
    

from bs4 import BeautifulSoup
soup = BeautifulSoup(page.content, 'lxml')
print(soup.prettify())

new_table = pd.DataFrame()
table = soup.find_all('table', class_='wikitable plainrowheaders')[0]
table
row_marker = 0
for row in table.find_all('tr'):
        column_marker = 0
        columns = row.find_all('td')
        for column in columns:
            new_table.iat[row_marker,column_marker] = column.get_text()
            column_marker += 1
        row_marker +=1
    
new_table