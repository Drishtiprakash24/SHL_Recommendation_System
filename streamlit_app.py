import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/recommend"

st.set_page_config(page_title="SHL Assessment Recommender", layout="centered")

st.title("🔍 SHL Assessment Recommendation System")
st.write("Enter a job role or skill description to get relevant SHL assessments.")

query = st.text_area(
    "Job Role / Skill Description",
    placeholder="e.g. Backend developer with Python, APIs, databases",
)

top_k = st.slider("Number of recommendation" \
"s", 3, 15, 5)

if st.button("Get Recommendations"):
    if not query.strip():
        st.warning("Please enter a description.")
    else:
        with st.spinner("Finding best assessments..."):
            response = requests.post(
                API_URL,
                json={"query": query, "top_k": top_k}
            )

        if response.status_code == 200:
            data = response.json()
            recs = data.get("recommendations", [])

            if not recs:
                st.info("No recommendations found.")
            else:
                st.success(f"Found {len(recs)} recommendations")

                for r in recs:
                    st.markdown(f"""
                    **{r['name']}**  
                    Type: `{r['test_type']}`  
                    🔗 [View Assessment]({r['url']})
                    ---
                    """)
        else:
            st.error("API error. Please check backend.")
