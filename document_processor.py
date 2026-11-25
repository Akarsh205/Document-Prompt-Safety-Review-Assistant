
import io
from pypdf import PdfReader
from docx import Document


def extract_text(uploaded_file):
    """Extract text from PDF, TXT and DOCX files."""

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".pdf"):
            pdf = PdfReader(uploaded_file)
            text = "\n".join(
                page.extract_text() or ""
                for page in pdf.pages
            )

        elif file_name.endswith(".txt"):
            text = uploaded_file.read().decode(
                "utf-8",
                errors="replace"
            )

        elif file_name.endswith(".docx"):
            document = Document(uploaded_file)
            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        else:
            raise ValueError("Unsupported file format")

        if not text.strip():
            raise ValueError("No readable text found")

        return text

    except Exception as e:
        raise ValueError(f"Document processing failed: {e}")


def split_into_chunks(text, chunk_size=500, overlap=50):
    """Split extracted text into overlapping chunks."""

    words = text.split()

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk size or overlap")

    chunks = []

    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


def process_document(uploaded_file):
    """Complete document processing pipeline."""

    extracted_text = extract_text(uploaded_file)

    chunks = split_into_chunks(extracted_text)

    return {
        "file_name": uploaded_file.name,
        "total_words": len(extracted_text.split()),
        "total_chunks": len(chunks),
        "chunks": chunks
    }

