import csv
import io
import docx
from pypdf import PdfReader
from pathlib import Path

def parse_document(file_path: Path) -> list[dict]:
    """
    Extracts text from PDF, DOCX, TXT, or CSV.
    Returns a list of Segment Dicts: [{"text": "...", "start": 0, "end": 0}].
    """
    ext = file_path.suffix.lower()
    segments = []
    
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    segments.append({"text": line, "start": 0, "end": 0})
                    
    elif ext == ".pdf":
        reader = PdfReader(str(file_path))
        for page in reader.pages:
            text = page.extract_text()
            if text:
                for line in text.split("\n"):
                    if line.strip():
                        segments.append({"text": line.strip(), "start": 0, "end": 0})
                        
    elif ext == ".docx":
        doc = docx.Document(str(file_path))
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                segments.append({"text": text, "start": 0, "end": 0})
                
    elif ext == ".csv":
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    text = cell.strip()
                    if text:
                        segments.append({"text": text, "start": 0, "end": 0})
                        
    return segments
