# chatbot_rag.py
# --- NAYE IMPORTS ---
from chatbot_config import INTERVIEWER_SYSTEM_PROMPT, GEMINI_MODEL, GEMINI_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.messages import HumanMessage, SystemMessage 
# --------------------
import streamlit as st
import os

# --- Initialize LLM LAZILY (Gemini) ---
@st.cache_resource
def load_llm_model():
    """Gemini model load karta hai."""
    if not GEMINI_API_KEY:
        st.error("❌ Gemini API Key not found. Please set 'GEMINI_API_KEY' in Streamlit Secrets.")
        return None
    try:
        llm_instance = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            api_key=GEMINI_API_KEY,
            temperature=0.6 
        )
        print("✅ Gemini Model initialized successfully.")
        return llm_instance
    except Exception as e:
        error_message = (
            f"❌ Failed to initialize Gemini model. "
            f"Please check your API key and network. Error: {e}"
        )
        print(error_message) 
        st.error(error_message)
        return None

# --- Interview Initialization ---
def initialize_interview(resume_text: str) -> str | None:
    """Pehla interview question generate karta hai."""
    llm = load_llm_model() 
    if not llm:
        return None

    # System Prompt ko format karein
    system_prompt_content = INTERVIEWER_SYSTEM_PROMPT.format(resume_text=resume_text)
    
    messages = [
        SystemMessage(content=system_prompt_content)
    ]
    
    try:
        print("Generating initial interview question (via Gemini)...")
        # LLM ko invoke karein
        response = llm.invoke(messages)
        print("Initial question generated.")
        return response.content.strip() if response and response.content else "Hello! Could you start by telling me a bit about yourself?"
    except Exception as e:
        print(f"Error generating initial question: {e}")
        st.error(f"Error communicating with Gemini: {e}")
        return None

# --- Get AI Response during Interview ---
def get_rag_response(user_query: str, user_name: str = "Candidate") -> str:
    """Next question/response lata hai."""
    llm = load_llm_model()
    if not llm:
        return "Error: AI model is currently unavailable." 

    # For now, we only pass the latest query. 
    # A robust system would pass the full history (all st.session_state.interview_messages).
    
    try:
        # Simple invocation
        response = llm.invoke([HumanMessage(content=user_query)])
        return response.content.strip() if response and response.content else "Okay, interesting. Could you please elaborate on that?"
    except Exception as e:
        error_message = f"Error getting Gemini response: {e}"
        print(error_message)
        st.error(f"Error communicating with Gemini: {e}")
        return "Sorry, I encountered an error trying to get a response. Please try again."