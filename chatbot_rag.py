# chatbot_rag.py
from chatbot_config import OLLAMA_MODEL, INTERVIEWER_SYSTEM_PROMPT
from langchain_community.llms import Ollama
import streamlit as st # Import streamlit for error display and caching
import os

# --- Initialize Ollama LAZILY ---
@st.cache_resource
def load_ollama_model():
    print(f"Loading Ollama model: {OLLAMA_MODEL}...")
    try:
        llm_instance = Ollama(model=OLLAMA_MODEL)
        print("Ollama model initialized successfully.")
        return llm_instance
    except Exception as e:
        error_message = (
            f"Failed to initialize Ollama model '{OLLAMA_MODEL}'. "
            f"Is the Ollama server running and the model pulled? Error: {e}"
        )
        print(error_message)
        st.error(error_message)
        return None

# --- Interview Initialization ---
def initialize_interview(resume_text: str) -> str | None:
    llm = load_ollama_model()
    if not llm:
        st.error("Cannot start interview: Ollama model failed to load.")
        return None

    prompt = INTERVIEWER_SYSTEM_PROMPT.format(resume_text=resume_text)
    try:
        print("Generating initial interview question...")
        response = llm.invoke(prompt)
        print("Initial question generated.")
        return response.strip() if response and response.strip() else "Hello! Could you start by telling me a bit about yourself?"
    except Exception as e:
        print(f"Error generating initial question: {e}")
        st.error(f"Error communicating with Ollama: {e}")
        return None

# --- Get AI Response during Interview ---
def get_rag_response(user_query: str, user_name: str = "Candidate") -> str:
    llm = load_ollama_model()
    if not llm:
        st.error("Cannot get response: Ollama model failed to load.")
        return "Error: AI model is currently unavailable."

    prompt = user_query # User's latest message

    try:
        print(f"Sending user query to Ollama: {prompt[:100]}...")
        response = llm.invoke(prompt)
        print("Received response from Ollama.")
        return response.strip() if response and response.strip() else "Okay, interesting. Could you please elaborate?"
    except Exception as e:
        print(f"Error getting Ollama response: {e}")
        st.error(f"Error communicating with Ollama: {e}")
        return "Sorry, I encountered an error trying to get a response. Please try again."