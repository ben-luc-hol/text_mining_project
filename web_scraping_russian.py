
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

data.reset_index(inplace=True, drop=True)

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

### Copy dataframe to use for translated data
kp_data_english = data.copy()
#kp_data_english

#Check length of df
#len(data)
#len(kp_data_english)

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

# SAVE THE TRANSLATIONS IN A PICKLE TO AVOID RE-RUNNING TRANSLATION API IN CASE SOMETHING BREAKS
#with open('data/translated_headlines.pkl', 'wb') as f:
#    pickle.dump(translated_headlines, f)

#len(translated_headlines)

#Replacing headline column w/ translated headlines:
kp_data_english['headline'] = translated_headlines

### Translate the subheadings column:

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

#print(translated_subheadings)

#Pickle it
#with open('data/translated_subheadings.pkl', 'wb') as f:
#    pickle.dump(translated_subheadings, f)

# Replace subheading column with translated article subheadings
kp_data_english['subheadings'] = translated_subheadings



### The API is likely to throw an error when hitting overage (2+ million characters).
## Before translating the content, determine the index point at which overage may kick in.
# Azure's free tier student plan does not seem to include overages.

#cumulative_characters = []
#total_chars = 0
#for i, row in data.iterrows():
#    article = row['article_content']
#    article_len = len(article)
#    total_chars += article_len
#    cumulative_characters.append(total_chars)

#limits_data = pd.DataFrame()
#limits_data['cumulative_characters'] = cumulative_characters
#limits_data['over_limit'] = limits_data['cumulative_characters'] >= 2000000 - len_sub - len_head

#print(limits_data.iloc[518:520, :])
## The API should be under the limit up to and including article no. 518 in the index.
# Attempt to translate content until the API alerts that the free quota is hit.
# ** Subsequently switch to pay-as-you-go, and translate the remaining article contents and continue the list.append.


### Translating article content:

translated_contents = []

for i, row in data[:63].iterrows():

    print(f'Requesting translation {i+1}/{len(data[:])} to API. \n')
    # Specify original headline:
    russian_content = row['article_content']

    body = [{
        'text': russian_content
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
    english_content = r_json[0]['translations'][0]['text']
    translated_contents.append(english_content)

    # Progress report
    print(f'Translation {i+1}/{len(data)} successful.\n')


### Translations up to index 62 worked before throwing an error that the API was overloaded.
#with open('data/translated_contents_index0_62.pkl', 'wb')as f:
#    pickle.dump(translated_contents, f)

## Continuing to translate content:

translated_contents_2 = []

for i, row in data[63:144].iterrows():

    print(f'Requesting translation {i+63}/{len(data[:])} to API. \n')
    # Specify original headline:
    russian_content = row['article_content']

    body = [{
        'text': russian_content
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
    english_content = r_json[0]['translations'][0]['text']
    translated_contents_2.append(english_content)

    # Progress report
    print(f'Translation {i+63}/{len(data)} successful.\n')

#print(translated_contents_2)
#len(translated_contents_2)
#with open('data/translated_contents_index62_144.pkl', 'wb')as f:
#    pickle.dump(translated_contents_2, f)

### Start next index at 144
## Continuing:

translated_contents_3 = []

for i, row in data[144:519].iterrows():

   # print(f'Requesting translation {i+145}/{len(data[:])} to API. \n')
    # Specify original headline:
    russian_content = row['article_content']

    body = [{
        'text': russian_content
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
    english_content = r_json[0]['translations'][0]['text']
    translated_contents_3.append(english_content)

    # Progress report
 #   print(f'Translation {i+145}/{len(data)} successful.\n')


#with open('data/translated_contents_index144_209.pkl', 'wb')as f:
#    pickle.dump(translated_contents_3, f)


#### Continuing next batch of translations:

translated_contents_4 = []

for i, row in data[209:519].iterrows():
    #Index error fixed - print status reports on indexes:
    print(f'Requesting translation at dataframe index {i}. \n')
    # Specify original headline:
    russian_content = row['article_content']

    body = [{
        'text': russian_content
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
    english_content = r_json[0]['translations'][0]['text']
    translated_contents_4.append(english_content)

    print(f'Translation successful at dataframe index {i}. \n')

#len(translated_contents_4)

#Concatenate the lists created so far:

all_translated_contents = []
all_translated_contents.extend(translated_contents)
all_translated_contents.extend(translated_contents_2)
all_translated_contents.extend(translated_contents_3)
all_translated_contents.extend(translated_contents_4)
len(all_translated_contents)

### Start next batch at i= 269, see how far it goes:
# Adding 2-second delay  to avoid overloading the API to see if it runs more smoothly
translated_contents_5 = []

for i, row in data[269:519].iterrows():

    print(f'Requesting translation at dataframe index {i}. \n')
    # Specify original headline:
    russian_content = row['article_content']

    body = [{
        'text': russian_content
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
    english_content = r_json[0]['translations'][0]['text']
    translated_contents_5.append(english_content)

    print(f'Translation successful at dataframe index {i}. \n')
    # Adding delay before next translation
    print(f'Next translation at index {i+1} in 2 seconds. \n')
    time.sleep(2)

#len(translated_contents_5)
## This seemed to work. Will be replicated in the next batch.

#Concatenate:
all_translated_contents.extend(translated_contents_5)
#len(all_translated_contents)



## Identify duplicate (fixed in code above - ignore)
#duplicates = set([x for x in all_translated_contents if all_translated_contents.count(x)>1])
#print(enumerate(duplicates))
#delete accidental duplicate
#del all_translated_contents[63]
#duplicates = set([x for x in all_translated_contents if all_translated_contents.count(x)>1])
#len(all_translated_contents)


#with open('data/all_translated_contents_ip.pkl', 'wb') as f:
#    pickle.dump(all_translated_contents, f)


### Attempting to continue translations for content estimated to be above the API quota:
translated_contents_over = []

for i, row in data[519:716].iterrows():

    print(f'Requesting translation at dataframe index {i}. \n')
    # Specify original headline:
    russian_content = row['article_content']

    body = [{
        'text': russian_content
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
    english_content = r_json[0]['translations'][0]['text']
    translated_contents_over.append(english_content)

    # Progress report
    print(f'Translation successful at dataframe index {i}. \n')
    print(f'Next translation at index {i+1} in 2 seconds. \n')
    time.sleep(2)


##### Worked until index 716 At index 716 the free Azure quota is EXCEEDED.
#Concatenate:
all_translated_contents.extend(translated_contents_over)
len(all_translated_contents)


#    NOTE !!!!  AZURE PRICING TIER HAS NOW BEEN UPDATED TO S1 STANDARD.
#    ALL TRANSLATIONS BELOW WILL NOW BE PAY AS YOU GO AND WILL INCUR A COST TO TRANSLATE
#    $10.00 PER 1 MILLION CHARACTERS !!!

translated_contents_paid = []

for i, row in data[716:].iterrows():

    print(f'Requesting translation at dataframe index {i}. \n'
          f'Note: This translation incurs usage fees \n')
    # Specify original headline:
    russian_content = row['article_content']

    body = [{
        'text': russian_content
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
    english_content = r_json[0]['translations'][0]['text']
    translated_contents_paid.append(english_content)

    # Progress report
    print(f'Translation successful at dataframe index {i}. \n')
    print(f'Next translation at index {i+1} in 2 seconds. \n')
    time.sleep(2)


## Final concatenation: all 923 articles translated.

all_translated_contents.extend(translated_contents_paid)
#len(all_translated_contents)

#Pickle just in case
#with open('data/all_translated_contents.pkl', 'wb') as f:
#    pickle.dump(all_translated_contents, f)

## Replacing article content with translated article content
kp_data_english['article_content'] = all_translated_contents


##### Clean up /  translate other columns:
authors = kp_data_english['authors'].unique().tolist()

en_authors = []

for author in authors:

    body = [{
        'text': author
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
    translated_author = r_json[0]['translations'][0]['text']
    en_authors.append(translated_author)

len(authors)
len(en_authors)

#print(en_authors)

author_mapping = {}
for i in range(len(authors)):
    author_mapping[authors[i]] = en_authors[i]

kp_data_english['authors'] = kp_data_english['authors'].map(author_mapping)


## Date translations / formatting:
import dateparser

dates = kp_data_english['published']
formatted_dates = []
for date in dates:
    date_obj = dateparser.parse(date, languages=['ru'])
    parsed_date = date_obj.strftime('%Y-%m-%d')
    formatted_dates.append(parsed_date)

kp_data_english['published'] = formatted_dates



# Save the translated data to file
kp_data_english.to_csv("data/komsomolskaya_pravda_english.csv", index=False)
#kp_data_english.to_parquet("data/komsomolskaya_pravda_english.parquet")

##### END ######