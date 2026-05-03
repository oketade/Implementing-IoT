import io
from typing import Optional

MOCK_PARSED_CV = {
    "name": "Peter Adedayo Oketade",
    "email": "peter.oketade@student.fi",
    "phone": "+358 45 678 9012",
    "location": "Vantaa, Finland",
    "summary": (
        "Industrial Information Technology student with strong interest in IoT, "
        "embedded systems, and platform development. Experienced in building "
        "data-driven applications and passionate about bridging the gap between "
        "engineering and real-world industry problems."
    ),
    "skills": ["Python", "JavaScript", "Node.js", "React", "SQL", "IoT / MQTT", "Embedded C", "Figma"],
    "experience": [
        {
            "title": "Junior Developer",
            "company": "Nokia",
            "period": "May 2024 – Aug 2024",
            "description": (
                "Developed backend microservices for internal tools. "
                "Collaborated with senior engineers on REST API integrations."
            ),
            "type": "Internship",
        },
        {
            "title": "IT Support Technician",
            "company": "Haaga-Helia IT Dept",
            "period": "2023 – Present",
            "description": (
                "Provided technical support, managed hardware inventory, "
                "and resolved network issues for faculty and students."
            ),
            "type": "Part-time",
        },
    ],
    "education": [
        {
            "degree": "Industrial Information Technology",
            "institution": "LAB University of Applied Sciences",
            "period": "2023 – 2025",
            "status": "Current",
        }
    ],
}


def extract_text_from_html(file_bytes: bytes) -> str:
    from html.parser import HTMLParser

    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.chunks = []
            self._skip = False

        def handle_starttag(self, tag, attrs):
            if tag in ('style', 'script'):
                self._skip = True

        def handle_endtag(self, tag):
            if tag in ('style', 'script'):
                self._skip = False
            if tag in ('div', 'p', 'br', 'li', 'h1', 'h2', 'h3', 'h4', 'tr'):
                self.chunks.append('\n')

        def handle_data(self, data):
            if not self._skip:
                self.chunks.append(data)

    parser = TextExtractor()
    parser.feed(file_bytes.decode('utf-8', errors='ignore'))
    lines = [l.strip() for l in ''.join(parser.chunks).splitlines()]
    return '\n'.join(l for l in lines if l)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    # Detect HTML disguised as PDF
    if file_bytes[:50].lstrip().startswith(b'<!') or file_bytes[:50].lstrip().lower().startswith(b'<html'):
        text = extract_text_from_html(file_bytes)
        if text.strip():
            return text.strip()

    # Try pdfplumber first
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception:
                    pass
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # Fallback: pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception:
                pass
        if text.strip():
            return text.strip()
    except Exception:
        pass

    # Fallback: OCR for scanned / image-based PDFs
    text = _ocr_pdf(file_bytes)
    if text.strip():
        return text.strip()

    raise RuntimeError(
        "Could not extract text from this PDF. "
        "OCR was attempted but Tesseract is not installed. "
        "Install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki "
        "or export your CV as .docx or .txt and upload that instead."
    )


def _ocr_pdf(file_bytes: bytes) -> str:
    """Use PyMuPDF + Tesseract to OCR each page of a scanned PDF."""
    try:
        import fitz  # pymupdf
        import pytesseract
        from PIL import Image

        # Point pytesseract at the default Windows install path if not on PATH
        import os, shutil
        if not shutil.which("tesseract"):
            pytesseract.pytesseract.tesseract_cmd = (
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            # Render page to a high-resolution image (300 DPI gives best OCR accuracy)
            mat = fitz.Matrix(300 / 72, 300 / 72)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang="eng")
            if text.strip():
                pages_text.append(text)
        doc.close()
        return "\n".join(pages_text)
    except ImportError:
        return ""   # OCR libraries not installed — caller raises RuntimeError
    except Exception:
        return ""   # Tesseract not installed or failed — caller raises RuntimeError


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        from docx import Document

        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise RuntimeError(f"DOCX extraction failed: {e}") from e


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")


def extract_text(filename: str, file_bytes: bytes) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        return extract_text_from_docx(file_bytes)
    elif ext == "txt":
        return extract_text_from_txt(file_bytes)
    raise ValueError(f"Unsupported file type: {ext}")


def get_mock_parsed_cv() -> dict:
    return dict(MOCK_PARSED_CV)
