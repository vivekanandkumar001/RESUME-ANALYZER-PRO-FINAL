
# chatbot_config.py
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent

# --- GEMINI CONFIG (For Cloud Interview) ---
GEMINI_API_KEY = os.getenv("AIzaSyAUp3OSvPWvwR7DWFHcsiJTLlbznvpxsv8") 
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash") # Cloud par tez model
# ----------------------------------------

# Ollama / LLaMA config (Local testing ke liye rakha hai, deployment par ignore hoga)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b-instruct-q4_K_M") 

# Embedding model for retrieval
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Paths
DATA_DIR_CHATBOT = ROOT / "data_chatbot"
STORAGE_DIR_CHATBOT = ROOT / "storage_chatbot"
CHROMA_DIR_CHATBOT = STORAGE_DIR_CHATBOT / "chroma"

# --- INTERVIEWER SYSTEM PROMPT ---
INTERVIEWER_SYSTEM_PROMPT = """
You are 'Progeni AI', an expert, friendly, and professional HR Interviewer conducting the initial screening.
Your goal is to assess the candidate's suitability based on their resume and answers.
... (Baaki ka prompt pehle jaisa) ...
"""

# (RAG System Prompt remains the same)

# chatbot_config.py
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent

# --- GEMINI CONFIG (For Cloud Interview) ---
GEMINI_API_KEY = os.getenv("AIzaSyAUp3OSvPWvwR7DWFHcsiJTLlbznvpxsv8") 
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash") # Cloud par tez model
# ----------------------------------------

# Ollama / LLaMA config (Local testing ke liye rakha hai, deployment par ignore hoga)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b-instruct-q4_K_M") 

# Embedding model for retrieval
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Paths
DATA_DIR_CHATBOT = ROOT / "data_chatbot"
STORAGE_DIR_CHATBOT = ROOT / "storage_chatbot"
CHROMA_DIR_CHATBOT = STORAGE_DIR_CHATBOT / "chroma"

# --- INTERVIEWER SYSTEM PROMPT ---
INTERVIEWER_SYSTEM_PROMPT = """
You are 'Progeni AI', an expert, friendly, and professional HR Interviewer conducting the initial screening.
Your goal is to assess the candidate's suitability based on their resume and answers.
... (Baaki ka prompt pehle jaisa) ...
"""

# (RAG System Prompt remains the same)
RAG_SYSTEM_PROMPT = """You are EduBot, a friendly and persuasive educational counselor...."""