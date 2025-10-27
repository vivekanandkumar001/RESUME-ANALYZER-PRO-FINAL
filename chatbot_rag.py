# chatbot_rag.py
from chatbot_config import INTERVIEWER_SYSTEM_PROMPT, GEMINI_MODEL
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
# Ollama and langchain_community imports are NOT needed when using Gemini
# from langchain_community.llms import Ollama 
import streamlit as st
import os

# --- Initialize LLM LAZILY (Gemini ONLY) ---
@st.cache_resource
def load_llm_model():
    """Loads the Gemini model, prioritizing st.secrets."""
    # st.secrets.get() is the standard way to retrieve secrets in Streamlit Cloud
    gemini_key = st.secrets.get("GEMINI_API_KEY")

    if not gemini_key:
        # Display the specific error that the UI showed you
        st.error("❌ Gemini API Key not found. Please set 'GEMINI_API_KEY' in Streamlit Secrets.")
        return None
    
    # We ignore Ollama entirely here since it will fail on Cloud
    try:
        llm_instance = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            api_key=gemini_key, # Use the key from st.secrets
            temperature=0.6 
        )
        print("✅ Gemini Model initialized successfully.")
        return llm_instance
    except Exception as e:
        error_message = f"❌ Failed to initialize Gemini model. Error: {e}"
        print(error_message)
        st.error(f"FATAL: Gemini failed to load. Check API key validity. Error: {e}")
        return None

# --- Interview Initialization (rest remains the same) ---
def initialize_interview(resume_text: str) -> str | None:
    llm = load_llm_model()
    if not llm: return None
    is_chat_model = hasattr(llm, 'invoke') and 'Chat' in str(type(llm))

    system_prompt_content = INTERVIEWER_SYSTEM_PROMPT.format(resume_text=resume_text)
    
    try:
        print("Generating initial interview question...")
        messages = [SystemMessage(content=system_prompt_content)]
        response = llm.invoke(messages)
        return response.content.strip() if response and response.content else "Hello! Could you start by telling me a bit about yourself?"
    except Exception as e:
        print(f"Error generating initial question: {e}")
        st.error(f"Error communicating with AI: {e}")
        return None

# --- Get AI Response during Interview (rest remains the same) ---
def get_rag_response(user_query: str, user_name: str = "Candidate") -> str:
    llm = load_llm_model()
    if not llm: return "Error: AI model is currently unavailable."

    try:
        response = llm.invoke([HumanMessage(content=user_query)])
        return response.content.strip() if response and response.content else "Okay, interesting. Could you please elaborate?"
    except Exception as e:
        print(f"Error getting AI response: {e}")
        st.error(f"Error communicating with AI: {e}")
        return "Sorry, I encountered an error trying to get a response. Please try again."