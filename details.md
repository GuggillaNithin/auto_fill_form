# Project Details: AI Resume Auto-Filler

## Overview
The **AI Resume Auto-Filler** is a lightweight, fully-local Python web application designed to automate the tedious process of manually entering data from a resume into a job application form. It takes an uploaded resume (in PDF, DOCX, or Image format), extracts the raw text, intelligently parses it to find key entities (Name, Email, Phone, Education, etc.), and pre-fills an editable application form.

Crucially, this project operates **entirely offline** and relies strictly on local Python libraries without making any external API calls (e.g., OpenAI).

---

## Technical Architecture

The project is split into three main components:
1. **Frontend / UI (`app.py`)**: Handles the user interaction, file uploads, and renders the auto-filled form.
2. **Text Extraction (`extractor.py`)**: Responsible for reading the raw bytes of the uploaded file and converting it into plain text, regardless of whether it is a document or an image.
3. **Data Parsing (`parser.py`)**: The brain of the application. It takes the raw, unstructured text and uses Natural Language Processing (NLP) and pattern matching to extract structured fields.

---

## Libraries Used

Here is a breakdown of the core Python libraries used in this project and exactly what they do:

### 1. User Interface
* **`streamlit`**: Used to build the entire web interface. It provides the file uploader widget, the layout, the loading spinners, and the editable form where the final extracted data is displayed.

### 2. Document Extraction
* **`PyMuPDF` (imported as `fitz`)**: A highly robust library used to parse PDF files. It accurately pulls text from standard digital PDFs.
* **`python-docx`**: Used to read `.docx` files (Microsoft Word). It iterates through the paragraphs in the document to reconstruct the text.
* **`pytesseract`**: An Optical Character Recognition (OCR) wrapper for Google's Tesseract-OCR Engine. This is used when a user uploads an image (`.png`, `.jpg`, `.jpeg`). It visually scans the image and attempts to "read" the text from it.
* **`Pillow` (imported as `PIL`)**: The Python Imaging Library, used to open and process the image bytes before passing them to `pytesseract`.

### 3. NLP & Parsing Strategy
Because OCR and PDF parsers can sometimes output messy text (missing newlines, weird spacing), the parsing logic uses a multi-layered approach:

* **`spacy`**: An industrial-strength Natural Language Processing library. We use the `en_core_web_sm` model to perform **Named Entity Recognition (NER)**. SpaCy analyzes the grammatical structure of the text to identify "Entities" like `PERSON` (for names) and `ORG` (for universities and companies). 
* **`re` (Python Built-in)**: Regular Expressions are used extensively to catch things that AI/NLP models might miss. 
  * **Strict Patterns**: Used for finding Emails, Phone Numbers, and URLs (LinkedIn, GitHub) since these follow exact formats.
  * **Deep Fallbacks**: Used to aggressively search for Degrees (e.g., finding variations like `B.Tech` or `Ph.D`) and Universities (by searching for surrounding words near the keyword "University").
  * **Keywords**: Used to scan for predefined technical skills (Python, Java, Git, Agile, etc.).

---

## Workflow Summary

1. **Upload**: User uploads a file via Streamlit.
2. **Extract**: `extractor.py` routes the file to PyMuPDF (if PDF), python-docx (if Word), or Pytesseract (if Image) to get a raw string of text.
3. **Parse**: `parser.py` attacks the string using Heuristics (first 5 lines for a Name), Regex (Emails/Phones/Degrees), and finally SpaCy (NER for complex names and organizations).
4. **Review**: The structured dictionary is passed back to Streamlit, which populates the text boxes in the form for user review.
