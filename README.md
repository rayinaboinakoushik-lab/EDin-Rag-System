# EDin-RAG-System

> **A Dockerized Retrieval-Augmented Generation system that ingests educational YouTube lectures and generates grounded, source-cited answers to student queries using FastAPI, pgvector, and Google Gemini.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?logo=postgresql)](https://github.com/pgvector/pgvector)
[![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?logo=google)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

Students preparing for competitive exams like NEET rely heavily on educational YouTube lectures for guidance on counselling rounds, admission strategies, cutoff interpretations, and rank predictions. However, extracting precise information from hours of video content is difficult, time-consuming, and inefficient.

**EDin-RAG-System** solves this by transforming educational video transcripts into a searchable, intelligent knowledge base. The system retrieves the most relevant lecture segments and uses Google Gemini to generate accurate, grounded answers — complete with source references and confidence scores.

A key advantage of this system is its **data sourcing strategy**: it ingests content from domain experts who analyze and predict NEET exam results, cutoffs, and ranks within days of the exam — making the knowledge base significantly more current and accurate than official data sources that arrive months later.

Unlike generic AI assistants that rely on static training data, EDin-RAG-System dynamically retrieves knowledge directly from expert educational content.

---

## ✨ Key Features

- 🎥 **YouTube Lecture Ingestion** — Automatically fetches and processes educational video transcripts
- 🧩 **Semantic Chunking** — Splits transcripts into meaningful, retrievable segments
- 🗄️ **Vector Storage with pgvector** — Stores embeddings in PostgreSQL for fast similarity search
- 🔍 **Retrieval-Augmented Generation** — Grounds every answer in retrieved lecture content
- 🤖 **Google Gemini Integration** — Uses Gemini for both embeddings and LLM generation (zero extra dependencies)
- 📊 **Confidence Scoring** — Every response includes a confidence score for answer reliability
- 🔗 **Source Tracking** — Returns source chunk IDs with every answer for full traceability
- 🌐 **Multilingual Support** — Ingests Telugu content and answers queries in English via cross-lingual embeddings (Gemini handles the language bridge automatically)
- ⚡ **FastAPI REST API** — Clean, documented API with Swagger UI out of the box
- 🐳 **Fully Dockerized** — One command to run the entire system
- 🔄 **Automated Ingestion Pipeline** — Detects and ingests new videos automatically

---

## 🏗️ System Architecture

```
User Query
    │
    ▼
┌─────────────┐
│  FastAPI    │  ← REST API Layer
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Gemini Embeddings  │  ← Query → Vector
└──────┬──────────────┘
       │
       ▼
┌──────────────────────────┐
│  pgvector Similarity     │  ← Retrieve top-k chunks
│  Search (PostgreSQL)     │
└──────┬───────────────────┘
       │
       ▼
┌─────────────────────┐
│  Relevant Lecture   │  ← Retrieved context
│  Chunks             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Gemini LLM         │  ← Grounded generation
└──────┬──────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  {answer, sources[], confidence}     │  ← Structured response
└──────────────────────────────────────┘
```

---

## 🔄 Data Ingestion Pipeline

```
YouTube Expert Lectures
         │
         ▼
┌─────────────────────┐
│  Fetch Metadata     │  ← Video ID, title, channel
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Extract Transcript │  ← Raw text from video
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Clean & Chunk      │  ← Semantic text segmentation
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Generate Embeddings│  ← Gemini Embedding API
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Store in pgvector  │  ← PostgreSQL vector storage
└─────────────────────┘
```

> **Why expert YouTube channels?** The system specifically targets NEET domain experts who publish predictions and analysis within days of an exam — long before official cutoff data is released. This gives the system a major freshness advantage over static data sources.

---

## 📁 Project Structure

```
EDin-Rag-System/
├── src/
│   ├── api/
│   │   └── main.py                  # FastAPI app entry point
│   │
│   ├── automation/
│   │   ├── detect_new_videos.py     # Auto-detect new YouTube uploads
│   │   ├── ingest_transcripts.py    # Trigger ingestion pipeline
│   │   └── init_db.py               # Database initialization
│   │
│   ├── core/
│   │   └── logger.py                # Centralized logging
│   │
│   ├── phase1/
│   │   ├── fetch_metadata.py        # YouTube video metadata
│   │   └── fetch_transcript.py      # Transcript extraction
│   │
│   └── rag/
│       ├── app.py                   # RAG orchestration
│       ├── chunk_transcripts.py     # Text chunking logic
│       ├── embeddings.py            # Gemini embedding generation
│       ├── retrieval.py             # pgvector similarity search
│       ├── generation.py            # Gemini LLM generation
│       └── migrate_chunks.py        # DB migration utilities
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI + Uvicorn |
| **LLM Generation** | Google Gemini |
| **Embeddings** | Google Gemini Embedding API |
| **Vector Database** | PostgreSQL + pgvector |
| **Transcript Source** | YouTube (via transcript API) |
| **Containerization** | Docker + Docker Compose |
| **Language** | Python 3.10+ |

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed
- A **Google Gemini API key** — get one at [Google AI Studio](https://aistudio.google.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/rayinaboinakoushik-lab/EDin-Rag-System.git
cd EDin-Rag-System
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=edin_rag
```

### 3. Start All Containers

```bash
docker compose up --build
```

This spins up:
- The **FastAPI** application server
- The **PostgreSQL + pgvector** database

### 4. Access the API

Open your browser and navigate to:

```
http://localhost:8000/docs
```

This opens the interactive **Swagger UI** where you can explore and test all endpoints.

---

## 💬 Example Usage

### Ask a Question

**Request:**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/ask' \
  -H 'Content-Type: application/json' \
  -d '{"question": "What is the cutoff for BC-D category?"}'
```

**Response:**
```json
{
  "answer": "BC-D government cutoff is 415 marks. For private colleges, the cutoff is expected to be around 403 to 425 ranks lower than the government cutoff, with marks potentially falling between 402 and 401. In the third round, the cutoff for BC-D is expected to be around 401 marks.",
  "sources": [98, 140, 85, 20, 97],
  "confidence": 0.69
}
```

| Field | Description |
|---|---|
| `answer` | LLM-generated response grounded in lecture content |
| `sources` | IDs of the lecture chunks used to generate the answer |
| `confidence` | Retrieval confidence score (0–1) |

---

## 🗺️ Roadmap

- [x] Core RAG pipeline with FastAPI
- [x] pgvector integration for semantic search
- [x] Google Gemini embeddings + generation
- [x] Confidence scoring and source tracking
- [x] Docker containerization
- [x] Multilingual support — Telugu ingestion with English query answering
- [ ] Automated detection and ingestion of new YouTube videos (Mission 2)
- [ ] Streaming responses for real-time interaction
- [ ] Web interface for student queries
- [ ] Expansion to additional exam domains (JEE, UPSC, etc.)
- [ ] Cloud deployment (GCP / Render)

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

Please make sure your code follows the existing structure and includes relevant comments.

---

## 💡 Why This Project Matters

Educational content on platforms like YouTube contains valuable, time-sensitive insights that are impossible to search using traditional keyword methods. NEET counselling experts publish predictions and cutoff analyses within days of an exam — information that is highly accurate but buried in hours of video.

This project demonstrates how **Retrieval-Augmented Generation** can transform unstructured expert video content into a structured, queryable knowledge assistant — capable of delivering precise, source-grounded answers to complex domain-specific questions in real time.

---

## 👤 Author

**Koushik Rayinaboina**
- GitHub: [@rayinaboinakoushik-lab](https://github.com/rayinaboinakoushik-lab)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
