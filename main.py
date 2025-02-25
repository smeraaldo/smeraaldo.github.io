import requests
import pandas as pd
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

url = "https://www.tiobe.com/tiobe-index/"
tiktokers = []

# Wyslanie żądania do strony (punkt 1).
response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# Wyszukujemy odpowiednią gałąź.
table = soup.find('table', attrs = {'id':'top20'}) 
table = soup.find('tbody')
languages = []
counter = 1 # Dla pozycji języka.

# Iterujemy po wszyskich językach.
for tr in table.find_all('tr'):
    language = {}

    language['Position'] = counter
    counter += 1

    tds = tr.find_all('td')
    language['Name'] = tds[4].text
    language['Ratings'] = tds[5].text
    language['Change'] = tds[6].text

    languages.append(language)

# Wyszukujemy dodatkowe informacje za pomocą DuckDuckGo (punkt 3).
with DDGS() as ddgs:
    for lang in languages:
        lang_name = lang['Name']
        
        # Wyszukiwanie opisu (overview) języka.
        query_info = f"{lang_name} programming language overview"
        info_results = ddgs.text(query_info, max_results=1)
        if info_results:
            lang['Info'] = info_results[0].get('body', 'No description').strip()
            lang['Info_URL'] = info_results[0].get('href', '')
        else:
            lang['Info'] = "No additional information"
            lang['Info_URL'] = ""
        
        # Wyszukiwanie obrazka (logo) języka.
        query_image = f"{lang_name} programming language logo"
        image_results = ddgs.images(query_image, max_results=1)
        if image_results:
            lang['Image'] = image_results[0].get('image', '')
        else:
            lang['Image'] = ""

# Generujemy plik Markdown z tabelą używając pandas (punkt 2).
df = pd.DataFrame(languages)
with open('table.md', 'w', encoding='utf-8') as file:
    file.write('### Popularity of Programming Languages\n\n')
    file.write(df[['Position', 'Name', 'Ratings', 'Change']].to_markdown(index=False))

# Generujemy stronę główną witryny (index.md) w katalogu głównym (punkt 4).
with open("index.md", "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write("layout: default\n")
    f.write("title: Home\n")
    f.write("---\n\n")

    f.write("# Popularity of Programming Languages\n\n")
    f.write("Below is a list of programming languages according to the TIOBE index, along with additional information found on the web.\n\n")
    f.write("| Position | Name | Ratings | Change | Info |\n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for lang in languages:
        # Przygotowanie bezpiecznej nazwy pliku (zamiana spacji i niepożądanych znaków)
        safe_name = lang['Name'].replace(' ', '_').replace('/', '_')
        name_link = f"[{lang['Name']}](./site/{safe_name}.md)"
        info_link = f"[Details]({lang['Info_URL']})" if lang['Info_URL'] else "N/A"
        f.write(f"| {lang['Position']} | {name_link} | {lang['Ratings']} | {lang['Change']} | {info_link} |\n")

# Generujemy podstrony dla każdego języka w katalogu 'site'.
for lang in languages:
    safe_name = lang['Name'].replace(' ', '_').replace('/', '_')
    filename = f"site/{safe_name}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("layout: default\n")
        f.write(f"title: {lang['Name']}\n")
        f.write("---\n\n")

        f.write(f"# {lang['Name']}\n\n")
        f.write(f"**Position:** {lang['Position']}\n\n")
        f.write(f"**Ratings:** {lang['Ratings']}\n\n")
        f.write(f"**Change:** {lang['Change']}\n\n")
        f.write(f"**Overview:** {lang['Info']}\n\n")
        f.write(f"[Additional information]({lang['Info_URL']})\n\n")
        if lang['Image']:
            f.write(f"![Logo]({lang['Image']})\n")