import streamlit as st
import os
from pathlib import Path
from src.utils import get_chroma_dir, get_data_dir, get_top_k, get_gemini_api_key
from src.embedder import Embedder
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.generator import Generator

# Set page config
st.set_page_config(
    page_title="RAG Document Q&A Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics and premium dark/light mode integration
st.markdown("""
<style>
    /* Gradient Background and Hero style */
    .hero-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .hero-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Document tags */
    .doc-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.3rem;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    
    /* Cards for retrieved chunks */
    .chunk-card {
        background: #f8f9fa;
        border-left: 5px solid #2a5298;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .chunk-card:hover {
        transform: translateY(-2px);
    }
    .dark-mode .chunk-card {
        background: #1e2430;
        border-left: 5px solid #4a76c5;
    }
    
    .chunk-meta {
        font-size: 0.85rem;
        font-weight: 600;
        color: #555;
        margin-bottom: 0.5rem;
    }
    
    .similarity-badge {
        background-color: #28a745;
        color: white;
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# App state management
if "embedder" not in st.session_state:
    st.session_state.embedder = Embedder()

# Setup Vector Store
chroma_dir = get_chroma_dir()
vector_store = VectorStore(chroma_dir)

# Main layout
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🤖 AI Document Q&A Assistant</div>
    <div class="hero-subtitle">Retrieve-Augmented Generation (RAG) Pipeline over your Knowledge Base</div>
</div>
""", unsafe_allow_html=True)

# Sidebar layout
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/artificial-intelligence.png", width=100)
    st.title("Settings & Config")
    
    # API Key management
    api_key_env = get_gemini_api_key()
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=api_key_env if api_key_env else "",
        type="password",
        help="Get a free Gemini API key at https://aistudio.google.com/"
    )
    
    # Overwrite environment variable value with user input for this run
    if api_key_input:
        os.environ["GOOGLE_API_KEY"] = api_key_input
        
    st.divider()
    
    # Top-K Slider
    top_k = st.slider("Top-K Chunks to Retrieve", min_value=1, max_value=10, value=get_top_k())
    
    st.divider()
    
    # Knowledge Base Stats
    st.subheader("Knowledge Base Status")
    doc_count = vector_store.count()
    if doc_count > 0:
        st.success(f"Database Loaded: {doc_count} chunks indexed.")
    else:
        st.warning("Database Empty: No chunks found. Please run indexer.")
        
    # List actual files in data directory
    data_dir = get_data_dir()
    if data_dir.exists():
        st.markdown("**Indexed Files:**")
        for file in data_dir.iterdir():
            if file.is_file() and file.suffix.lower() in [".pdf", ".docx", ".txt", ".md"]:
                st.markdown(f"- 📄 `{file.name}`")
    
    st.divider()
    st.info("Developed for AI Engineering Internship Assignment.")

# Main app execution
if doc_count == 0:
    st.warning("⚠️ The vector database is empty! Please click below to generate sample documents and index them.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Step 1: Generate Sample Documents", use_container_width=True):
            import subprocess
            with st.spinner("Generating document files..."):
                result = subprocess.run(["python", "generate_data_files.py"], capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("Sample documents created in `/data`!")
                    st.rerun()
                else:
                    st.error(f"Error generating files: {result.stderr}")
    with col2:
        st.button("Step 2: Index Documents", disabled=True, use_container_width=True)

else:
    # Set up Retriever and Generator
    retriever = Retriever(st.session_state.embedder, vector_store)
    generator = Generator()

    # Create tabs
    tab_qa, tab_docs = st.tabs(["💬 Ask Q&A Bot", "📄 Browse Knowledge Base"])

    with tab_qa:
        st.markdown("### Ask a question against your loaded documents:")
        
        # Suggested questions
        suggested = [
            "Explain the core mathematical formula of the self-attention mechanism in Transformers.",
            "What is the EU AI Act risk levels and how does it classify AI risk?",
            "What strategies are mentioned for climate change mitigation in transportation?",
            "What is the history of the Apollo 11 moon landing?",
            "Explain decorators and generators in Python.",
            "What is the capital of France?" # Unanswerable query
        ]
        
        selected_suggestion = st.selectbox("Select a sample query to test:", ["-- Choose a query --"] + suggested)
        
        query_input = st.text_input(
            "Enter your custom question here:",
            value=selected_suggestion if selected_suggestion != "-- Choose a query --" else "",
            placeholder="Type your question..."
        )
        
        if st.button("Generate Answer", type="primary", use_container_width=True) or query_input:
            if not query_input.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Retrieving sources and generating grounded answer..."):
                    # 1. Retrieve
                    results = retriever.retrieve(query_input, top_k=top_k)
                    
                    if not results:
                        st.error("No relevant documents found.")
                    else:
                        # 2. Generate
                        answer, prompt_used = generator.generate_answer(query_input, results)
                        
                        # Display output
                        st.markdown("### Answer")
                        st.markdown(f"<div style='background-color:#eef2f7; padding:1.5rem; border-radius:10px; border-left: 6px solid #28a745; margin-bottom: 1.5rem; color: #111;'>{answer}</div>", unsafe_allow_html=True)
                        
                        # Expandable source details
                        with st.expander("🔍 View Retrieved Sources Used for Grounding"):
                            for i, res in enumerate(results):
                                score = res['score']
                                st.markdown(f"""
                                <div class="chunk-card">
                                    <div class="chunk-meta">
                                        📄 <strong>{res['source']}</strong> | Page/Section: <strong>{res['page']}</strong>
                                        <span class="similarity-badge">Cosine Similarity: {score:.4f}</span>
                                    </div>
                                    <div style="font-size:0.95rem; color:#333; white-space: pre-wrap;">{res['text']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                        with st.expander("🛠️ View Raw LLM Grounding Prompt"):
                            st.code(prompt_used, language="markdown")

    with tab_docs:
        st.markdown("### Loaded Documents Overview")
        st.write("Browse the pages and text loaded into the vector database.")
        
        # Read files from data directory
        for file in data_dir.iterdir():
            if file.is_file() and file.suffix.lower() in [".pdf", ".docx", ".txt", ".md"]:
                with st.expander(f"📄 {file.name}"):
                    st.write(f"File Type: `{file.suffix.upper()[1:]}`")
                    st.write(f"Path: `{file.absolute()}`")
                    
                    if file.suffix.lower() == ".txt":
                        with open(file, "r", encoding="utf-8") as f:
                            st.text_area("File Content Preview", f.read()[:2000], height=300)
                    elif file.suffix.lower() == ".docx":
                        import docx
                        doc = docx.Document(file)
                        text = "\n".join([p.text for p in doc.paragraphs])
                        st.text_area("File Content Preview", text[:2000], height=300)
                    elif file.suffix.lower() == ".pdf":
                        import pypdf
                        reader = pypdf.PdfReader(file)
                        text = ""
                        for p_idx in range(min(len(reader.pages), 3)):
                            page_text = reader.pages[p_idx].extract_text() or ""
                            text += f"--- Page {p_idx+1} ---\n" + page_text + "\n"
                        st.text_area("File Content Preview (First 3 Pages)", text[:2000], height=300)
