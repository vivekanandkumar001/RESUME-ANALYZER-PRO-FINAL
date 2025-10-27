# chatbot_rag.py
from chatbot_config import OLLAMA_MODEL, INTERVIEWER_SYSTEM_PROMPT, GEMINI_MODEL, GEMINI_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI # New Import
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.llms import Ollama # Kept for local fallback context
import streamlit as st
import os

# --- Initialize LLM LAZILY (Gemini Priority) ---
@st.cache_resource
def load_llm_model():
    print(f"Attempting to load AI model (Gemini: {GEMINI_MODEL} / Ollama: {OLLAMA_MODEL})...")
    
    # 1. Try Gemini (Cloud deployment preferred)
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_ACTUAL_GEMINI_API_KEY_HERE":
        try:
            llm_instance = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                api_key=GEMINI_API_KEY,
                temperature=0.6 
            )
            print("✅ Gemini Model initialized successfully.")
            return llm_instance
        except Exception as e:
            print(f"❌ Gemini initialization failed: {e}")
            # Fall through to check for local Ollama

    # 2. Try Ollama (Local/Dev fallback)
    try:
        # If running locally, this should work (assumes Ollama is running)
        ollama_llm = Ollama(model=OLLAMA_MODEL)
        # Quick check: if local connection fails, don't return it
        # ollama_llm.invoke("test") # Test is too slow for cache, assume connection is okay
        print(f"✅ Ollama Model ({OLLAMA_MODEL}) initialized successfully.")
        return ollama_llm
    except Exception as e:
        error_message = f"❌ Neither Gemini nor Ollama could be initialized. Error: {e}"
        print(error_message)
        st.error(f"FATAL: {error_message}")
        return None

# --- Interview Initialization ---
def initialize_interview(resume_text: str) -> str | None:
    llm = load_llm_model()
    if not llm: return None

    # Determine if the model is a ChatModel (Gemini) or LLM (Ollama)
    is_chat_model = hasattr(llm, 'invoke') and 'Chat' in str(type(llm))

    system_prompt_content = INTERVIEWER_SYSTEM_PROMPT.format(resume_text=resume_text)
    
    try:
        print("Generating initial interview question...")
        
        if is_chat_model:
            # For Gemini (ChatModel)
            messages = [SystemMessage(content=system_prompt_content)]
            response = llm.invoke(messages)
            result = response.content
        else:
            # For Ollama (LLM) - send the prompt directly
            response = llm.invoke(system_prompt_content)
            result = response

        print("Initial question generated.")
        return result.strip() if result and result.strip() else "Hello! Could you start by telling me a bit about yourself?"
    except Exception as e:
        print(f"Error generating initial question: {e}")
        st.error(f"Error communicating with AI: {e}")
        return None

# --- Get AI Response during Interview ---
def get_rag_response(user_query: str, user_name: str = "Candidate") -> str:
    llm = load_llm_model()
    if not llm: return "Error: AI model is currently unavailable."

    is_chat_model = hasattr(llm, 'invoke') and 'Chat' in str(type(llm))
    
    try:
        print(f"Sending user query: {user_query[:50]}...")
        
        if is_chat_model:
            # For Gemini (ChatModel)
            messages = [HumanMessage(content=user_query)]
            response = llm.invoke(messages)
            result = response.content
        else:
            # For Ollama (LLM)
            response = llm.invoke(user_query)
            result = response

        print("Received response from AI.")
        return result.strip() if result and result.strip() else "Okay, interesting. Could you please elaborate?"
    except Exception as e:
        print(f"Error getting AI response: {e}")
        st.error(f"Error communicating with AI: {e}")
        return "Sorry, I encountered an error trying to get a response. Please try again."