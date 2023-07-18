from main import app, db
from models import TShirts

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


        
# Load product data from the database
def load_product_data():
    with app.app_context():
        products = TShirts.query.all()
        return products


# Prepare data
def prepare_data(products):
    corpus = []
    labels = []
    for product in products:
        name = product.name if product.name is not None else ""
        description = product.description if product.description is not None else ""
        gender = product.gender if product.gender is not None else ""
        keywords = product.keywords if product.keywords is not None else ""
        category = product.category if product.category is not None else ""
        size = " ".join(product.size) if product.size is not None else ""
        color = " ".join(product.color) if product.color is not None else ""
        
        corpus.append(name + ' ' + description + ' ' + gender + ' ' + keywords + ' ' + category + ' ' + size + ' ' + color)
        labels.append(product.tshirtId)
        
    return corpus, labels


# Vectorize the data
def vectorize_data(corpus):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    return vectorizer, X



from fuzzywuzzy import fuzz


# def search_products(search_term, top_k=3, max_price=None, min_price=None, category=None):
#     # Load product data from the database
#     products = load_product_data()
#     corpus, labels = prepare_data(products)

#     # Split the search term into words
#     search_words = search_term.lower().split()

#     # Calculate fuzzy match scores for each product name with search words
#     scores = []
#     for product in products:
#         product_name = product.name.lower()
#         score = max(fuzz.partial_ratio(word, product_name) for word in search_words)
#         scores.append(score)

#     # Sort the products based on the fuzzy match scores
#     sorted_products = [product for _, product in sorted(zip(scores, products), key=lambda x: x[0], reverse=True)]

#     # Vectorize the sorted product names for similarity calculation
#     sorted_names = [product.name for product in sorted_products]
#     vectorizer, X = vectorize_data(sorted_names)

#     # Transform the search term
#     search_vector = vectorizer.transform([search_term])

#     # Calculate cosine similarity between search term and products
#     similarity_scores = cosine_similarity(search_vector, X)

#     # Get indices of products sorted by similarity score in descending order
#     sorted_indices = similarity_scores.argsort()[0][::-1]

#     # Reorder the sorted products based on the similarity scores
#     sorted_products = [sorted_products[i] for i in sorted_indices]

#     # Filter products based on price range
#     if max_price is not None and max_price >= 0:
#         sorted_products = [product for product in sorted_products if product.price <= max_price]
#     if min_price is not None and min_price >= 0:
#         sorted_products = [product for product in sorted_products if product.price >= min_price]

#     # Filter products based on category
#     if category is not None:
#         sorted_products = [product for product in sorted_products if product.category.lower() == category.lower()]

#     # Get top-k most similar products
#     top_products = sorted_products[:top_k]

#     return top_products


def search_products(search_term, top_k=3, max_price=None, min_price=None, category=None):
    # Load product data from the database
    products = load_product_data()
    corpus, labels = prepare_data(products)

    # Split the search term into words
    search_words = search_term.lower().split()

    # Sort the products based on the priority of the search term in the name
    sorted_products = sorted(products, key=lambda product: sum(word in product.name.lower() for word in search_words), reverse=True)

    # Vectorize the sorted product names for similarity calculation
    sorted_names = [product.name for product in sorted_products]
    vectorizer, X = vectorize_data(sorted_names)

    # Transform the search term
    search_vector = vectorizer.transform([search_term])

    # Calculate cosine similarity between search term and products
    similarity_scores = cosine_similarity(search_vector, X)

    # Get indices of products sorted by similarity score in descending order
    sorted_indices = similarity_scores.argsort()[0][::-1]

    # Reorder the sorted products based on the similarity scores
    sorted_products = [sorted_products[i] for i in sorted_indices]

    # Filter products based on price range
    if max_price is not None and max_price >= 0:
        sorted_products = [product for product in sorted_products if product.price <= max_price]
    if min_price is not None and min_price >= 0:
        sorted_products = [product for product in sorted_products if product.price >= min_price]

    # Filter products based on category
    if category is not None:
        sorted_products = [product for product in sorted_products if product.category.lower() == category.lower()]

    # Get top-k most similar products
    top_products = sorted_products[:top_k]

    return top_products
