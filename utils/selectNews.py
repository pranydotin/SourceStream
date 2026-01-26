import os
from functools import lru_cache

os.environ["CUDA_VISIBLE_DEVICES"] = ""


@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-mpnet-base-v2")


@lru_cache(maxsize=1)
def get_category_model():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    model_name = "pranydotin/distilbert-news-classifier"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    return tokenizer, model


def groupSimilarArticles(articles):
    from sentence_transformers import util
    import numpy as np

    articles = [a for a in articles if a.get("title") and a.get("category")]
    threshold = 0.65

    category_dict = {}
    for a in articles:
        category_dict.setdefault(a["category"], []).append(a)

    clustered_by_category = {}
    model = get_embedding_model()

    for category, cat_articles in category_dict.items():
        titles = [a["title"] for a in cat_articles]
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


def categorize_articles(articles):
    import torch

    tokenizer, model = get_category_model()

    for a in articles:
        title = a.get("title")
        inputs = tokenizer(title, return_tensors="pt")
        outputs = model(**inputs)
        predicted_class = model.config.id2label[
            outputs.logits.argmax().item()
        ]
        a["category"] = predicted_class

    return articles


def select_news_source(articles):
    from utils.db.db_utils import getPreference

    articles = list(articles)

    cat_articles = categorize_articles(articles)
    cluster = groupSimilarArticles(cat_articles)

    final_articles = []

    for category, articles_group in cluster.items():
        for group in articles_group:
            if len(group) == 1:
                final_articles.append(group[0])
                continue

            sources = [article["source"] for article in group]
            preferred_source = getPreference(category, sources)

            for article in group:
                if article["source"] == preferred_source:
                    final_articles.append(article)

    return final_articles
