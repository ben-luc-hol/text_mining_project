import pandas as pd
import subprocess
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

for article in kp_article_ids:
    url = f'https://www.kp.ru/daily/27473.5/{article}/'
    response = requests.get(url)

    if response.status_code == 200:
        print(f'# {article} Response Successful. \n')
        soup = BeautifulSoup(response.text, 'html5lib')

        try:
            headline = get_headline(soup)
            subheading = get_subheading(soup)
            date = get_date(soup)
            author = get_author(soup)
            content = get_content(soup)

            headlines.append(headline)
            subheadings.append(subheading)
            authors.append(author)
            dates.append(date)
            content.append(content)

            print(f" #{article} Successfully Scraped.\n")

        except Exception as e:
            print(f'#{article} Scraping Yielded {e}. Skipping.\n')
            continue

    else:
        print(f'# {article} Scraping Yielded Code {response.status_code}. Skipping.\n')
        continue

    print(f'#{article} Complete. Next Scrape in 10 Seconds.')
    time.sleep(10)

data = pd.DataFrame({
    'source':'KomsomolskayaPravda',
    'country': 'Russia',
    'headline': headlines,
    'subheadings':subheadings,
    'published': dates,
    'article_content':contents
})
#%%
