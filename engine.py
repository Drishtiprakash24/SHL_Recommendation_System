import pandas as pd
from sentence_transformers import SentenceTransformer, util

# 1. Load your crawled data
db = pd.read_csv('shl_full_database.csv')
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Pre-calculate embeddings for the whole catalog (Do this once)
catalog_embeddings = model.encode(db['search_content'].tolist(), convert_to_tensor=True)

def get_recommendations(query, top_k=10):
    # 3. Encode the user query
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # 4. Compute cosine similarity
    hits = util.semantic_search(query_embedding, catalog_embeddings, top_k=top_k)
    
    # 5. Extract the results
    results = []
    for hit in hits[0]:
        idx = hit['corpus_id']
        results.append({
            "Assessment Name": db.iloc[idx]['Assessment Name'],
            "URL": db.iloc[idx]['URL'],
            "Score": hit['score']
        })
    return pd.DataFrame(results)

# Test with your sample query
query = "I am hiring for Java developers who can also collaborate effectively..."
print(get_recommendations(query))