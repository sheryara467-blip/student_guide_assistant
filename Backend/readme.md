# Student Guide Assistant

A RAG-powered chatbot that answers student questions from university PDF documents.

## Stack

- **Backend:** FastAPI + Pinecone + Groq + fastembed (BAAI/bge-small-en-v1.5) + scikit-learn
- **Frontend:** React + Vite
- **Deployed:** Backend on Render, Frontend on Vercel

## How It Works

1. User asks a question
2. Question is converted to a 384-dim vector using fastembed
3. Pinecone returns the most relevant chunks from the indexed university documents
4. Groq LLM generates a grounded answer from those chunks

## Running Locally

**Backend:**
```bash
cd Backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

**Backend** (`Backend/.env`):
```
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
GROQ_API_KEY=
```

**Frontend** (`frontend/.env.local`):
```
VITE_API_URL=http://localhost:8000
```