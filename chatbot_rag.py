# chatbot_rag.py
from chatbot_config import INTERVIEWER_SYSTEM_PROMPT, GEMINI_MODEL, GEMINI_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.messages import HumanMessage, SystemMessage 
import streamlit as st
import os

# --- Initialize LLM LAZILY (Gemini ONLY) ---
@st.cache_resource
def load_llm_model():
    gemini_key = st.secrets.get("GEMINI_API_KEY")

    if not gemini_key:
        st.error("❌ Gemini API Key not found. Please set 'GEMINI_API_KEY' in Streamlit Secrets.")
        return None
    
    try:
        llm_instance = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            api_key=gemini_key,
            temperature=0.6 
        )
        return llm_instance
    except Exception as e:
        error_message = f"❌ Failed to initialize Gemini model. Error: {e}"
        print(error_message)
        st.error(f"FATAL: Gemini failed to load. Check API key validity. Error: {e}")
        return None

# --- Interview Initialization (ROBUST CHECK ADDED) ---
def initialize_interview(resume_text: str) -> str | None:
    llm = load_llm_model()
    if not llm: return None
    
    # --- FIX: Check if resume text is actually present ---
    if not resume_text or len(resume_text.strip()) < 50:
         st.error("Error: Resume text is empty or too short. Please upload a valid resume in the Analyzer tab.")
         return None
    # ----------------------------------------------------

    system_prompt_content = INTERVIEWER_SYSTEM_PROMPT.format(resume_text=resume_text)
    
    messages = [
        SystemMessage(content=system_prompt_content)
    ]
    
    try:
        print("Generating initial interview question...")
        response = llm.invoke(messages)
        print("Initial question generated.")
        
        # Check if the generated content is valid
        if response and response.content and response.content.strip():
            return response.content.strip()
        else:
             # This means Gemini returned an empty string or something non-text
             st.error("AI returned an empty response. Trying a fallback question.")
             return "Hello! Could you start by telling me a little bit about yourself?"
             
    except Exception as e:
        print(f"Error communicating with AI: {e}")
        st.error(f"Error communicating with AI: {e}")
        return None

# --- Get AI Response during Interview (rest is correct) ---
def get_rag_response(user_query: str, user_name: str = "Candidate") -> str:
    llm = load_llm_model()
    if not llm: return "Error: AI model is currently unavailable."

    # Final sanity check before sending empty content
    if not user_query or not user_query.strip():
         return "Please provide a detailed answer so I can ask a follow-up question."

    try:
        response = llm.invoke([HumanMessage(content=user_query)])
        return response.content.strip() if response and response.content else "Okay, interesting. Could you please elaborate?"
    except Exception as e:
        st.error(f"Error communicating with AI: {e}")
        return "Sorry, I encountered an error trying to get a response. Please try again."