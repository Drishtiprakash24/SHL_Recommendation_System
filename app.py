from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
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

# Load vector DB created from embeddings
vector_db = Chroma(persist_directory="shl_vector_db")

# Load SHL full database for normalization/fallback
shl_df = pd.read_csv("shl_full_database.csv")

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

    # Retrieve top 30 similar assessments first
    results = vector_db.similarity_search_with_score(request.query, k=30)

    if not results:
        return {"recommendations": []}

    # Apply balanced logic
    balanced = balanced_recommendations(results, final_k=request.top_k)

    # Prepare response
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

# ----------------------------
# Run with: uvicorn app:app --reload
# ----------------------------
