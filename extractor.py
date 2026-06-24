import io
import fitz  # PyMuPDF
from docx import Document
from PIL import Image

try:
    import pytesseract
    # Common installation path for Tesseract on Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    PYTESSERACT_AVAILABLE = True
except Exception as e:
    PYTESSERACT_AVAILABLE = False

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    text = ""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF: {e}")

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        raise ValueError(f"Error reading DOCX: {e}")

def extract_text_from_image(file_bytes: bytes) -> str:
    """Extract text from an image file using Pytesseract."""
    try:
        image = Image.open(io.BytesIO(file_bytes)).convert('RGB')
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise ValueError(f"OCR Failed. Please make sure you have installed Tesseract OCR on your Windows machine. Details: {e}")

def extract_text(file_bytes: bytes, filename: str) -> str:
    """Main extraction function based on file extension."""
    ext = filename.split(".")[-1].lower()
    
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        return extract_text_from_docx(file_bytes)
    elif ext in ["png", "jpg", "jpeg"]:
        if not PYTESSERACT_AVAILABLE:
            raise ValueError("Pytesseract library is not available.")
        return extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
