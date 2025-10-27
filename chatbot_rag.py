# chatbot_rag.py
from chatbot_config import INTERVIEWER_SYSTEM_PROMPT, GEMINI_MODEL
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.messages import HumanMessage, SystemMessage 
import streamlit as st
import os

# --- Initialize LLM LAZILY (Gemini ONLY) ---
@st.cache_resource
def load_llm_model():
    """Loads the Gemini model, prioritizing st.secrets."""
    # st.secrets.get() is the standard way to retrieve secrets in Streamlit Cloud
    # This will look for GEMINI_API_KEY inside the st.toml file or GitHub Secrets
    gemini_key = st.secrets.get("GEMINI_API_KEY")

    if not gemini_key:
        # Display the specific error that the UI showed you
        st.error("❌ Gemini API Key not found. Please set 'GEMINI_API_KEY' in Streamlit Secrets.")
        return None
    
    try:
        llm_instance = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            api_key=gemini_key, # Use the key from st.secrets
            temperature=0.6 
        )
        print("✅ Gemini Model initialized successfully.")
        return llm_instance
    except Exception as e:
        error_message = (
            f"❌ FATAL: Failed to initialize Gemini model. "
            f"Check API key validity. Error: {e}"
        )
        print(error_message)
        st.error(error_message)
        return None

# --- Interview Initialization ---
def initialize_interview(resume_text: str) -> str | None:
    llm = load_llm_model()
    if not llm: return None
    
    # System Prompt ko format karein
    system_prompt_content = INTERVIEWER_SYSTEM_PROMPT.format(resume_text=resume_text)
    
    messages = [
        SystemMessage(content=system_prompt_content)
    ]
    
    try:
        print("Generating initial interview question...")
        response = llm.invoke(messages)
        print("Initial question generated.")
        return response.content.strip() if response and response.content else "Hello! Could you start by telling me a bit about yourself?"
    except Exception as e:
        print(f"Error generating initial question: {e}")
        st.error(f"Error communicating with AI: {e}")
        return None

# --- Get AI Response during Interview ---
def get_rag_response(user_query: str, user_name: str = "Candidate") -> str:
    llm = load_llm_model()
    if not llm: return "Error: AI model is currently unavailable."

    try:
        # Simple invocation - relies on model managing short-term conversation context
        response = llm.invoke([HumanMessage(content=user_query)])
        return response.content.strip() if response and response.content else "Okay, interesting. Could you please elaborate?"
    except Exception as e:
        error_message = f"Error getting AI response: {e}"
        print(error_message)
        st.error(f"Error communicating with AI: {e}")
        return "Sorry, I encountered an error trying to get a response. Please try again."