# Research PDF Agent

This project provides a lightweight AI research assistant that lets you upload any number of PDFs, index them, and query them with an API. It stores PDFs on disk, indexes text with SQLite FTS, and optionally uses OpenAI to generate responses.

## Features
- Upload multiple PDFs at once.
- Unlimited storage (bounded by disk capacity).
- Full-text search over PDF contents.
- Optional OpenAI-powered answers when `OPENAI_API_KEY` is set.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## API

### Upload PDFs

```bash
curl -F "files=@paper1.pdf" -F "files=@paper2.pdf" http://localhost:8000/documents/upload
```

### List PDFs

```bash
curl http://localhost:8000/documents
```

### Ask a question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize the findings", "top_k": 5}'
```

## Storage
- PDFs are stored in `data/uploads/`.
- The SQLite index lives in `data/index.sqlite`.

Set custom paths with:

```bash
export PDF_AGENT_DB=/path/to/index.sqlite
export PDF_AGENT_STORAGE=/path/to/uploads
```
