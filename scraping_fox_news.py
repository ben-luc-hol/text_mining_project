import pandas as pd
import requests
from bs4 import BeautifulSoup
import re


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
#print(headlines)

# Now, only subheadings and text contents need to be added. Futhermore, video links should be excluded from the data.
# The attributes from above will be added into a dataframe, video links excluded, and subsequently the contents and
#subheadings will be scraped for each article and added.

data = pd.DataFrame({
    'source':'FoxNews',
    'country': 'UnitedStates',
    'link': [f'https://www.foxnews.com{link}' for link in links],
    'author':authors,
    'published': dates,
    'headline': headlines,
    'subheading':'to be scraped',
    'content': 'to be scraped'
     }
)

### Filter out video links


data_without_video = data[~data['link'].str.contains('video')].copy()

data_without_video


fox_news_links = data_without_video['link'].tolist()

fox_news_links[50]



test_article = requests.get(fox_news_links[50])
test_soup = BeautifulSoup(test_article.text, 'html5lib')

test_soup

print(fox_news_links[155])
test_article2 = requests.get(fox_news_links[155])
test_soup2 = BeautifulSoup(test_article2.text, 'html5lib')


## Defining function to extract article text ONLY.
# The FNC articles are riddled with other text that is classified under the same text class
# As the content itself. Through painstaking trial and error, and identifying

def get_content(soup_object):
    # Only the article body should be included.
    article_body = soup_object.find({'div':'article-body'})
    # All article text is under the tag '<p>' in the html. Extract this text.
    p_tags = article_body.find_all('p')
    text = [p.get_text() for p in p_tags]
    #This renders a list of paragraphs (text). In each, the first two and the final four elements of
    # The list are reliably NOT a part of the actual article. These are removed:
    text = text[2:-4]
    # Then, a lot of text in ALL CAPS or that does not end with a period, are not relevant to the article.
    #These are removed by specifying to keep only text that is not upper case and that ends with a period. (regex)
    text = [paragraph for paragraph in text if not paragraph.isupper() and re.search(r'\.$', paragraph)]
    #Joining the paragraphs...
    content = "".join(text)
    #And voilá:
    return content

# This works on both tests:
get_content(test_soup)
get_content(test_soup2)

# Then, get the subheading:
def get_subhead(soup_object):
    subhead = soup_object.find('h2')
    text = subhead.get_text()
    return text

get_subhead(test_soup)
get_subhead(test_soup2)



## Looping through Fox News articles under the Ukraine-Russia war tag (some articles may not be as relevent)
# And scraping contents and subheadlines:
subheadings = []
contents = []

for i, link in enumerate(fox_news_links):
    response = requests.get(link)

    if response.status_code == 200:
        print(f'# {link} Response Successful. \n')
        print(f'Scraping article {i+1}/{len(fox_news_links)} with link {link}\n')

        soup = BeautifulSoup(response.text, 'html5lib')

        # Run pre-defined functions to get article elements, return None if an exception is raised
        try:
            subhead = get_subhead(soup)
        except:
            print('Subheading not found')
            headline = None
        try:
            content = get_content(soup)
        except:
            print('Content not found')
            content = None
    # If connection unsuccessful, skip to next article
    else:
        continue
        print(f'{link} not scraped. Skipping to next.\n')

    # Append successfully scraped elements to corresponding empty lists; append 'None' if an exception was raised for the field,
    # This ensures that the lists are of same length and with each appended element corresponding to those in other lists by index
    if subhead is not None:
        subheadings.append(subhead)
    else:
        subheadings.append(None)
    if content is not None:
        contents.append(content)
    else:
        contents.append(None)

    print(f'#{link} Complete.\n')


print(subheadings)
print(contents)

data_without_video['subheading'] = subheadings
data_without_video['content'] = contents

data_without_video.to_csv('data/fox_news_raw.csv', index= False)
