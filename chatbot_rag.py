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
    
    # Safely retrieve key from st.secrets (which loads from secrets.toml on Cloud)
    gemini_key = st.secrets.get("GEMINI_API_KEY")
    
    if not gemini_key:
        st.error("❌ FATAL: Gemini API Key not found. Please ensure 'GEMINI_API_KEY' is set in .streamlit/secrets.toml AND in GitHub Repository Secrets.")
        return None
    
    try:
        llm_instance = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            api_key=gemini_key, # Key mil gayi, ab use karo
            temperature=0.6 
        )
        print("✅ Gemini Model initialized successfully.")
        return llm_instance
    except Exception as e:
        error_message = f"❌ Failed to initialize Gemini model. Error: {e}"
        print(error_message)
        st.error(f"FATAL: Gemini failed to load. Check API key validity. Error: {e}")
        return None

# --- Interview Initialization (rest is correct) ---
def initialize_interview(resume_text: str) -> str | None:
    llm = load_llm_model()
    if not llm: return None
    
    system_prompt_content = INTERVIEWER_SYSTEM_PROMPT.format(resume_text=resume_text)
    messages = [SystemMessage(content=system_prompt_content)]
    
    try:
        response = llm.invoke(messages)
        return response.content.strip() if response and response.content else "Hello! Could you start by telling me a bit about yourself?"
    except Exception as e:
        st.error(f"Error communicating with AI: {e}")
        return None

# --- Get AI Response during Interview (rest is correct) ---
def get_rag_response(user_query: str, user_name: str = "Candidate") -> str:
    llm = load_llm_model()
    if not llm: return "Error: AI model is currently unavailable."

    try:
        response = llm.invoke([HumanMessage(content=user_query)])
        return response.content.strip() if response and response.content else "Okay, interesting. Could you please elaborate?"
    except Exception as e:
        st.error(f"Error communicating with AI: {e}")
        return "Sorry, I encountered an error trying to get a response. Please try again."