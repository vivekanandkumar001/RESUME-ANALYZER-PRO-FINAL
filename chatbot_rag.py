# chatbot_rag.py
from chatbot_config import OLLAMA_MODEL, INTERVIEWER_SYSTEM_PROMPT, RAG_SYSTEM_PROMPT
# RAG components are not needed for pure conversational interview unless adding knowledge base
# from chatbot_config import CHROMA_DIR_CHATBOT, EMBED_MODEL
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
# -------------------------
from langchain_community.llms import Ollama # Keep Ollama import
import streamlit as st # Import streamlit for error display and caching
import os

# --- Initialize Ollama LAZILY ---
# The function is cached, but it's only CALLED when needed inside other functions
# This prevents it from running during import, avoiding the Streamlit error
@st.cache_resource
def load_ollama_model():
    """Loads the Ollama model specified in chatbot_config. Caches the loaded model."""
    print(f"Attempting to load Ollama model: {OLLAMA_MODEL}...")
    try:
        # Initialize the Ollama instance
        llm_instance = Ollama(model=OLLAMA_MODEL)
        # Optional: Add a quick check to see if the model connection works
        # llm_instance.invoke("Hi") # Example check, might add latency
        print("Ollama model initialized successfully.")
        return llm_instance
    except Exception as e:
        # Provide a more detailed error message
        error_message = (
            f"Failed to initialize Ollama model '{OLLAMA_MODEL}'. "
            f"Is the Ollama server running and the model pulled? Error: {e}"
        )
        print(error_message) # Log the error
        # Use st.error to display the error prominently in the Streamlit app
        st.error(error_message)
        return None

# --- Interview Initialization ---
def initialize_interview(resume_text: str) -> str | None:
    """Generates the first interview question using the system prompt and resume.
       Returns the question string or None on error."""
    # --- Load model INSIDE the function ---
    llm = load_ollama_model() # Get the (potentially cached) model instance
    # ------------------------------------
    if not llm:
        st.error("Cannot start interview: Ollama model failed to load.")
        return None # Indicate failure

    # Format the specific interviewer prompt with the resume text
    prompt = INTERVIEWER_SYSTEM_PROMPT.format(resume_text=resume_text)
    try:
        print("Generating initial interview question...")
        response = llm.invoke(prompt)
        print("Initial question generated.")
        # Provide a standard fallback if the response is empty or whitespace
        return response.strip() if response and response.strip() else "Hello! Could you start by telling me a bit about yourself?"
    except Exception as e:
        error_message = f"Error generating initial question: {e}"
        print(error_message)
        st.error(f"Error communicating with Ollama during initialization: {e}")
        return None # Indicate failure

# --- Get AI Response during Interview ---
def get_rag_response(user_query: str, user_name: str = "Candidate") -> str:
    """Gets the next question/response from the AI during the interview (using Ollama's context).
       Returns the AI's response string."""
    # --- Load model INSIDE the function ---
    llm = load_ollama_model() # Get the (potentially cached) model instance
    # ------------------------------------
    if not llm:
        st.error("Cannot get response: Ollama model failed to load.")
        return "Error: AI model is currently unavailable." # User-friendly error

    # For a conversational interview, just send the latest user message.
    # Ollama handles the conversation history internally for subsequent turns.
    prompt = user_query

    try:
        print(f"Sending user query to Ollama: {prompt[:100]}...") # Log truncated query
        response = llm.invoke(prompt)
        print("Received response from Ollama.")
        # Provide a standard fallback if the response is empty or whitespace
        return response.strip() if response and response.strip() else "Okay, interesting. Could you please elaborate on that?"
    except Exception as e:
        error_message = f"Error getting Ollama response: {e}"
        print(error_message)
        st.error(f"Error communicating with Ollama: {e}")
        return "Sorry, I encountered an error trying to get a response. Please try again."

# --- (Optional RAG functions for knowledge base - keep commented out or separate) ---
# These would use CHROMA_DIR_CHATBOT, EMBED_MODEL, RAG_SYSTEM_PROMPT
# @st.cache_resource
# def get_vectorstore(): ...
# def retrieve_context(query: str, k: int = 3) -> str: ...
# def get_knowledge_base_response(query: str): ...