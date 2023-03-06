import pandas as pd
from creds.apikeys import newsKey
from creds.apikeys import twitterKey
import requests
from bs4 import BeautifulSoup
import json


newsKey = newsKey

## Sources
url = f'https://newsapi.org/v2/everything/sources?apiKey={newsKey}'
s = requests.get(url)
s = s.json()
print(s)

### Russian Language news - February 24
#q=Украина?
#Russian Language news articles mentioning Ukraine:

#With a free account it's not possible to get more than 100 results.

url = 'https://newsapi.org/v2/everything?'
params = {
    'language':'ru',
    'q':'Украина',
    'from':'2023-02-04',
    'to':'2023-03-03',
    'pageSize': 100,
    'apiKey': newsKey,
    'excludeDomains': 'https://consent.google.com/ml?continue=https://news.google.com'
}


r1 = requests.get(url, params=params)
data1 = json.loads(r1.text)
print(data1)




#total_articles = ru_data['totalResults']

## Too many API requests for free tier to work. limited to max 100 results
##
#articles = []
#for page in range(1, (total_articles // params['pageSize']) + 2):
#    params['page'] = page
#    r = requests.get(url, params=params)
#    data = json.loads(r.text)
#    articles.append(data['articles'])

#for article in articles:
#    print(article['title'])



with open('data/russian_news.json', 'w') as f:
    json.dump(data1, f)



####################
# Parsing Russian news articles:
# Information to be retained includes:
# * Title
# * Source
# * Description
# * Link
# * Content


# In order to perform analysis in a comparable way with news sources in other languages,
# the articles will be TRANSLATED TO ENGLISH.
# (Figure out a way to scrape the content html?)

with open('data/russian_news.json', 'r') as f:
    russian_articles = json.load(f)


print(russian_articles)

articles = russian_articles['articles']
titles = [article['title'] for article in articles]
sources = [article['source']['name'] for article in articles]
descriptions = [article['description'] for article in articles]
links = [article['url'] for article in articles]

russian_articles_df = pd.DataFrame({
    'title':titles,
    'source':sources,
    'description':descriptions,
    'link':links
})

russian_articles_df

## Russian articles sources:
#print(russian_articles_df['source'].value_counts())

## Yields
#Lenta           79
#Google News     15
#Vedomosti.ru     5
#3dnews.ru        1
#Name: source, dtype: int64



#Lenta.
test_link = russian_articles_df.iloc[0,3]
print(test_link)
test_html = requests.get(test_link)
print(test_html)
soup = BeautifulSoup(test_html.text, 'html.parser')
#article_element = soup.find('div', {'class':'articleBody'})
#print(article_element)
article_text = soup.get_text()
print(article_text)


#Google News




