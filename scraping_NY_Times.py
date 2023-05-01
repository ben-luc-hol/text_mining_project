#*******************************************************************************************************************************************

#*****************                   U.S. MEDIA COVERAGE OF THE WAR IN UKRAINE (NY TIMES)            *********************

#*************************************************************************************************************************




import pickle
import time
import datetime as dt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

#### Scraping  New York Times articles under the Ukraine-Russia heading

### The NY Times keeps a topic page on the Russia-Ukraine war at nytimes.com/news-event/ukraine-russia.
# This is a dynamic infinite-scroll type website, meaning that regular scraping with requests will not
# Render all of the articles.

# For this, use selenium & webdriver to simulate a user to scroll and scrape"

## Initialize options and instantiate the webdriver (Chrome)
options = webdriver.ChromeOptions()
#options.headless = True

driver = webdriver.Chrome(service=ChromeService(
    ChromeDriverManager().install()), options=options)

## URL to be scraped:
url = 'https://www.nytimes.com/news-event/ukraine-russia#stream-panel'

driver.get(url)
#Add a wait time to ensure the website loads (2s)
wait = WebDriverWait(driver, 15)
time.sleep(2)
#wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.css-1aia2tm')))

# Press "search" tab to get a full list of articles that allows for a smoother scroll
search_tab = driver.find_element(By.XPATH, '//span[text()="Search"]')
#nav_element = driver.find_element(By.CLASS_NAME, 'css-m3796d')
#search_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Search"]')))
# "Click" the search tab
search_tab.click()
#nav_element.click()

# Scrape list of articles starting 11/26 (same date as KP)
stop_date_string = 'November 26, 2022'
# Convert string to datetime - This is the oldest article date to scrape from the NY Times:
stop_date = dt.datetime.strptime(stop_date_string, '%B %d, %Y')

##### Simulate scrolling down the page, wait, load more elements
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span[data-testid="todays-date"]')))
    date_elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-testid="todays-date"]')
    if not date_elements:
        break

    # While the latest date on the site (currently displayed) is greater than the cutoff date, keep scrolling to the bottom of the page
    last_date_string = date_elements[-1].text.strip()
    last_date = dt.datetime.strptime(last_date_string, '%B %d, %Y')
    # Stop scrolling if the last date is less than / equal to the stop_date:
    if last_date <= stop_date:
        break

    time.sleep(2)
    scroll_element = driver.find_elements((By.TAG_NAME, 'html'))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

# Get the final html
html = driver.page_source

#Put in bs4 to parse
soup = BeautifulSoup(html, 'html5lib')

# Define function to get article links, append
def get_links(soup_object):
    article_links = soup_object.find_all('div', {'class':'css-1l4spti'})
    links = []
    for article in article_links:
        link = article.find('a', href=True)
        href = link['href']
        links.append(f'https://www.nytimes.com{href})
    return links

# Get list of NY times article links
ny_times_links = get_links(soup)


print(ny_times_links)

# Save list to pickle
with open('data/ny_times_links.pkl', 'wb') as f:
    pickle.dump(ny_times_links, f)


#*******************************************************************************************************************************************

#*****************                   LOOPING THROUGH ARTICLES AND SCRAPING TEXT CONTENTS            *********************

#*************************************************************************************************************************

from requests_html import HTMLSession

## Ensure that credentials are given (logged in with my personal NY Times account with an active subscription)

from creds.logins import nytimesEmail
from creds.logins import nytimesPassword
import pickle
from bs4 import BeautifulSoup
import time
import pandas as pd

with open('data/ny_times_links.pkl', 'rb') as file:
    ny_times_links = pickle.load(file)


print(ny_times_links[5])


session = HTMLSession()

login_url = 'https://myaccount.nytimes.com/auth/login'
credentials = {'username':nytimesEmail, 'password': nytimesPassword}
session.post(login_url, credentials)

test_url = 'https://www.nytimes.com/2023/03/06/world/europe/ukraine-bakhmut-battle.html'
test_response = session.get(test_url)

test_soup = BeautifulSoup(test_response.text, 'html5lib')

print(test_soup)


def get_headline(soup_object):
    headline = soup_object.find('h1').text
    return headline

get_headline(test_soup)


def get_summary(soup_object):
    summary = soup_object.find('p', class_='css-1n0orw4 e1wiw3jv0')
    if summary is not None:
        return summary.text
    else:
        summary = soup_object.find('p', class_ = 'css-y47omd e1wiw3jv0')
        if summary is not None:
            return summary.text
        else:
            return None


get_summary(test_soup)


def get_content(soup_object):
    p_tags = soup_object.find_all('p', class_='css-at9mc1 evys1bk0')
    text = [p.get_text() for p in p_tags]
    return text

get_content(test_soup)

#Author
def get_author(soup_object):
    author_tags = soup_object.find_all('a', class_='css-n8ff4n e1jsehar0')
    authors = [a.text for a in author_tags]
    return authors

get_author(test_soup)

# Date
#def get_date(soup_object):
#    published = soup_object.find('span', class_='css-1sbuyqj e16638kd3').text
#    return published
#
#get_date(test_soup)


#### Loop over the articles in the NY Times articles list. Append each article to empty dataframe:


headlines = []
summaries = []
authors = []
dates = []
contents = []

for i, link in enumerate(ny_times_links):
    response = session.get(link)

    if response.status_code == 200:
        print(f'# {link} Response Successful. \n')
        print(f'Scraping article {i+1}/{len(ny_times_links)} with link {link}\n')

        soup = BeautifulSoup(response.text, 'html5lib')

        # Run pre-defined functions to get article elements, return None if an exception is raised
        try:
            headline = get_headline(soup)
        except:
            print('Headline not found')
            headline = None

        try:
            summary = get_summary(soup)
        except:
            print('Summary not found')
            summary = None

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
        print(f'{link} not scraped. Skipping to next.\n')

    # Append successfully scraped elements to corresponding empty lists; append 'None' if an exception was raised for the field,
    # This ensures that the lists are of same length and with each appended element corresponding to those in other lists by index
    if headline is not None:
        headlines.append(headline)
    else:
        headlines.append(None
                         )
    if summary is not None:
        summaries.append(summary)
    else:
        summaries.append(None)
    dates.append(date)
    if author is not None:
        authors.append(author)
    else:
        authors.append(None)
    if content is not None:
        contents.append(content)
    else:
        contents.append(None)
    print(f'#{link} Complete.\n')

    time.sleep(1)

len(headlines)
len(summaries)
len(authors)
len(contents)


## There was a problem with finding the dates. Instead, use dates given from link

data = pd.DataFrame({
    'source':'NYTimes',
    'country': 'UnitedStates',
    'link': ny_times_links,
    'author':authors,
    'published': ny_times_links,
    'headline': headlines,
    'summary':summaries,
    'content':contents
})

data


data.to_csv('data/NYT_raw.csv', index=False)