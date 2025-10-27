# chatbot_config.py
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent

# Ollama Model for Chatbot/Interviewer
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Embedding model for RAG (if used)
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Paths for Chatbot Data and Storage
DATA_DIR_CHATBOT = ROOT / "data_chatbot"
STORAGE_DIR_CHATBOT = ROOT / "storage_chatbot"
CHROMA_DIR_CHATBOT = STORAGE_DIR_CHATBOT / "chroma"

# --- INTERVIEWER SYSTEM PROMPT ---
INTERVIEWER_SYSTEM_PROMPT = """
You are 'Progeni AI', an expert, friendly, and professional HR Interviewer...
... (पूरा prompt जैसा पिछली बार दिया था) ...
**Start the interview now with your first question.**
"""

# (Optional RAG Prompt)
RAG_SYSTEM_PROMPT = """You are EduBot, a helpful assistant..."""