# chatbot_ingest.py
from pathlib import Path
import json
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
# --- CORRECTED IMPORT ---
from langchain_core.documents import Document
# ------------------------
# Use chatbot specific config
from chatbot_config import DATA_DIR_CHATBOT, CHROMA_DIR_CHATBOT, EMBED_MODEL, STORAGE_DIR_CHATBOT

def load_documents():
    docs = []
    print(f"Loading documents from: {DATA_DIR_CHATBOT}")
    # Load all .json files from the chatbot data directory
    json_files = list(DATA_DIR_CHATBOT.glob("*.json"))
    if not json_files:
        print(f"Warning: No JSON files found in {DATA_DIR_CHATBOT}")
        return docs

    for p in sorted(json_files):
        try:
            content = p.read_text(encoding="utf-8")
            if not content:
                print(f"Warning: Skipping empty file {p.name}")
                continue
            j = json.loads(content)
            if isinstance(j, list):
                count = 0
                for item in j:
                    # Ensure item is converted to string for page_content
                    page_content_str = json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item)
                    docs.append(Document(page_content=page_content_str, metadata={"source": p.name}))
                    count += 1
                print(f" -> Loaded {count} items from list in {p.name}")
            else:
                # Ensure item is converted to string for page_content
                page_content_str = json.dumps(j, ensure_ascii=False) if isinstance(j, dict) else str(j)
                docs.append(Document(page_content=page_content_str, metadata={"source": p.name}))
                print(f" -> Loaded 1 object from {p.name}")

        except json.JSONDecodeError:
            print(f"❌ Error: Could not decode JSON from {p.name}")
        except Exception as e:
            print(f"❌ Error loading {p.name}: {e}")
    return docs

def run_ingest():
    # Ensure directories exist
    STORAGE_DIR_CHATBOT.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR_CHATBOT.mkdir(parents=True, exist_ok=True)
    DATA_DIR_CHATBOT.mkdir(parents=True, exist_ok=True) # Ensure data dir exists too

    docs = load_documents()
    if not docs:
        print("❌ Error: No documents loaded. Ingestion cannot proceed.")
        print(f"   Please add JSON files (like courses.json, faq.json) to the '{DATA_DIR_CHATBOT}' directory.")
        return

    # Split documents into smaller chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50) # Smaller chunks for RAG
    chunks = splitter.split_documents(docs)

    if not chunks:
        print("❌ Error: Could not split documents into chunks.")
        return

    print(f"Created {len(chunks)} chunks. Preparing for embedding...")
    try:
        # Initialize embedding model
        embed = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

        # Create Chroma vector store FROM SCRATCH (overwrites old data)
        print(f"Creating/overwriting vector store at: {CHROMA_DIR_CHATBOT}")
        vs = Chroma.from_documents(chunks, embedding=embed, persist_directory=str(CHROMA_DIR_CHATBOT))
        vs.persist() # Save the database to disk
        print(f"✅ Ingest complete. Chroma index written to: {CHROMA_DIR_CHATBOT}")
    except Exception as e:
        print(f"❌ Error during embedding or saving to Chroma: {e}")


if __name__ == "__main__":
    run_ingest()