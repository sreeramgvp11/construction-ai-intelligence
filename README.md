# Construction Project Intelligence Platform

AI-powered AEC project assistant for construction documents, RFIs, change orders, contracts, blueprints, and site reports.

## What it does

Construction teams deal with many project documents: RFIs, drawings, contracts, site reports, inspection notes, and change orders. This platform lets users upload project documents and ask natural language questions such as:

- Which change orders affect the electrical system?
- What tasks are behind schedule?
- Summarize all RFIs related to HVAC.
- What contract clauses mention delays or penalties?
- What safety issues appeared in recent site reports?

## Core AI Features

- OCR/document extraction
- RAG over construction documents
- Multi-agent workflows
- Document classification
- Citation-based answers
- Project risk summaries

## Tech Stack

- Python
- FastAPI
- PostgreSQL + pgvector
- OpenAI API
- LangGraph
- Redis
- Docker

## MVP Scope

### Phase 1
- Upload PDFs
- Extract text
- Chunk documents
- Generate embeddings
- Store chunks
- Ask questions using RAG

### Phase 2
- Add document classification
- Add RFI/change order/site report agents
- Add project risk summary

### Phase 3
- Add blueprint/image OCR
- Add dashboard
- Add role-based project access

## Run Locally

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
cp .env.example .env

uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Author

Sreeram Gangavarapu
