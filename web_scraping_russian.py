
import pandas as pd
from creds.apikeys import newsKey
from creds.apikeys import twitterKey
import requests
import pickle
import json
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

response762 = requests.get(api_url,params)
json_response762 = response762.json()
print(json_response762)

## Examining the JSON output:
# CLASS 13 DENOTES UNIQUE ARTICLES WHICH SHOULD WORK
## WITH THE LINK https://www.kp.ru/daily/27473.5/{ARTICLE ID}/

## Test list-append code to extract article IDs:

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

# Now, test web scraping for each article's title, date, and content:

#Print the first article to use for scraping purposes -- check link in browser
print(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[0]}')

test_scrape_url = requests.get(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[0]}')