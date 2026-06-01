# =============================================================================
# scripts/ingest_pdf.py — PDF Ingestion Script
# =============================================================================
# Yeh script aapka PDF le kar:
#   1. Text extract aur chunks banata hai
#   2. Har chunk ko OpenAI se embedding mein convert karta hai
#      (NOTE: Groq abhi embeddings support nahi karta, isliye OpenAI use hoga)
#      (Groq_API_KEY .env mein rakhi hai — aap use chat/LLM ke liye use karein)
#   3. Sab vectors Pinecone index mein upload kar deta hai
#
# INSTALL (pehle yeh run karein):
#   pip install openai pinecone-client pypdf python-dotenv groq
#
# USAGE:
#   python scripts/ingest_pdf.py --pdf data/handbook.pdf
#   python scripts/ingest_pdf.py --pdf data/catalog.pdf --topic "Course Catalog"
#   python scripts/ingest_pdf.py --folder data/pdfs/
# =============================================================================

import sys
import os
import argparse
import time
import uuid

from dotenv import load_dotenv
load_dotenv()

# ── Required Libraries ────────────────────────────────────────────────────────
try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai library nahi mili. Run karein: pip install openai")
    sys.exit(1)

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    print("ERROR: pinecone-client nahi mila. Run karein: pip install pinecone-client")
    sys.exit(1)

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf nahi mili. Run karein: pip install pypdf")
    sys.exit(1)


# =============================================================================
# PDF TEXT EXTRACTION & CHUNKING
# =============================================================================

def load_pdf_chunks(pdf_path: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    """
    PDF file se text extract karke overlapping chunks banata hai.

    Args:
        pdf_path:     PDF file ka path
        chunk_size:   Har chunk mein characters ki tadaad
        chunk_overlap: Chunks ke beech overlap (context preserve karne ke liye)

    Returns:
        List of dicts: {chunk_id, content, page}
    """
    if not os.path.exists(pdf_path):
        print(f"ERROR: File nahi mili: {pdf_path}")
        sys.exit(1)

    print(f"[PDF] '{os.path.basename(pdf_path)}' se text extract ho raha hai...")

    reader = PdfReader(pdf_path)
    full_text_pages = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            full_text_pages.append((page_num + 1, text.strip()))

    if not full_text_pages:
        print("[PDF] WARNING: Koi text nahi mila. PDF text-based hai ya scanned?")
        return []

    # Saara text ek string mein (page number track karte hue)
    chunks = []
    chunk_id = 0

    for page_num, page_text in full_text_pages:
        start = 0
        while start < len(page_text):
            end = start + chunk_size
            chunk_text = page_text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "chunk_id": chunk_id,
                    "content":  chunk_text,
                    "page":     page_num
                })
                chunk_id += 1

            # Overlap ke saath aage badhein
            start += chunk_size - chunk_overlap

    return chunks


# =============================================================================
# EMBEDDING SERVICE (OpenAI)
# =============================================================================

class EmbeddingService:
    """
    OpenAI API se text embeddings generate karta hai.
    Groq embeddings support nahi karta — isliye OpenAI zaruri hai.
    """

class EmbeddingService:
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        print("[Embedding] Local model load ho raha hai...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[Embedding] Model ready!")

    def embed_batch(self, texts: list) -> list:
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()
    def embed_batch(self, texts: list) -> list:
        """
        Ek batch of texts ko embed karta hai.

        Args:
            texts: String list jise embed karna hai

        Returns:
            List of embedding vectors (floats)
        """
        # Empty ya whitespace-only texts hata do
        cleaned = [t if t.strip() else "." for t in texts]

        response = self.client.embeddings.create(
            model=self.model,
            input=cleaned
        )

        return [item.embedding for item in response.data]


# =============================================================================
# PINECONE SERVICE
# =============================================================================

class PineconeService:
    """
    Pinecone vector database se connect hota hai aur vectors upsert karta hai.
    Pinecone v3 (latest) use karta hai.
    """

    def __init__(self):
        api_key    = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")

        if not api_key:
            print("ERROR: PINECONE_API_KEY .env mein nahi mili!")
            sys.exit(1)
        if not index_name:
            print("ERROR: PINECONE_INDEX_NAME .env mein nahi mila!")
            sys.exit(1)

        self.index_name = index_name
        self.dimension  = int(os.getenv("EMBEDDING_DIMENSION", 1536))

        pc = Pinecone(api_key=api_key)

        # Index exist nahi karta to bana do
        existing_indexes = [idx.name for idx in pc.list_indexes()]
        if index_name not in existing_indexes:
            print(f"[Pinecone] Index '{index_name}' nahi mila — naya bana raha hoon...")
            pc.create_index(
                name      = index_name,
                dimension = self.dimension,
                metric    = "cosine",
                spec      = ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(f"[Pinecone] Index '{index_name}' successfully bana gaya!")
        else:
            print(f"[Pinecone] Index '{index_name}' milgaya — connect ho raha hoon...")

        self.index = pc.Index(index_name)

    def upsert_vectors(self, vectors: list, batch_size: int = 100):
        """
        Vectors ko Pinecone mein upsert karta hai.

        Args:
            vectors:    List of {id, values, metadata}
            batch_size: Ek baar mein kitne vectors bheje jayein
        """
        total = len(vectors)
        for i in range(0, total, batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"  Upserted {min(i + batch_size, total)}/{total} vectors...")

    def get_index_stats(self) -> dict:
        """Index ki stats return karta hai."""
        stats = self.index.describe_index_stats()
        return {"total_vector_count": stats.total_vector_count}


# =============================================================================
# TOPIC INFERENCE
# =============================================================================

def _infer_topic(text: str, filename: str) -> str:
    """
    Text mein keywords dekh kar topic assign karta hai.
    Koi match na ho to filename se topic banata hai.
    """
    text_lower = text.lower()

    keyword_topic_map = {
        ("register", "registration", "enroll", "enrollment", "sign up"): "Course Registration",
        ("gpa", "grade", "grading", "academic standing", "probation"):   "Grading & Academic Standing",
        ("scholarship", "financial aid", "tuition", "fee", "payment"):   "Financial Aid & Scholarships",
        ("exam", "test", "assessment", "midterm", "final"):              "Exams & Assessments",
        ("library", "borrow", "database", "journal"):                    "Library Services",
        ("plagiarism", "academic integrity", "cheating", "turnitin"):    "Academic Integrity",
        ("health", "counseling", "wellness", "mental health"):           "Health & Counseling",
        ("internship", "career", "job", "resume", "interview"):          "Career Services",
        ("graduate", "graduation", "degree", "credit hours"):            "Graduation Requirements",
        ("attendance", "absence", "absent"):                             "Attendance Policy",
    }

    for keywords, topic in keyword_topic_map.items():
        if any(kw in text_lower for kw in keywords):
            return topic

    return os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()


# =============================================================================
# MAIN INGESTION PIPELINE
# =============================================================================

def ingest_pdf(pdf_path: str, topic_override: str = None):
    """
    Ek PDF file ka pura ingestion pipeline chalata hai.

    Steps:
        1. PDF se text extract aur chunk
        2. Embedding service initialize
        3. Sab chunks embed karo (batches mein)
        4. Pinecone ke liye vectors tayar karo
        5. Vectors upsert karo
    """
    print(f"\n{'='*60}")
    print(f"  PDF Ingestion Shuru: {pdf_path}")
    print(f"{'='*60}\n")

    # ── Step 1: Extract + Chunk ───────────────────────────────────────────────
    print("[Step 1] PDF se text extract aur chunk ban raha hai...")
    chunks = load_pdf_chunks(pdf_path, chunk_size=500, chunk_overlap=50)

    if not chunks:
        print("[Step 1] Koi chunk nahi bana. Process band.")
        return

    print(f"[Step 1] {len(chunks)} chunks tayar hue.")

    # ── Step 2: Services Initialize ───────────────────────────────────────────
    print("\n[Step 2] Embedding aur Pinecone services connect ho rahi hain...")
    embedding_service = EmbeddingService()
    pinecone_service  = PineconeService()

    # ── Step 3: Embed Chunks ──────────────────────────────────────────────────
    print(f"\n[Step 3] {len(chunks)} chunks embed ho rahe hain...")
    source_name    = os.path.basename(pdf_path)
    texts          = [chunk["content"] for chunk in chunks]
    batch_size     = 50
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size
        print(f"  Batch {batch_num}/{total_batches} embed ho raha hai...")
        embeddings = embedding_service.embed_batch(batch)
        all_embeddings.extend(embeddings)
        time.sleep(0.3)  # Rate limit respect karne ke liye

    print(f"[Step 3] {len(all_embeddings)} chunks successfully embed hue.")

    # ── Step 4: Vectors Tayar Karo ────────────────────────────────────────────
    print(f"\n[Step 4] {len(chunks)} vectors Pinecone ke liye tayar ho rahe hain...")
    vectors = []

    for chunk, embedding in zip(chunks, all_embeddings):
        topic = topic_override or _infer_topic(chunk["content"], source_name)

        vectors.append({
            "id":     f"{source_name}_{chunk['chunk_id']}_{uuid.uuid4().hex[:6]}",
            "values": embedding,
            "metadata": {
                "topic":    topic,
                "content":  chunk["content"],
                "source":   source_name,
                "page":     chunk.get("page", 0),
                "chunk_id": chunk["chunk_id"]
            }
        })

    # ── Step 5: Pinecone Upsert ───────────────────────────────────────────────
    print(f"\n[Step 5] {len(vectors)} vectors Pinecone mein upload ho rahe hain...")
    pinecone_service.upsert_vectors(vectors)

    # ── Summary ───────────────────────────────────────────────────────────────
    stats = pinecone_service.get_index_stats()
    print(f"\n{'='*60}")
    print(f"  Ingestion Mukammal!")
    print(f"  PDF:              {source_name}")
    print(f"  Chunks upload:    {len(vectors)}")
    print(f"  Total in index:   {stats.get('total_vector_count', 'unknown')}")
    print(f"{'='*60}\n")


def ingest_folder(folder_path: str):
    """Folder mein saari PDF files ingest karta hai."""
    if not os.path.isdir(folder_path):
        print(f"ERROR: '{folder_path}' valid directory nahi hai.")
        sys.exit(1)

    pdf_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf")
    ]

    if not pdf_files:
        print(f"Koi PDF nahi mili: {folder_path}")
        return

    print(f"{len(pdf_files)} PDF(s) mili hain:")
    for f in pdf_files:
        print(f"  - {f}")

    for pdf_file in pdf_files:
        ingest_pdf(pdf_file)


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="PDF files ko Pinecone vector database mein ingest karo."
    )
    parser.add_argument("--pdf",    type=str, help="Single PDF file ka path")
    parser.add_argument("--folder", type=str, help="Folder ka path jisme multiple PDFs hain")
    parser.add_argument("--topic",  type=str, default=None,
                        help="Saare chunks ke liye topic label override")

    args = parser.parse_args()

    if not args.pdf and not args.folder:
        parser.print_help()
        print("\nERROR: --pdf ya --folder zarur specify karein.")
        sys.exit(1)

    if args.folder:
        ingest_folder(args.folder)
    elif args.pdf:
        ingest_pdf(r"C:\Users\hpksa\Downloads\dataset_quiz.pdf", topic_override=args.topic)