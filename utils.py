import docx2txt
import PyPDF2
from fpdf import FPDF
from docx import Document
import os
import time

def extract_text_from_file(file):
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    elif file.name.endswith(".docx"):
        return docx2txt.process(file)

    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")

    return ""

def save_edited_resume(text, format="docx"):
    os.makedirs("uploads", exist_ok=True)
    timestamp = int(time.time())
    path = f"uploads/updated_resume_{timestamp}.{format}"

    if format == "docx":
        doc = Document()
        doc.add_paragraph(text)
        doc.save(path)
    else:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, text)
        pdf.output(path)

    return path