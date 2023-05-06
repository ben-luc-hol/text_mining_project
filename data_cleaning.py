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
#data.to_csv('data/All_Articles_Clean.csv', index=False)

data
##### Creating various datasets:

from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

dates = data['published']
dates
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


stemmed_data.insert(1, 'published', data['published'])

stemmed_data.to_csv('data/processed_data/stemmed_data.csv', index = False)


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



lemmed_data.insert(1, 'published', data['published'])


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



preprocessed_data.insert(1, 'published', data['published'])
preprocessed_data.to_csv('data/processed_data/preprocessed_data.csv', index = False)



# Count vectorizer:

vectorizer100 = CountVectorizer(input='content',
                                stop_words='english',
                                max_features=100)


headlines_01 = preprocessed_data['headline_summary']
headlines_01

CV_headlines_1 = vectorizer100.fit_transform(headlines_01)
colnames = vectorizer100.get_feature_names()
CV100_headlines_full = pd.DataFrame(CV_headlines_1.toarray(), columns = colnames)
CV100_headlines_full.insert(0,'LABEL', source_label)
CV100_headlines_full.to_csv('data/processed_data/headlines_unaltered_CV_100.csv', index=False)


headlines_02 = stemmed_data['headline_summary']

CV_headlines_2 = vectorizer100.fit_transform(headlines_02)
colnames = vectorizer100.get_feature_names()
colnames
CV100_headlines_stemmed = pd.DataFrame(CV_headlines_2.toarray(), columns = colnames)
CV100_headlines_stemmed.insert(0,'LABEL', source_label)

CV100_headlines_stemmed.to_csv('data/processed_data/headlines_stemmed_CV_100.csv', index=False)



headlines_03 = lemmed_data['headline_summary']

CV_headlines_3 = vectorizer100.fit_transform(headlines_03)
colnames = vectorizer100.get_feature_names()
colnames
CV100_headlines_lemmed = pd.DataFrame(CV_headlines_3.toarray(), columns = colnames)
CV100_headlines_lemmed.insert(0,'LABEL', source_label)

CV100_headlines_lemmed
CV100_headlines_stemmed.to_csv('data/processed_data/headlines_lemmed_CV_100.csv', index=False)


### CONTENT (Top 250 features)

vectorizer250 = CountVectorizer(input='content',
                                stop_words='english',
                                max_features=250)



content_01 = preprocessed_data['content']
content_01

CV_content_1 = vectorizer250.fit_transform(content_01)
colnames = vectorizer250.get_feature_names()
CV250_content_full = pd.DataFrame(CV_content_1.toarray(), columns = colnames)
CV250_content_full.insert(0,'LABEL', source_label)
CV250_content_full

CV250_content_full.to_csv('data/processed_data/content_unaltered_CV_250.csv', index=False)


content_02 = stemmed_data['content']
content_02

CV_content_2 = vectorizer250.fit_transform(content_02)
colnames = vectorizer250.get_feature_names()
CV250_content_stemmed = pd.DataFrame(CV_content_2.toarray(), columns = colnames)
CV250_content_stemmed.insert(0,'LABEL', source_label)
CV250_content_stemmed

CV250_content_stemmed.to_csv('data/processed_data/content_stemmed_CV_250.csv', index=False)



content_03 = lemmed_data['content']

CV_content_3 = vectorizer250.fit_transform(content_03)
colnames = vectorizer250.get_feature_names()
CV250_content_lemmed = pd.DataFrame(CV_content_3.toarray(), columns = colnames)
CV250_content_lemmed.insert(0,'LABEL', source_label)
CV250_content_lemmed

CV250_content_lemmed.to_csv('data/processed_data/content_lemmed_CV_250.csv', index=False)


## Ngrams:

content_01 = preprocessed_data['content']

n_vectorizer12000 = CountVectorizer(input='content',
                                    stop_words='english',
                                    max_features=12000,
                                    ngram_range=(2,4))


CV_content_4 = n_vectorizer12000.fit_transform(content_01)
colnames= n_vectorizer12000.get_feature_names()
CV12000_content_orig = pd.DataFrame(CV_content_4.toarray(), columns = colnames)
CV12000_content_orig.insert(0,'LABEL', source_label)

CV12000_content_orig.to_csv('data/processed_data/CV_ngrams_12000.csv', index = False)


n_vectorizer1000 = CountVectorizer(input='content',
                                    stop_words='english',
                                    max_features=1000,
                                    ngram_range=(5,5))

#New ngram dataframe:
content_01 = preprocessed_data['content']

n_vectorizer1000 = CountVectorizer(input='content',
                                    stop_words='english',
                                    max_features=1000,
                                    ngram_range=(4,4))


CV_content_5 = n_vectorizer1000.fit_transform(content_01)
colnames= n_vectorizer1000.get_feature_names()
CV1000_content_orig = pd.DataFrame(CV_content_5.toarray(), columns = colnames)
CV1000_content_orig.insert(0,'LABEL', source_label)

CV1000_content_orig

CV1000_content_orig.to_csv('data/processed_data/CV_ngrams_1000.csv', index = False)


#### TDIF


tfid1000 = TfidfVectorizer(input= 'content',
                           stop_words='english',
                           max_features=1000)


TF1000_content_orig = tfid1000.fit_transform(content_01)
colnames = tfid1000.get_feature_names()
TF1000_content_orig = pd.DataFrame(TF1000_content_orig.toarray(), columns=colnames)
TF1000_content_orig.insert(0,'LABEL', source_label)

TF1000_content_orig.to_csv('data/processed_data/TF_original_1000.csv')




n_tfid1000 = TfidfVectorizer(input= 'content',
                           stop_words='english',
                           max_features=1000,
                            ngram_range=(4,4))


TF1000_content_orig_ngram = n_tfid1000.fit_transform(content_01)
colnames = n_tfid1000.get_feature_names()
TF1000_ngram = pd.DataFrame(TF1000_content_orig_ngram.toarray(), columns=colnames)
TF1000_ngram.insert(0,'LABEL', source_label)

TF1000_ngram.to_csv('data/processed_data/TF_ngrams_1000.csv', index = False)







