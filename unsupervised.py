import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

### K-means Clustering

# Data prep:
# Using LEMMATIZED data for clustering:
cluster_data = pd.read_csv('data/processed_data/lemmatized_data.csv')

cluster_data = cluster_data.dropna()
cluster_data
#Limit to article content only:

labels = cluster_data['source']
labels

cluster_data = cluster_data['content']

cluster_data
# Use top 400 features:

tfid400 = TfidfVectorizer(input= 'content',
                           stop_words='english',
                           max_features=400)

data = tfid400.fit_transform(cluster_data)
colnames = tfid400.get_feature_names()
data = pd.DataFrame(data.toarray(), columns=colnames)


labels.to_csv('data/unsupervised_data/clustering_data_tfid400_labels.csv', index=False)
data.to_csv('data/unsupervised_data/clustering_data_tfid400_features.csv', index=False)


### K-means Clustering

#First, find optimal k:

scores = []
for k in range(2,12):
    kmeans = KMeans(n_clusters = k)
    kmeans.fit(data)
    average_silhouette = silhouette_score(data, kmeans.labels_)
    scores.append(average_silhouette)

fig = plt.figure(figsize=(10,6))
plt.plot(range(2,12), scores)
plt.xlabel('No. of clusters')
plt.ylabel('Silhouette score')
plt.title('Silhouette Method for Optimal K')
plt.savefig('data/unsupervised_data/kmeansViz1.png')
plt.show()


# K-means with two clusters:
k2 = KMeans(n_clusters=2)
k2.fit(data)
k2_prediction = k2.predict(data)

cluster_data = pd.DataFrame(cluster_data)
cluster_data.insert(0,'Source',labels)
cluster_data.insert(1,'K=2', k2_prediction)
cluster_data['K=2'] = cluster_data['K=2'].astype('category')
cluster_data

counts = cluster_data['K=2'].value_counts()

# % observations by cluster:
percentages = counts / len(cluster_data['K=2'])*100

# Bar chart:
fig, ax = plt.subplots()
bars = ax.bar(percentages.index, percentages.values)
ax.set_xlabel('Cluster')
plt.xticks(range(len(percentages.index)), percentages.index)
ax.set_ylabel('Percentage')
ax.set_ylim(0, 100)

for i, v in enumerate(percentages.values):
    ax.text(i, v + 1, "{:.1f}%".format(v), ha='center')
plt.savefig('data/unsupervised_data/kmeansViz2.png')
plt.show()


#Distribution within clusters:

grouped = cluster_data.groupby(['Source', 'K=2']).size().unstack(fill_value=0)
percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100

percentages = percentages.T
percentages

total_articles_by_source = grouped.sum(axis=1)
source_percentages = grouped.div(total_articles_by_source, axis=0) * 100


for column in percentages.columns:
    ax = percentages[column].plot(kind='bar')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Percentage')
    ax.set_title(f'Source {column}')
    ax.set_ylim([0, 100])

    # add percentage labels to each bar
    for i, v in enumerate(percentages[column]):
        ax.text(i, v + 2, "{:.1f}%".format(v), ha='center')

    plt.savefig(f'data/unsupervised_data/KMeansViz_K2_{column}.png')
    plt.show()



# K-means with three clusters:


k3 = KMeans(n_clusters=3)
k3.fit(data)
k3_prediction = k3.predict(data)


cluster_data.insert(2,'K=3', k3_prediction)
cluster_data

counts = cluster_data['K=3'].value_counts()
counts
# % observations by cluster:
percentages = counts / len(cluster_data['K=3'])*100
percentages
# Bar chart:
fig, ax = plt.subplots()
bars = ax.bar(percentages.index, percentages.values)
ax.set_xlabel('Cluster')
plt.xticks(range(len(percentages.index)), percentages.index)
ax.set_ylabel('Percentage')
ax.set_ylim(0, 100)

for i, v in enumerate(percentages.values):
    ax.text(i, v + 1, "{:.1f}%".format(v), ha='center')
plt.savefig('data/unsupervised_data/kmeansViz3.png')
plt.show()


#Distribution within clusters:

grouped = cluster_data.groupby(['Source', 'K=3']).size().unstack(fill_value=0)
percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100

percentages = percentages.T
percentages

total_articles_by_source = grouped.sum(axis=1)
source_percentages = grouped.div(total_articles_by_source, axis=0) * 100


for column in percentages.columns:
    ax = percentages[column].plot(kind='bar')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Percentage')
    ax.set_title(f'Source {column}')
    ax.set_ylim([0, 100])

    # add percentage labels to each bar
    for i, v in enumerate(percentages[column]):
        ax.text(i, v + 2, "{:.1f}%".format(v), ha='center')

    plt.savefig(f'data/unsupervised_data/KMeansViz_K3_{column}.png')
    plt.show()




# K-means with four clusters:

k4 = KMeans(n_clusters=4)
k4.fit(data)
k4_prediction = k4.predict(data)


cluster_data.insert(3,'K=4', k4_prediction)
cluster_data ['K=4'] = k4_prediction
cluster_data

counts = cluster_data['K=4'].value_counts().sort_index()
counts
# % observations by cluster:
percentages = counts / len(cluster_data['K=4'])*100
percentages
# Bar chart:
fig, ax = plt.subplots()
bars = ax.bar(percentages.index, percentages.values)
ax.set_xlabel('Cluster')
plt.xticks(range(len(percentages.index)), percentages.index)
ax.set_ylabel('Percentage')
ax.set_ylim(0, 50)

for i, v in enumerate(percentages.values):
    ax.text(i, v + 1, "{:.1f}%".format(v), ha='center')
plt.savefig('data/unsupervised_data/kmeansViz4.png')
plt.show()


#Distribution within clusters:

grouped = cluster_data.groupby(['Source', 'K=4']).size().unstack(fill_value=0)
percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100

percentages = percentages.T
percentages

total_articles_by_source = grouped.sum(axis=1)
source_percentages = grouped.div(total_articles_by_source, axis=0) * 100

grouped
for column in percentages.columns:
    ax = percentages[column].plot(kind='bar')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Percentage')
    ax.set_title(f'Source {column}')
    ax.set_ylim([0, 100])

    # add percentage labels to each bar
    for i, v in enumerate(percentages[column]):
        ax.text(i, v + 2, "{:.1f}%".format(v), ha='center')

    plt.savefig(f'data/unsupervised_data/KMeansViz_K4_{column}.png')
    plt.show()


cluster_data.to_csv('data/unsupervised_data/cluster_predictions_content.csv', index=False)

cluster_data

K0 = cluster_data[cluster_data['K=4'] == 0]
K0 = K0['content']
K0 = " ".join(K0)
K0
with open('data/unsupervised_data/K0.txt', 'w') as file:
    file.write(K0)


K1 = cluster_data[cluster_data['K=4'] == 1]
K1 = K1['content']
K1 = " ".join(K1)
K1

with open('data/unsupervised_data/K1.txt', 'w') as file:
    file.write(K1)

K2 = cluster_data[cluster_data['K=4'] == 2]
K2 = K2['content']
K2 = " ".join(K2)
K2

with open('data/unsupervised_data/K2.txt', 'w') as file:
    file.write(K2)

K3 = cluster_data[cluster_data['K=4'] == 3]
K3 = K3['content']
K3 = " ".join(K3)
K3

with open('data/unsupervised_data/K3.txt', 'w') as file:
    file.write(K3)



# Data Prep for ARM

## Ngram on headlines

#Where did the NAs go? What happened? Mismatch in length must be accounted for.
lemma = pd.read_csv('data/processed_data/lemmatized_data.csv')
kmeans_lemma = pd.read_csv('data/unsupervised_data/cluster_predictions_content.csv')


data = pd.merge(lemma, kmeans_lemma, on = 'content', how='left')

K4_predictions = data['K=4']
K4_predictions.to_csv('data/unsupervised_data/KMEANS_PREDICTIONS_FULL_LENGTH_DATA.csv', index= False)


arm_data = pd.read_csv('data/processed_data/stemmed_data.csv')

## Ignore FutureWarning spam
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)



arm_data.insert(2, 'kmeans', K4_predictions)

arm_data = arm_data[['source','published', 'kmeans', 'headline_summary']]
arm_data.isna().sum()
arm_data = arm_data.dropna()
arm_data.isna().sum()
arm_data

arm_data_prelim = arm_data['headline_summary']

arm_data_prelim


arm_vectorizer = CountVectorizer(input= 'content',
                                 stop_words='english',
                                 max_features=175,
                                 ngram_range= 2)



arm_vectorized = arm_vectorizer.fit_transform(arm_data_prelim)
colnames = arm_vectorizer.get_feature_names()
arm_vectorized = pd.DataFrame(arm_vectorized.toarray(), columns=colnames)

arm_vectorized

arm_vectorized.to_csv('data/unsupervised_data/arm_data_1.csv', index = False)

arm_vectorized = pd.DataFrame(arm_vectorized)
arm_vectorized.insert(0, 'source', arm_data['source'])
arm_vectorized.insert(1, 'source', arm_data['source'])

arm_vectorized


### Latent Dirichlet Allocation