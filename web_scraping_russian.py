import pandas as pd
import requests
import pickle
import time
from bs4 import BeautifulSoup

#### Scraping Komsomolskaya Pravda's "Special Military Operation" topic page

## ## Through inspecting the Network dev tool in Chrome browser,
# API endpoint was identified, which should be easier than scraping the raw HTML.

#Test most recent article page (762) and verifying the other params lead to the
# special operations page. Check the output:

api_url = 'https://s02.api.yc.kpcdn.net/content/api/1/pages/get.json'
params = {
    'pages.direction':'page',
    'pages.number': 762,
    'pages.spot':0,
    'pages.target.class':15,
    'pages.target.id':2995236
}

# Requesting page 762 - the most recent articles
response762 = requests.get(api_url,params)
json_response762 = response762.json()
print(json_response762)

## Examining the JSON output and dictionary structure, it becomes clear
# That class 13 denotes unique articles. It also becomes clear that the
#@id within class 13 is a unique identifier for articles, and that it
#leads to the article in question when pasted into the following link:

# https://www.kp.ru/daily/27473.5/{@id}/

## First, test out extracting these @id values from the dictionary
# from the most recent page requested:
test_kp_list = []
for child in json_response762['childs']:
    for grandchild in child['childs']:
        if grandchild['@class'] == 13:
            article_id = grandchild['@id']
            test_kp_list.append(article_id)

print(test_kp_list)


## NOW: Get ARTICLE IDs for all of Komsomolskaya's coverage from late-November to present:

#Empty list for article ID numbers:
kp_article_ids = []
# Using network dev tool in Chrome, the unique API endpoint for pages under the "special operation"
# topic page in komsomolskaya's coverage was identified.
#The range of articles to be scraped is from 710 (~November 28) to 762 (current).
for page_no in range(710, 762):
    api_url = 'https://s02.api.yc.kpcdn.net/content/api/1/pages/get.json'
    params = {
         'pages.direction':'page',
         'pages.number': page_no,
         'pages.spot':0,
         'pages.target.class':15,
         'pages.target.id':2995236
    }
    response = requests.get(api_url,params)
    json_response = response.json()

    #The JSON file is structured such that 'class 13' denotes articles.
    for child in json_response['childs']:
        for grandchild in child['childs']:
            if grandchild['@class'] == 13:
                article_id = grandchild['@id']
                kp_article_ids.append(article_id)

## Pickle article list to avoid having to re-run above code:

with open('data/kp_article_id.pkl', 'wb') as f:
    pickle.dump(kp_article_ids, f)

#Reload pickle file
with open('data/kp_article_id.pkl', 'rb') as f:
    kp_article_ids = pickle.load(f)

print(kp_article_ids)


# Now, test web scraping for each article's title, date, and content:

#Print the first article to use for scraping purposes -- check link in browser
#print(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[0]}/')
#print(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[1]}/')
#print(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[2]}/')


test_scrape_url = requests.get(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[0]}')

# Dump url into BeautifulSoup:
test_soup = BeautifulSoup(test_scrape_url.text, 'html5lib')

#Write functions to extract key elements:

#Headline
def get_headline(soup_object):
    headline = soup_object.find('h1').text
    return headline
#print(get_headline(test_soup))

#Subheading
def get_subheading(soup_object):
    subheading = soup_object.find('div', class_='sc-j7em19-4 nFVxV')
    return subheading.text
#print(get_subheading(test_soup))

# Body content
def get_content(soup_object):
    p_tags = soup_object.find_all('p', class_='sc-1wayp1z-16 dqbiXu')
    text = [p.get_text() for p in p_tags]
    return text
#print(get_content(test_soup))

#Author
def get_author(soup_object):
    author = soup_object.find('span', class_='sc-1jl27nw-1 bmkpOs').text
    return author
#print(get_author(test_soup))

# Date
def get_date(soup_object):
    published = soup_object.find('span', class_='sc-j7em19-1 dtkLMY').text
    return published
#print(get_date(test_soup))


#Test on random article:

test2 = requests.get(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[500]}/')
test2_text = test2.text

test_soup2 = BeautifulSoup(test2_text, 'html5lib')

print(get_headline(test_soup2))
print(get_subheading(test_soup2))
print(get_date(test_soup2))
print(get_author(test_soup2))
print(get_content(test_soup2))

#test2.status_code
########### GET ARTICLES IN FOR LOOP, STORE ARTICLES

### LISTS

#print(kp_article_ids)

#subprocess.run(['caffeinate'])

headlines = []
subheadings = []
authors = []
dates = []
contents = []

for i, article in enumerate(kp_article_ids[617:]):


    url = f'https://www.kp.ru/daily/27473.5/{article}/'
    response = requests.get(url)

    if response.status_code == 200:

        print(f'# {article} Response Successful. \n')
        print(f'Scraping article {i+1}/{len(kp_article_ids)} with ID {article}\n')

        soup = BeautifulSoup(response.text, 'html5lib')

        try:
            headline = get_headline(soup)
        except:
            print('Headline not found')
            headline = None

        try:
            subheading = get_subheading(soup)
        except:
            print('Subheading not found')
            subheading = None

        try:
            date = get_date(soup)
        except:
            print('Date not found')
            date = None

        try:
            author = get_author(soup)
        except:
            print("Author not found")
            author = None

        try:
            content = get_content(soup)
        except:
            print("Content not found")
            content = None
    else:
        continue
        print(f'{article} not scraped. Skipping.\n')

    if all(x is not None for x in [headline, subheading, date, author, content]):
        headlines.append(headline)
        subheadings.append(subheading)
        authors.append(author)
        dates.append(date)
        contents.append(content)
        print(f"{article} successfully scraped.\n")
    else:
        headlines.append(None)
        subheadings.append(None)
        authors.append(None)
        dates.append(None)
        contents.append(None)
        print(f"{article} not fully scraped. \n")

    print(f'#{article} Complete.\n')
   # time.sleep(3)

#%%

#print(len(headlines))
#print(len(subheadings))
#print(len(authors))
#print(len(dates))
#print(len(contents))

#print(kp_article_ids[616:])

### Save dataframe

data = pd.DataFrame({
    'source':'KomsomolskayaPravda',
    'country': 'Russia',
    'link': [f'https://www.kp.ru/daily/27473.5/{i}/' for i in kp_article_ids],
    'authors':authors,
    'published': dates,
    'headline': headlines,
    'subheadings':subheadings,
    'article_content':contents
})

data.to_csv('data/komsomolskaya_pravda_raw.csv', index=False)
data.to_parquet('data/kp_raw.parquet')

## Remove data with none types
data = pd.read_csv('data/komsomolskaya_pravda_raw.csv')

data = data[data['article_content'].notnull()].copy()




data['article_content'] = data['article_content'].str.strip('[').str.strip(']')
data['article_content'] = data['article_content'].str.strip("'")
data['article_content'] = data['article_content'].str.replace(".', '", ". ")
print(data.iloc[0,7])
data


data
## Translate dataframe
len_head = sum(len(text) for text in data["headline"])
len_sub = sum(len(text) for text in data["subheadings"])
len_cont = sum(len(text) for text in data["article_content"])

print(f'Chars in headlines: {len_head}\n')
print(f'Chars in subheadings: {len_sub}\n')
print(f'Chars in content: {len_cont}\n')
print(f'Total characters to translate: {sum([len_cont,len_sub,len_head])}')


## Microsoft Azure will be used to translate the text data from Russian into English.
## Roughly ~3.5 million characters will be translated. 2 million on free tier, the rest
## Using student credits.

## Test translation on headlines:

from creds.apikeys import translatorKey1
import uuid
import json

endpoint = 'https://api.cognitive.microsofttranslator.com/'
path = '/translate'
location = 'eastus'
key = translatorKey1

url = endpoint+path

headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': location,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

params = {
    'api-version':'3.0',
    'from':'ru'
    'to':'en'

}









