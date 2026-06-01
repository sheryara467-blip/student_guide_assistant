# =============================================================================
# utils/data_loader.py — Dataset & PDF Loading Utilities
# =============================================================================
# This module handles loading raw data from disk:
#   1. load_knowledge_base() → loads the fallback JSON knowledge base
#   2. load_pdf_text()       → extracts and chunks text from a PDF file
#
# These are pure utility functions with no business logic — they just read
# files and return clean Python data structures.
# =============================================================================

import json
import os
from typing import List, Dict


# ── JSON Knowledge Base Loader ────────────────────────────────────────────────

def load_knowledge_base(file_path: str = None) -> List[Dict]:
    """
    Loads the local JSON knowledge base from disk.

    Args:
        file_path: Optional custom path. Defaults to data/knowledge_base.json.

    Returns:
        List of dicts, each with keys: id, topic, content.
    """
    if file_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "knowledge_base.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Knowledge base not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"[DataLoader] Loaded {len(data)} JSON entries.")
    return data


# ── PDF Loader & Chunker ──────────────────────────────────────────────────────

def load_pdf_chunks(
    pdf_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict]:
    """
    Extracts text from a PDF and splits it into overlapping chunks.

    Why chunking?
    - Vector databases store fixed-size pieces of text
    - Smaller chunks = more precise retrieval
    - Overlap ensures no context is lost at chunk boundaries

    Args:
        pdf_path:      Path to the PDF file on disk.
        chunk_size:    Target number of characters per chunk (default: 500).
        chunk_overlap: Number of characters to overlap between chunks (default: 50).

    Returns:
        List of dicts: [{ "chunk_id", "source", "page", "content" }, ...]
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("pdfplumber is required: pip install pdfplumber")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"[DataLoader] Extracting text from: {pdf_path}")

    # Step 1: Extract text page by page using pdfplumber
    pages_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text and text.strip():
                pages_text.append({"page": page_num, "text": text.strip()})

    print(f"[DataLoader] Extracted text from {len(pages_text)} pages.")

    # Step 2: Combine all page text into one string (preserving page metadata)
    chunks = []
    chunk_id = 0
    source_name = os.path.basename(pdf_path)

    for page_data in pages_text:
        text = page_data["text"]
        page_num = page_data["page"]

        # Step 3: Slide a window of `chunk_size` chars across each page
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if len(chunk_text) > 50:  # Skip tiny fragments
                chunks.append({
                    "chunk_id": f"chunk_{chunk_id}",
                    "source": source_name,
                    "page": page_num,
                    "content": chunk_text
                })
                chunk_id += 1

            # Move forward but leave overlap from the previous chunk
            start += chunk_size - chunk_overlap

    print(f"[DataLoader] Created {len(chunks)} chunks from PDF.")
    return chunks