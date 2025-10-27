# utils.py
import docx2txt
import PyPDF2
from fpdf import FPDF
from docx import Document
import os
import time
import json # Added json import

# --- Existing Functions ---

def extract_text_from_file(file):
    """Extracts plain text from PDF, DOCX, or TXT file objects."""
    try:
        if file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text: # Append only if text is extracted
                     text += page_text + "\n" # Add newline between pages
            return text.strip() # Remove leading/trailing whitespace

        elif file.name.endswith(".docx"):
            # Use a temporary file path
            temp_path = f"temp_{int(time.time())}_{os.getpid()}.docx"
            try:
                with open(temp_path, "wb") as f:
                    f.write(file.getvalue())
                text = docx2txt.process(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path) # Clean up temp file
            return text.strip()

        elif file.name.endswith(".txt"):
            # Try common encodings
            try:
                file.seek(0)
                return file.read().decode("utf-8").strip()
            except UnicodeDecodeError:
                try:
                    file.seek(0)
                    return file.read().decode("latin-1").strip()
                except Exception as e:
                     print(f"Error decoding .txt file: {e}")
                     return ""
            except Exception as e:
                print(f"Error reading .txt file: {e}")
                return ""
    except Exception as e:
        print(f"Error extracting text from {getattr(file, 'name', 'file')}: {e}")
        return ""

    return "" # Fallback

def save_edited_resume(text, format="docx"):
    """Saves the provided text as a DOCX or PDF file in an 'uploads' directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    upload_dir = os.path.join(base_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = int(time.time())
    file_name = f"updated_resume_{timestamp}.{format}"
    path = os.path.join(upload_dir, file_name)

    try:
        if format == "docx":
            doc = Document()
            doc.add_paragraph(str(text) if text is not None else "")
            doc.save(path)
        elif format == "pdf":
            pdf = FPDF()
            pdf.add_page()
            try:
                pdf.set_font("Arial", size=12)
            except RuntimeError:
                print("Warning: Arial font not found. Using default.")
                pdf.set_font("Helvetica", size=12) # Fallback

            pdf_text = str(text) if text is not None else ""
            pdf.multi_cell(0, 10, pdf_text.encode('latin-1', 'replace').decode('latin-1'))
            pdf.output(path)
        else:
             print(f"Unsupported format: {format}")
             return None

        print(f"Saved edited resume to: {path}")
        return path
    except Exception as e:
        print(f"Error saving edited resume to {path}: {e}")
        return None

# --- JSON Functions (Appended) ---

def load_json(path):
    """Load JSON from path, return Python object or None on failure."""
    try:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                return None
            data = json.loads(content)
            return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {path}: {e}")
        return None
    except Exception as e:
        print(f"Error loading JSON {path}: {e}")
        return None

def save_json(path, obj):
    """Save Python object as JSON (indent=4, ensure_ascii=False)."""
    try:
        output_dir = os.path.dirname(path)
        if output_dir:
             os.makedirs(output_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj if obj is not None else [], f, ensure_ascii=False, indent=4)
        print(f"Successfully saved JSON to {path}")
        return True
    except Exception as e:
        print(f"Error saving JSON {path}: {e}")
        return False