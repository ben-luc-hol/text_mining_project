import pandas as pd
import requests
from bs4 import BeautifulSoup
import json


#### Scraping  Fox News articles under the Ukraine-Russia heading

## Fox News videos and articles can be accessed with a REST API call, similar to the one on KP's website.
# By FIRST testing the 'from' endpoint in the URL, the dates in question (same as other news orgs) can be approximated in the

test = requests.get('https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fconflicts%2Fukraine&excludeBy=tags&excludeValues=&size=1&from=700')
json_test = test.json()
#data = json.loads(soup)
print(json_test)


date = json_test[0]['publicationDate']
url = json_test[0]['url']
author = json_test[0]['authors'][0]['name']
print(date, url, author)

print(author)

## Start at(from) 401 to 1150 with size=1.
## If you wish to use this API for a topic of your choice, go to a given topic page and use the network utility when inspecting the website in your browser.
## "article-search?searchBy=tag .........." should give you a request URL similar to the one above. Documentation for the API was not found.
headlines = []
dates = []
links = []
authors = []

for i in range(401, 1150):
    r = requests.get(f'https://www.foxnews.com/api/article-search?searchBy=tags&values=fox-news%2Fworld%2Fconflicts%2Fukraine&excludeBy=tags&excludeValues=&size=1&from={i}')
    js = r.json()
    date = js[0]['publicationDate']
    link = js[0]['url']
    headline = js[0]['title']
    try:
        author = js[0]['authors'][0]['name']
    except (KeyError, IndexError):
        author = None
    dates.append(date)
    links.append(link)
    headlines.append(headline)
    authors.append(author)

print(headlines)



# Now, only subheadings and text contents need to be added. Futhermore, video links should be excluded from the data.
# The attributes from above will be added into a dataframe, video links excluded, and subsequently the contents and
#subheadings will be scraped for each article and added.

data = pd.DataFrame({
    'source':'NYTimes',
    'country': 'UnitedStates',
    'link': links,
    'author':authors,
    'published': dates,
    'headline': headlines,
    'subheading':'to be scraped',
    'content': 'to be scraped'
     }
)