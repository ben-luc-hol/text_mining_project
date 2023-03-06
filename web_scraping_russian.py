
#*******************************************************************************************************************************************

#*****************                   RUSSIAN LANGUAGE MEDIA COVERAGE OF THE WAR IN UKRAINE            **************************************

#*******************************************************************************************************************************************

# Import required libraries for scraping and formatting data:

import pandas as pd
import requests
import pickle
import time
from bs4 import BeautifulSoup

#*******************************************************************************************************************************************

#*****************                   LOCATING KOMSOMOLSKAYA PRAVDA TEXT DATA                            ************************************

#*******************************************************************************************************************************************



#### Scraping Komsomolskaya Pravda's "Special Military Operation" topic page

# Topic URL found here: https://www.kp.ru/daily/euromaidan/


# Used browser inspect and network dev tool to familiarize with the website/html structure.
# Website contains "load more" button.
# Using network tool, the website was found to be structured in pages containing article links,
# where each 'load more' click calls an API to load another page of articles.

# API endpoint was identified, structure was studied.
# This is more convenient than attempting to simulate 'load more' clicks and scraping the html directly.

# As of March 5, the most recent article page = 762.
# API params were verified to lead to the correct topic page.

## Testing API call on most recent article directory page:

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

## This was successful.

## When examining the JSON output and dictionary structure, it becomes clear that 'class 13' in the dictionary contains
# information on unique articles.

# '@id' within class 13 is identified as a unique identifier for articles.
# This article ID number can evidently be pasted directly into the following link, which leads directly to a given article:

# https://www.kp.ru/daily/27473.5/{@id}/

## First, test out extracting these @id values from the dictionary (using the most recent articles page):
test_kp_list = []
for child in json_response762['childs']:
    for grandchild in child['childs']:
        if grandchild['@class'] == 13:
            article_id = grandchild['@id']
            test_kp_list.append(article_id)

# This successfully produces a list of unique article IDs!!
print(test_kp_list)


##  *****   Get ARTICLE IDs for all of KP's war coverage from late-November to present:

#Empty list for article ID numbers:
kp_article_ids = []

# Using network dev tool in Chrome, the unique API endpoint for pages under the "special operation"
# topic page in komsomolskaya's coverage was identified.

#The range of articles to be scraped is from 710 (~November 28) to 762 (current).
# Loop through the articles pages to scrape all class 13 article IDs:
for page_no in range(710, 762):
    api_url = 'https://s02.api.yc.kpcdn.net/content/api/1/pages/get.json'

    ## Correct API parameters were identified with Chrome inspect tools
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
    #Extract the article IDs only and append to empty list:
    for child in json_response['childs']:
        for grandchild in child['childs']:
            if grandchild['@class'] == 13:
                article_id = grandchild['@id']
                kp_article_ids.append(article_id)


## Save article IDs list as a pickle file to avoid having to re-run above code - Just in case:

with open('data/kp_article_id.pkl', 'wb') as f:
    pickle.dump(kp_article_ids, f)


#*******************************************************************************************************************************************

#*****************                   SCRAPING & SAVING KOMSOMOLSKAYA PRAVDA ARTICLES                            ****************************

#*******************************************************************************************************************************************


#Reload pickle file with list of unique KP articles:

with open('data/kp_article_id.pkl', 'rb') as f:
    kp_article_ids = pickle.load(f)

# Ensure the list was loaded right
#print(kp_article_ids)


# Now, test web scraping for each article's title, date, and content:

#Print the first article to use for scraping purposes --  checking link in browser
#print(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[0]}/')
#print(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[1]}/')
#print(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[2]}/')


# Testing the first URL to article:
test_scrape_url = requests.get(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[0]}')

# Using bs4 to parse the article's html structure:
test_soup = BeautifulSoup(test_scrape_url.text, 'html5lib')


# By inspecting the website in the browser, the specific elements (classes) to be scraped
# were identified. Functions below extract these core elements:

# * Headline of article
# * Subheading of article
# * Author of article
# * Date and time published
# * Text content/ body of article


#Writing functions to extract key elements:

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


#Testing functions on random article:

test2 = requests.get(f'https://www.kp.ru/daily/27473.5/{kp_article_ids[500]}/')
print(f'Status: {test2.status_code}\n')
test2_text = test2.text
test_soup2 = BeautifulSoup(test2_text, 'html5lib')

print(f'Test Headline: {get_headline(test_soup2)} \n')
print(f'Test Subheading: {get_subheading(test_soup2)} \n')
print(f'Test Author: {get_author(test_soup2)} \n')
print(f'Test Date: {get_date(test_soup2)} \n')
print(f'Test Content: {get_content(test_soup2)}')


## Functions were successful!




########### GET ARTICLES IN FOR LOOP, STORE ARTICLES


# Caffeinate computer (mac OS) if necessary:
#subprocess.run(['caffeinate'])


## Empty lists to append headline, subheading, author, date, and content elements scraped from kp.ru HTML:
headlines = []
subheadings = []
authors = []
dates = []
contents = []

## Loop through the article IDs scraped in the above code
for i, article in enumerate(kp_article_ids):

    # Paste article ID into the "special military operation" topic link
    url = f'https://www.kp.ru/daily/27473.5/{article}/'

    # Request article endpoint html
    response = requests.get(url)

    # Run script if connection successful
    if response.status_code == 200:

        print(f'# {article} Response Successful. \n')
        print(f'Scraping article {i+1}/{len(kp_article_ids)} with ID {article}\n')

        # bs4 object to parse html
        soup = BeautifulSoup(response.text, 'html5lib')

        # Run pre-defined functions to get article elements, return None if an exception is raised
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
    # If connection unsuccessful, skip to next article
    else:
        continue
        print(f'{article} not scraped. Skipping.\n')

    # Append successfully scraped elements to corresponding empty lists; append 'None' if an exception was raised for the field,
    # This ensures that the lists are of same length and with each appended element corresponding to those in other lists by index
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

   # Consider spacing out scrapes by x seconds to avoid excessive server requests, if necessary:
   # time.sleep(3)

#%%

# Ensure the lists are of same size:
#print(len(headlines))
#print(len(subheadings))
#print(len(authors))
#print(len(dates))
#print(len(contents))



### SAVE RAW DATAFRAME:

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
#data.to_parquet('data/kp_raw.parquet')


#*******************************************************************************************************************************************

#*****************                   TRANSLATE KOMSOMOLSKAYA PRAVDA TEXT DATA                         **************************************

#*******************************************************************************************************************************************

from creds.apikeys import translatorKey1
import uuid
import json


data = pd.read_csv('data/komsomolskaya_pravda_raw.csv')

## REMOVE ARTICLES CONTAINING 'NONE'
data = data[data['article_content'].notnull()].copy()



## Strip some strings from the content
data['article_content'] = data['article_content'].str.strip('[').str.strip(']')
data['article_content'] = data['article_content'].str.strip("'")
data['article_content'] = data['article_content'].str.replace(".', '", ". ")

# Print 1 content observation to ensure that it worked
# Russian language does not use apostrophes, stripping them will not interfere with translation
# since any apostrophes will have emerged from data formatting.

print(data.iloc[0,7])


## 3 Columns to translate. Determine the number of characters contained in each"
len_head = sum(len(text) for text in data["headline"])
len_sub = sum(len(text) for text in data["subheadings"])
len_cont = sum(len(text) for text in data["article_content"])

print(f'Chars in headlines: {len_head}\n')
print(f'Chars in subheadings: {len_sub}\n')
print(f'Chars in content: {len_cont}\n')
print(f'Total characters to translate: {sum([len_cont,len_sub,len_head])}')


## Microsoft Azure will be used to translate the text data from Russian into English.

##  ~3.5 million characters will be translated. 2 million on free tier, the rest using academic use credits.

## Initialize Translation API
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


# Run translation on the headline column (73192 characters):

### Testing the translation code on a single headline:

test_headline = data.loc[12, 'headline']
print(f'Russian headline: {test_headline}\n')

params = {
    'api-version': '3.0',
    'from': 'ru',
    'to': 'en'
}

body = [{
    'text': test_headline
}]

r_test = requests.post(url, params=params, headers=headers, json=body)
re_test = r_test.json()

print(f'Dictionary structure of translation:\n {re_test}\n')

print(f'Translated headline: {re_test[0]["translations"][0]["text"]}\n')




### Create emptu translated dataset:
kp_data_english = data
#kp_data_english


#### Translate the headline column:

# Empty list of translated headlines:

translated_headlines = []

for i, row in data.iterrows():

    # Specify original headline:
    russian_headline = row['headline']

    body = [{
        'text': russian_headline
    }]
    # Set params
    params = {
        'api-version': '3.0',
        'from': 'ru',
        'to': 'en'
    }
    # Post request to translation API
    r = requests.post(url, params=params, headers=headers, json=body)
    r_json = r.json()

    # Extract the translated text from the API response and store it in the translated_data DataFrame
    english_headline = r_json[0]['translations'][0]['text']
    translated_headlines.append(english_headline)



print(translated_headlines)

kp_data_english['headline'] = translated_headlines




### TRANSLATE SUBHEADINGS:

translated_subheadings = []

for i, row in data.iterrows():

    print(f'Requesting translation {i+1}/{len(data)} to API. \n')
    # Specify original headline:
    russian_subheading = row['subheadings']

    body = [{
        'text': russian_subheading
    }]
    # Set params
    params = {
        'api-version': '3.0',
        'from': 'ru',
        'to': 'en'
    }
    # Post request to translation API
    r = requests.post(url, params=params, headers=headers, json=body)
    r_json = r.json()

    # Extract the translated text from the API response and store it in the translated_data DataFrame
    english_subheading = r_json[0]['translations'][0]['text']
    translated_subheadings.append(english_subheading)

    # Progress report
    print(f'Translation {i+1}/{len(data)} successful.\n')


kp_data_english['subheadings'] = translated_subheadings
kp_data_english







### The API is likely to throw an error when hitting overage (2+ million characters).
## Before translating the content, 




# Save the translated data to a file
translated_data.to_csv("translated_data_file.csv", index=False)







