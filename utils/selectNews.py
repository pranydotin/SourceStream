import numpy as np
from sentence_transformers import SentenceTransformer, util
from utils.db.db_utils import getPreference, fetch_categories
import os
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("all-mpnet-base-v2")


def groupSimilarArticles(articles):

    # Ensure articles have a 'category'
    articles = [a for a in articles if a.get('title') and a.get('category')]
    threshold = 0.65

    # Organize articles by category
    category_dict = {}
    for a in articles:
        category_dict.setdefault(a['category'], []).append(a)

    clustered_by_category = {}

    for category, cat_articles in category_dict.items():
        titles = [a['title'] for a in cat_articles]
        embeddings = model.encode(titles, convert_to_tensor=True)
        similarity_matrix = util.cos_sim(embeddings, embeddings).cpu().numpy()

        clusters = []
        visited = set()

        for i in range(len(cat_articles)):
            if i in visited:
                continue
            cluster = [cat_articles[i]]
            visited.add(i)
            for j in range(i + 1, len(cat_articles)):
                if similarity_matrix[i][j] > threshold and j not in visited:
                    cluster.append(cat_articles[j])
                    visited.add(j)
            clusters.append(cluster)

        clustered_by_category[category] = clusters

    return clustered_by_category


def select_news_source(articles):

    articles = [i for i in articles if i['source'] != 'Garhwal Post']
    cat_articles = categorize_articles(articles)

    cluster = groupSimilarArticles(cat_articles)

    final_articles = []
    for category, articles_group in cluster.items():

        for articles in articles_group:
            if len(articles) == 1:
                final_articles.append(articles)
                continue

            sources = [article['source'] for article in articles]
            preferred_source = getPreference(category, sources)
            for article in articles:
                if article['source'] == preferred_source:
                    final_articles.append(article)

    return final_articles


def categorize_articles(articles):
    model_name = "pranydotin/distilbert-news-classifier"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    for a in articles:
        title = a.get('title')
        inputs = tokenizer(title, return_tensors="pt")
        outputs = model(**inputs)
        predicted_class = model.config.id2label[outputs.logits.argmax().item()]
        a['category'] = predicted_class

    return articles
