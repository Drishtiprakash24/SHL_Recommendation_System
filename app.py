from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# ----------------------------
# Request/Response Models
# ----------------------------
class RecommendRequest(BaseModel):
    query: str
    top_k: int = 10  # default 10 recommendations

class Assessment(BaseModel):
    name: str
    url: str
    test_type: str
    score: float
    reason: str

class RecommendResponse(BaseModel):
    recommendations: List[Assessment]

# ----------------------------
# Initialize App & DB
# ----------------------------
app = FastAPI(title="SHL Assessment Recommendation API")

VECTOR_DB_DIR = "shl_vector_db"
CSV_FILE = "shl_full_database.csv"

embeddings = HuggingFaceEmbeddings()

# Build vector DB if it doesn't exist
if not os.path.exists(VECTOR_DB_DIR):
    print("Vector DB not found. Building from CSV...")
    shl_df = pd.read_csv(CSV_FILE)
    texts = shl_df['name'].tolist()
    metadatas = shl_df.to_dict(orient="records")
    vector_db = Chroma.from_texts(texts, embeddings, metadatas=metadatas, persist_directory=VECTOR_DB_DIR)
    vector_db.persist()
else:
    vector_db = Chroma(persist_directory=VECTOR_DB_DIR)

# Load SHL CSV for fallback (optional)
shl_df = pd.read_csv(CSV_FILE)

# ----------------------------
# Balanced Recommendation Logic
# ----------------------------
def balanced_recommendations(results, final_k=10):
    type_dict = {"K": [], "P": [], "A": []}
    for doc, score in results:
        ttype = doc.metadata.get("test_type", "K")
        if ttype in type_dict:
            type_dict[ttype].append((doc, score))

    num_types = len([v for v in type_dict.values() if v])
    per_type = max(final_k // num_types, 1)

    balanced = []
    for items in type_dict.values():
        balanced.extend(items[:per_type])

    if len(balanced) < final_k:
        remaining = [r for r in results if r not in balanced]
        balanced.extend(remaining[:final_k - len(balanced)])

    return balanced[:final_k]

# ----------------------------
# Health Check Endpoint
# ----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ----------------------------
# Assessment Recommendation Endpoint
# ----------------------------
@app.post("/recommend", response_model=RecommendResponse)
def recommend_assessments(request: RecommendRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Retrieve top 30 similar assessments
    results = vector_db.similarity_search_with_score(request.query, k=30)
    if not results:
        return {"recommendations": []}

    balanced = balanced_recommendations(results, final_k=request.top_k)

    recommendations = []
    for doc, score in balanced:
        recommendations.append(
            Assessment(
                name=doc.metadata.get("name", ""),
                url=doc.metadata.get("url", ""),
                test_type=doc.metadata.get("test_type", ""),
                score=round(score, 4),
                reason=f"Recommended due to strong relevance to '{request.query}'"
            )
        )

    return {"recommendations": recommendations}

# Run with: uvicorn app:app --reload
