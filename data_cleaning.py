import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt

nytimes = pd.read_csv('data/NYT_raw.csv')
pravda = pd.read_csv('data/komsomolskaya_pravda_english.csv')
russiatoday = pd.read_csv('data/russia_today_raw.csv')
foxnews = pd.read_csv('data/fox_news_raw.csv')


## Cleaning up NYTimes

clean_nytimes = nytimes.copy()

print(clean_nytimes['author'])


#Cleaning up author names
#def join_authors(col):
#    names = col.replace('[', '').replace(']', '').replace('\'', '').split(', '),
#    return names

#test = nytimes['author'].apply(join_authors)


## Cleadning up publishing date column
clean_nytimes['published'] = clean_nytimes['published'].str.extract(r'/(\d{4}/\d{2}/\d{2})/')
clean_nytimes['published'] = pd.to_datetime(clean_nytimes['published']).dt.strftime('%Y-%m-%d')


# Cleaning up author column
def clean_names(c):
    c = re.sub(r"[^a-zA-Z,. ]", "",c)
    return c


clean_nytimes['author'] = clean_nytimes['author'].apply(clean_names)

clean_nytimes['content'] = clean_nytimes['content'].str.strip("['']")

#clean_nytimes.to_csv('data/NYT_clean.csv', index = False)



## Clean up Pravda

pravda_clean = pravda.copy()

pravda_clean['author'] = pravda_clean['author'].apply(lambda x: x.title())

pravda_clean


## Clean up fox

foxnews_clean = foxnews.copy()

foxnews_clean['published'] = foxnews_clean['published'].apply(lambda x: datetime.fromisoformat(x))
foxnews_clean['published'] = pd.to_datetime(foxnews_clean['published']).dt.strftime('%Y-%m-%d')

foxnews_clean['content'][0]

foxnews_clean['content'][42]


foxnews_clean = foxnews_clean[foxnews_clean['content'].str.len()>500].copy()


plt.hist(foxnews_clean[foxnews_clean['content'].str.len()<500]['content'].str.len(), bins=100)
plt.title('Distribution of Article Character Length')
plt.xlabel('Number of Characters')
plt.ylabel('Frequency')
plt.show()


### Remove all articles under length of 500

#foxnews_clean = foxnews_clean[foxnews_clean['content'].str.len() > 500].copy()

foxnews_clean



# Clean up RT:

russiatoday_clean = russiatoday.copy()
russiatoday_clean['published'] = russiatoday_clean['published'].apply(lambda x: x.strip())
russiatoday_clean['published'] = russiatoday_clean['published'].apply(lambda x: datetime.strptime(x, '%b %d, %Y %H:%M'))
russiatoday_clean['published'] = russiatoday_clean['published'].apply(lambda x: x.strftime('%Y-%m-%d'))

russiatoday_clean['headline'] = russiatoday_clean['headline'].apply(lambda x: x.strip('\n').strip())
russiatoday_clean['subheading'] = russiatoday_clean['subheading'].apply(lambda x: x.strip('\n').strip())


russiatoday_clean

## Join all articles into the same df:

# Harmonize column names
list(clean_nytimes.columns)
list(pravda_clean.columns)
list(foxnews_clean.columns)
list(russiatoday_clean.columns)

cols = list(clean_nytimes.columns)

pravda_clean.columns = cols
foxnews_clean.columns = cols
russiatoday_clean.columns = cols

# Join

data = pd.concat([clean_nytimes, pravda_clean, foxnews_clean, russiatoday_clean], ignore_index=True)
data = data.sort_values('published', ascending=False)
data = data.reset_index(drop=True)
data.to_csv('data/All_Articles_Clean.csv', index=False)

data
##### Creating various datasets:

from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer



# Content - Stemming

#Labels
source_label = data['source']

source_label
country_label = data['country']


## Stemming

stemmer = PorterStemmer()

#Labeled data of content using stemming:
def stem_text(text):
    text = re.sub(r"[^a-zA-Z]+", " ", text)
    text = text.lower()
    words = text.split()
    stemmed_words = [stemmer.stem(word) for word in words]
    stemmed_text = " ".join(stemmed_words)
    return stemmed_text

stemmed_data = data[['source', 'headline', 'summary', 'content']].copy()
stemmed_data['headline_summary'] = (stemmed_data['headline'].fillna('') + ' ' + stemmed_data['summary'].fillna(''))
stemmed_data.drop(columns=['headline', 'summary'], axis=1, inplace=True)
stemmed_data['content'] = stemmed_data['content'].apply(stem_text)
stemmed_data['headline_summary'] = stemmed_data['headline_summary'].apply(stem_text)

stemmed_data.to_csv('data/processed_data/stemmed_data.csv')


## Lemmatized data:

#Do this first if wordnet is not already installed:
#import nltk
#nltk.download('wordnet')


lemmatizer = WordNetLemmatizer()

def lem_text(text):
    text = re.sub(r"[^a-zA-Z]+", " ", text)
    text = text.lower()
    words = text.split()
    lem_words = [lemmatizer.lemmatize(word) for word in words]
    lem_text = " ".join(lem_words)
    return lem_text


lemmed_data = data[['source', 'headline', 'summary', 'content']].copy()
lemmed_data['headline_summary'] = (lemmed_data['headline'].fillna('') + ' ' + lemmed_data['summary'].fillna(''))
lemmed_data.drop(columns=['headline', 'summary'], axis=1, inplace=True)
lemmed_data['content'] = lemmed_data['content'].apply(lem_text)
lemmed_data['headline_summary'] = lemmed_data['headline_summary'].apply(lem_text)

lemmed_data.to_csv('data/processed_data/lemmatized_data.csv', index = False)


## Clean dataset without stemming or lemming:

def clean_text(text):
    text = re.sub(r"[^a-zA-Z]+", " ", text)
    text = text.lower()
    return text

preprocessed_data = data[['source', 'headline', 'summary', 'content']].copy()
preprocessed_data['headline_summary'] = (preprocessed_data['headline'].fillna('') + ' ' + preprocessed_data['summary'].fillna(''))
preprocessed_data.drop(columns=['headline', 'summary'], axis=1, inplace=True)
preprocessed_data['content'] = preprocessed_data['content'].apply(clean_text)
preprocessed_data['headline_summary'] = preprocessed_data['headline_summary'].apply(clean_text)

preprocessed_data.to_csv('data/processed_data/preprocessed_data.csv/')


## 6 datasets with count vectorizer:

vectorizer = CountVectorizer(input=)

dataframes = [preprocessed_data, stemmed_data, lemmed_data]




## 6 datasets with tdifvectorizer:





