import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import wikipedia
from wikipedia.exceptions import DisambiguationError

wikipedia.set_lang("en")
url = "https://www.tiobe.com/tiobe-index/"

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

# Wyszukujemy dodatkowe informacje za pomocą DuckDuckGo i wikipedia api (punkt 3).
def get_wikipedia_summary(lang_name):
    search_results = wikipedia.search(lang_name.replace('#', ' Sharp') + "(programming language)")
    if search_results:
        try:
            page = wikipedia.page(search_results[0], auto_suggest=False)
        except DisambiguationError as e:
            page = wikipedia.page(e.options[0], auto_suggest=False)
        return page.summary, page.url
    else:
        return "No summary found.", ""

with DDGS() as ddgs:
    for lang in languages:
        lang_name = lang['Name']
        
        # Wyszukiwanie opisu (overview) języka za pomocą wikipedii.
        summary, url = get_wikipedia_summary(lang_name)
        lang['Info'] = summary
        lang['Info_URL'] = url
        
        # Wyszukiwanie obrazka (logo) języka.
        query_image = f"wikipedia {lang_name} programming language logo"
        image_results = ddgs.images(query_image, max_results=1)
        if image_results:
            lang['Image'] = image_results[0].get('image', '')
        else:
            lang['Image'] = ""
        
        # Wyszukiwanie przykładu kodu "Hello world" w tym języku.
        query_image = f"Hello World program in {lang_name}"
        image_results = ddgs.images(query_image, max_results=1)
        if image_results:
            lang['Hello_World'] = image_results[0].get('image', '')
        else:
            lang['Hello_World'] = ""

# Generujemy witrynę (index.md).
with open("index.md", "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write("layout: default\n")
    f.write("title: Home\n")
    f.write("---\n\n")

    f.write("# **20 Most Popular Programming Languages ​​According to the TIOBE Index.** \n\n")
    f.write("_The TIOBE Programming Community Index_ is an indicator of the popularity of programming languages. The index is updated _once a month_. The ratings are based on the number of qualified engineers worldwide, courses, and third-party providers. Popular websites _Google, Amazon, Wikipedia, Bing, and over 20 others_ are used to calculate the ratings. It is important to note that the TIOBE Index is not about the best programming language or the language in which the most lines of code are written. The index can be used to check whether your programming skills are still up to date or to make a strategic decision about which programming language to adopt when starting to build a new software system. \n")
    f.write("There are also images, short descriptions, and links to additional information for each language: \n\n")
    f.write("[List of languages](table.md)")

# Generujemy listę (table.md) w katalogu głównym (punkt 4).
with open("table.md", "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write("layout: default\n")
    f.write("title: Table\n")
    f.write("---\n\n")

    f.write("# Popularity of Programming Languages\n\n")
    f.write("Below is a list of programming languages according to the TIOBE index, click on the name to find more information.\n\n")
    f.write("| Position | Logo | Name | Ratings | Change | \n")
    f.write("| --- | --- | --- | --- | --- |\n")
    for lang in languages:
        # Przygotowanie bezpiecznej nazwy pliku (zamiana spacji i niepożądanych znaków).
        safe_name = lang['Name'].replace(' ', '_').replace('/', '_').replace('#', 'Sharp')
        page_link = f"[{lang['Name']}](./site/{safe_name}.md)"

        if lang['Image']:
            logo_md = f'<img src="{lang["Image"]}" alt="logo" width="30"/>'
        else:
            logo_md = " "

        f.write(f"| {lang['Position']} | {logo_md} | {page_link} | {lang['Ratings']} | {lang['Change']} |\n")

# Generujemy podstrony dla każdego języka w katalogu 'site'.
for lang in languages:
    safe_name = lang['Name'].replace(' ', '_').replace('/', '_').replace('#', 'Sharp')
    filename = f"site/{safe_name}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write("layout: default\n")
        f.write(f"title: {lang['Name']}\n")
        f.write("---\n\n")

        f.write(f'# <img src="{lang["Image"]}" alt="logo" width="30"/>')
        f.write(f"**{lang['Name']}** (_№{lang['Position']}_) \n\n")
        f.write(f"**Ratings:** {lang['Ratings']} | **Change:** {lang['Change']} \n\n")
        f.write(f"**Overview:** {lang['Info']}\n\n")

        if lang['Info_URL']:
            f.write(f"Below you can find example of writing 'Hello World' in {lang['Name']} and here some [additional information]({lang['Info_URL']})\n\n")
        if lang['Hello_World']:
            f.write(f"![Hello_World]({lang['Hello_World']})\n")
