SHL Assessment Recommendation System

---

Problem Overview

The goal of this project is to build an intelligent recommendation system that suggests the most relevant SHL assessments based on a recruiter’s natural language query.
The system returns a balanced mix of assessment types (Knowledge, Personality, Ability) and is evaluated using Recall@K, as required.

---

Solution Overview

The solution is built using:

Semantic Search (Embeddings + Vector DB)

Balanced recommendation logic

FastAPI backend

Streamlit frontend

Recall@K evaluation

---

Architecture

User Query
↓
Embedding Model (HuggingFace MiniLM)
↓
Chroma Vector Database
↓
Balanced Recommendation Logic
↓
FastAPI (JSON Response)
↓
Streamlit UI

---

Tech Stack

Python 3.11

LangChain

ChromaDB

HuggingFace Sentence Transformers

FastAPI

Streamlit

Pandas

Selenium (for scraping SHL data)

---

Project Structure
Assessment_SHL/
│
├── app.py # FastAPI backend
├── streamlit_app.py # Streamlit frontend
├── shl_full_database.csv # Scraped SHL assessments
├── train_data.csv # Labeled training queries
├── test_data.csv # Unlabeled test queries
├── predictions.csv # Final submission predictions
│
├── 01_shl_data_and_embeddings.ipynb
├── 02_balanced_recommendations.ipynb
├── 03_evaluation_recall_at_k.ipynb
│
├── requirements.txt
├── README.md
└── .gitignore

---

How to Run Locally

1.Create Virtual Environment
python -m venv venv
venv\Scripts\activate

2.Install Dependencies
pip install -r requirements.txt

3.Run FastAPI Backend
uvicorn app:app --reload

API will be available at:

http://127.0.0.1:8000

Test endpoint:

POST /recommend

4.Run Streamlit Frontend
streamlit run streamlit_app.py

Evaluation

Metric used: Recall@10

Mean Recall@10 achieved: 0.5

Balanced recommendation logic significantly improved recall compared to pure similarity search.

---


Key Highlights

Semantic understanding of recruiter intent

Balanced assessment type distribution

Scalable architecture

Clean separation of experimentation, evaluation, API, and UI
