library(wordcloud)
library(tm)
library(readr)


#Word Clouds

# Read in the text data from the file
rt_text <- readLines('data/processed_data/rt_content_all.txt')
nyt_text <- readLines('data/processed_data/nyt_content_all.txt')
kp_text <- readLines('data/processed_data/kp_content_all.txt')
fnc_text <- readLines('data/processed_data/fnc_content_all.txt')
# Generate the word cloud

## Remove words that are too frequent, see if it changes
exclude_words<- c("ukraine", "ukrainian", "russian", "said", "news", "told", "fox", "also", "russia", "just", "can", "first", "even",
  "end", "yes", "get", "president", "country", "say", "though", "day", "new", "since", "year", "countries", "last", "now", "officials",
  "military", "will", "one", "well", "like", "still", "two", "war")

corpus <- Corpus(VectorSource(rt_text))
corpus <- tm_map(corpus, removeWords, c(stopwords("english"),exclude_words))


wordcloud(words = corpus, scale=c(4,0.5), random.order=FALSE, rot.per=0.35, 
          colors=brewer.pal(8, "Dark2"), max.words=500)


corpus2 <- Corpus(VectorSource(nyt_text))
corpus2 <- tm_map(corpus2, removeWords, c(stopwords("english"),exclude_words))


wordcloud(words = corpus2, scale=c(4,0.5), random.order=FALSE, rot.per=0.35, 
          colors=brewer.pal(8, "Dark2"), max.words=500)




corpus3 <- Corpus(VectorSource(kp_text))
corpus3 <- tm_map(corpus3, removeWords, c(stopwords("english"),exclude_words))


wordcloud(words = corpus3, scale=c(4,0.5), random.order=FALSE, rot.per=0.35, 
          colors=brewer.pal(8, "Dark2"), max.words=500)



corpus4 <- Corpus(VectorSource(fnc_text))
corpus4 <- tm_map(corpus4, removeWords, c(stopwords("english"),exclude_words))


wordcloud(words = corpus4, scale=c(4,0.5), random.order=FALSE, rot.per=0.35, 
          colors=brewer.pal(8, "Dark2"), max.words=200)


exclude_words_k = c()

#### Word clouds for clusters (K-means)

k0 <- readLines('data/unsupervised_data/K0.txt')
k1 <- readLines('data/unsupervised_data/K1.txt')
k2 <- readLines('data/unsupervised_data/K2.txt')
k3 <- readLines('data/unsupervised_data/K3.txt')

xklude <-c("tank", "ukraine", "ukrainian", "russia", "russian", "said", "president", "will", "also", "one", "well", "new", "unit")

korpus0 <- Corpus(VectorSource(k0))
korpus0 <- tm_map(korpus0, removeWords, c(stopwords("english"),xklude))
wordcloud(words = korpus0, scale=c(4,0.5), random.order=FALSE, rot.per=0.35, 
          colors=brewer.pal(8, "Dark2"), max.words=500)


korpus1 <- Corpus(VectorSource(k1))
korpus1 <- tm_map(korpus1, removeWords, c(stopwords("english"),xklude))
wordcloud(words = korpus1, scale=c(4,0.5), random.order=FALSE, rot.per=0.35, 
          colors=brewer.pal(8, "Dark2"), max.words=500)


korpus2 <- Corpus(VectorSource(k2))
korpus2 <- tm_map(korpus2, removeWords, c(stopwords("english"),xklude))
wordcloud(words = korpus2, scale=c(4,0.5), random.order=FALSE, rot.per=0.35, 
          colors=brewer.pal(8, "Dark2"), max.words=500)


korpus3 <- Corpus(VectorSource(k3))
korpus3 <- tm_map(korpus3, removeWords, c(stopwords("english"),xklude))
wordcloud(words = korpus3, scale=c(4,0.5), random.order=FALSE, rot.per=0.35, 
          colors=brewer.pal(8, "Dark2"), max.words=500)

dev.off()



#### Hierarchical Clustering

library(stats)

cluster_data <- read.csv("data/unsupervised_data/clustering_data_tfid400_features.csv")
labels <- read_csv("data/unsupervised_data/clustering_data_tfid400_labels.csv") # load labels too


#dist_matrix <- as.matrix(scale(t(cluster_data)))
#cosine_dist <- 1-crossprod(dist_matrix) /(sqrt(colSums(dist_matrix^2)%*%t(colSums(dist_matrix^2))))


anyNA(cluster_data)

## Matrix is too large!
## Perform PCA:
pca <-  prcomp(cluster_data, scale = TRUE)
plot(pca, type = "l")
summary(pca)


## Extract 4 prinicipal components
pca_data <- as.matrix(pca$x[, 1:4])


class(pca_data)
dim(pca_data)
dist_matrix <- as.matrix(scale(t(pca_data)))


cosine_dist <- 1-crossprod(dist_matrix) /(sqrt(colSums(dist_matrix^2)%*%t(colSums(dist_matrix^2))))
cosine_dist <- as.dist(cosine_dist)

hclust_ward <-  hclust(cosine_dist, method="ward.D")

cut_tree <- stats::cutree(hclust_ward, k=5)

plot(hclust_ward, hang=-1, col=cut_tree)

head(cut_tree)

plot(hclust_ward)
plot(hclust_ward, cex=.7, hang=-30,main = "Cosine Sim")

dist_matrix <-

dim(dist_matrix)



clustering <- hclust(as.dist(dist_matrix), method="ward.D")

plot(clustering)

dend <- as.dendrogram(clustering)

plot(clustering)



# Add labels back to the dendrogram
labels <- labels[order.dendrogram(dend)]
labels_colors <- rainbow(length(labels))[rank(labels)]
labels <- dendextend::hang.dendrogram(dend, hang_height = 0.1, labels_cex = 0.8)
labels <- dendextend::assign_values_to_leaves_nodePar(labels, "label", labels)
labels <- dendextend::assign_values_to_leaves_nodePar(labels, "label_col", labels_colors)

