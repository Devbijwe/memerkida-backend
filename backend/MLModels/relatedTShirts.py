import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import TShirts
from main import app

# Retrieve T-shirt data from the database and preprocess if needed
with app.app_context():
    tshirts = TShirts.query.with_entities(
        TShirts.tshirtId,
        TShirts.gender,
        TShirts.price,
        TShirts.color,
        TShirts.size,
        TShirts.name,
        TShirts.description,
        TShirts.category,
        TShirts.keywords
    ).all()

# Prepare data for feature extraction
tshirt_ids, genders, prices, colors, sizes, names, descriptions, categories, keywords = zip(*tshirts)
corpus = [f"{gender} {price} {color} {size} {name} {description} {category} {keywords}" for gender, price, color, size, name, description, category, keywords in zip(genders, prices, colors, sizes, names, descriptions, categories, keywords)]

# Perform feature extraction using TF-IDF
vectorizer = TfidfVectorizer()
features = vectorizer.fit_transform(corpus)

# Convert features to NumPy array for efficient calculations
features = features.toarray()

# Calculate pairwise cosine similarity
cosine_sim = cosine_similarity(features)

def get_related_tshirts(tshirt_id, top_n=5):
    try:
        # Get the index of the target T-shirt
        tshirt_index = tshirt_ids.index(tshirt_id)
    except ValueError:
        print(f"T-shirt ID '{tshirt_id}' not found in the dataset.")
        return []

    # Calculate cosine similarity scores for all T-shirts
    scores = list(enumerate(cosine_sim[tshirt_index]))

    # Sort the T-shirts based on similarity scores
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # Get top N related T-shirts
    top_tshirts = [(tshirt_ids[idx], score) for idx, score in scores[1:top_n + 1]]

    return top_tshirts