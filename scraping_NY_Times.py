#*******************************************************************************************************************************************

#*****************                   U.S. MEDIA COVERAGE OF THE WAR IN UKRAINE (NY TIMES)            *********************

#*************************************************************************************************************************


import pandas as pd
import requests
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
from selenium.webdriver.common.action_chains import ActionChains

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

## Import the pickled list of article links


## Ensure that credentials are given (logged in with my personal NY Times account with an active subscription)
from creds.logins import nytimesEmail
from creds.logins import nytimesPassword

