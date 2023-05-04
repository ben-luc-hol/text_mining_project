import requests
from bs4 import BeautifulSoup
import pandas as pd
import itertools


test_url = 'https://www.rt.com/listing/trend.5a8da18adda4c85e788b459b/prepare/trend-news/6/80'

test_response = requests.get(test_url)

print(test_response.content)

test_soup = BeautifulSoup(test_response.content, 'html5lib')

def get_headline(soup_object):
    tags = soup_object.find_all('div', class_='list-card__content--title link_hover')
    headlines = []
    for tag in tags:
        headlines.append(tag.text)
    return headlines

get_headline(test_soup)


def get_links(soup_object):
    tags = soup_object.find_all('div', class_='list-card__content--title link_hover')
    links = []
    for tag in tags:
        a_tag = tag.find('a', class_ = 'link_hover')
        if a_tag:
            links.append(a_tag['href'])
    return links

get_links(test_soup)

def get_dates(soup_object):
    tags = soup_object.find_all('div', class_='list-card__content')
    dates = []
    for tag in tags:
        date_tag = tag.find('div', class_="card__date")
        if date_tag:
            date = date_tag.find('span', class_='date').text
            dates.append(date)
    return dates

def get_summary(soup_object):
        tags = soup_object.find_all('div', class_='list-card__content--summary')
        summaries = []
        for tag in tags:
            summaries.append(tag.text)
        return summaries


get_summary(test_soup)

test_url2 = 'https://www.rt.com/listing/trend.5a8da18adda4c85e788b459b/prepare/trend-news/6/166'

test_response2 = requests.get(test_url2)

test_soup2 = BeautifulSoup(test_response2.content, 'html5lib')
get_dates(test_soup2)

## API only callable back to January 18. These should be scraped anyway just to have more data.

## To get same dates, start from 80 (March 8 as of now) in API and iterate through 166.
headlines = []
links = []
dates = []
summaries = []

for i in range(80, 167):
    url = f'https://www.rt.com/listing/trend.5a8da18adda4c85e788b459b/prepare/trend-news/6/{i}'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    h = get_headline(soup)
    d = get_dates(soup)
    l = get_links(soup)
    s = get_summary(soup)

    headlines.append(h)
    dates.append(d)
    links.append(l)
    summaries.append(s)

print(dates)

working = "".join(dates)

print(working)

#flatten the lists before joining into df:

dates = list(itertools.chain.from_iterable(dates))
headlines = list(itertools.chain.from_iterable(headlines))
links = list(itertools.chain.from_iterable(links))
summaries = list(itertools.chain.from_iterable(summaries))



data = pd.DataFrame({
    'source':'RussiaToday',
    'country': 'Russia',
    'link': [f'https://www.rt.com{link}' for link in links],
    'author':'',
    'published': dates,
    'headline': headlines,
    'subheading': summaries,
    'content': 'to be scraped'
})

data

rt_links = list(data['link'])

rt_links[355]
#rt_links[175]

test3 = requests.get(rt_links[175])
test_soup_3 = BeautifulSoup(test3.content, 'html5lib')


def get_content(soup_object):
    article = soup_object.find('div', class_='article__text text').text
    return article


### RT does not typically list an Author. For this dataset, an author will not be scraped.
contents = []
for i, link in enumerate(rt_links):
    r = requests.get(link)

    if r.status_code == 200:
        print(f'# {link} \n Response Successful. \n')
        print(f'Scraping article {i+1}/{len(rt_links)} with link {link}:\n')

        soup = BeautifulSoup(r.content, 'html5lib')

        # Run pre-defined functions to get article elements, return None if an exception is raised
        try:
            content = get_content(soup)
        except:
            print('Content could not be scraped.')
            content = None
    # If connection unsuccessful, skip to next article
    else:
        continue
        print(f'{link} not scraped. Skipping to next.\n')

    # Append successfully scraped elements to corresponding empty lists; append 'None' if an exception was raised for the field,
    # This ensures that the lists are of same length and with each appended element corresponding to those in other lists by index
    if content is not None:
        contents.append(content)
    else:
        contents.append(None)
    print(f'#{link} Complete.\n')


data['content'] = contents

data.to_csv('data/russia_today_raw.csv', index=False)



