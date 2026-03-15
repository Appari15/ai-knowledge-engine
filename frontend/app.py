"""
Streamlit frontend for AI Knowledge Engine.
Run: streamlit run frontend/app.py
"""
import streamlit as st
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:8001"

# Page config
st.set_page_config(
    page_title="AI Knowledge Engine",
    page_icon="🧠",
    layout="wide",
)

# Header
st.title("🧠 AI Knowledge Engine")
st.caption("RAG-powered knowledge base | FREE AI Stack | Built by a Data Engineer")

# Sidebar
with st.sidebar:
    st.header("📊 System Stats")

    try:
        stats = requests.get(f"{API_URL}/api/stats", timeout=5).json()
        st.metric("📚 Articles", stats["articles_in_db"])
        st.metric("🔢 Vectors", stats["vectors_in_chromadb"])
        st.metric("💰 Total Cost", f"${stats['cost_so_far']:.2f}")
        st.success(f"Status: {stats['status']}")
    except Exception:
        st.warning("API not running. Start it with:")
        st.code("uvicorn src.api.main:app --port 8001")

    st.divider()

    st.header("⚙️ Settings")
    num_sources = st.slider("Number of sources", 1, 10, 5)

    st.divider()

    st.header("🛠️ Tech Stack")
    st.markdown("""
    - **LLM**: OpenRouter (FREE)
    - **Embeddings**: sentence-transformers
    - **Vector DB**: ChromaDB
    - **Database**: PostgreSQL
    - **API**: FastAPI
    - **Frontend**: Streamlit
    """)

    st.divider()
    st.markdown("💰 **Total Cost: $0.00**")

# Main content
st.markdown("---")

# Question input
question = st.text_input(
    "🔍 Ask anything about the knowledge base:",
    placeholder="What programming languages are discussed?",
)

col1, col2 = st.columns([1, 5])
with col1:
    ask_button = st.button("Ask 🚀", type="primary", use_container_width=True)

if ask_button and question:
    with st.spinner("🤔 Searching knowledge base and generating answer..."):
        try:
            response = requests.post(
                f"{API_URL}/api/ask",
                json={"question": question, "num_sources": num_sources},
                timeout=60,
            )

            if response.status_code == 200:
                data = response.json()

                # Answer
                st.markdown("### 💡 Answer")
                st.markdown(data["answer"])

                # Metrics row
                st.markdown("---")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("⏱️ Latency", f"{data['latency_seconds']}s")
                m2.metric("🔤 Tokens", data["tokens_used"]["total"])
                m3.metric("📚 Sources", len(data["sources"]))
                m4.metric("💰 Cost", f"${data['cost']:.2f}")

                # Sources
                st.markdown("### 📚 Sources")
                for i, source in enumerate(data["sources"]):
                    relevance_pct = int(source["relevance"] * 100)
                    with st.expander(
                        f"Source {i+1}: {source['title'][:60]} "
                        f"(Relevance: {relevance_pct}%)"
                    ):
                        st.write(f"**Source:** {source['source']}")
                        st.write(f"**Relevance:** {source['relevance']}")
                        st.write(f"**Chunk:** {source['chunk']}")

                # Model info
                st.markdown("---")
                st.caption(f"Model: {data['model']} | Tokens: {data['tokens_used']['total']} | Cost: $0.00")

            else:
                st.error(f"Error: {response.text}")

        except requests.ConnectionError:
            st.error("Cannot connect to API. Make sure it's running:")
            st.code("uvicorn src.api.main:app --port 8001")
        except Exception as e:
            st.error(f"Error: {e}")

elif ask_button and not question:
    st.warning("Please enter a question!")

# Footer
st.markdown("---")
st.markdown(
    "Built with ❤️ using **FastAPI** + **ChromaDB** + **OpenRouter** + **Streamlit** | "
    "100% FREE AI Stack"
)