# MITRA AI — Master Multilingual RAG Backend

Production-ready text-based multilingual Retrieval-Augmented Generation (RAG) backend for **MITRA AI**, built with **FastAPI**, **Sentence Transformers**, **FAISS**, and **Google Gemini API (`google-genai`)**.

---

## 🌟 Features

* **Text-Based Multilingual RAG**: Instant grounding of answers against official government health scheme documents.
* **Google Gemini Integration**: Grounded response generation with safety guardrails and zero Sarvam AI dependencies.
* **9 Indian Languages**: Supported language targets include English, Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Bengali, and Gujarati.
* **FAISS Vector Store**: Fast page-aware vector similarity search using `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
* **Temporary Personal Certificates**: Upload user certificates (income, age, caste) for session-scoped eligibility context without corrupting the permanent vector index.
* **Scheme Eligibility Guidance**: Rule-assisted & AI-synthesized health scheme matching based on user demographic profiles.
* **Production Ready**: Modular service architecture, Pydantic data validation, automated test suite, and ready for deployment on **Render**.

---

## 📁 Project Structure

```text
Backend/
├── app/
│   ├── main.py                  # FastAPI application entrypoint & lifecycle
│   ├── config.py                # Environment settings & Pydantic Config
│   ├── dependencies.py          # Service singletons & dependency injection
│   │
│   ├── api/                     # REST API endpoints
│   │   ├── chat.py              # POST /api/chat (Multilingual RAG chat)
│   │   ├── documents.py         # POST /api/documents/upload (Temporary documents)
│   │   ├── schemes.py           # GET /api/schemes & POST /api/schemes/eligibility
│   │   ├── rag.py               # POST /api/rag/ingest (Permanent RAG ingestion)
│   │   └── health.py            # GET /health & GET / (Status checks)
│   │
│   ├── services/                # Modular domain services
│   │   ├── gemini_service.py    # Google Gemini API integration
│   │   ├── embedding_service.py # SentenceTransformer embeddings
│   │   ├── retrieval_service.py # FAISS vector search & disk persistence
│   │   ├── rag_service.py       # Master RAG pipeline orchestrator
│   │   ├── document_service.py  # PDF processing & temp doc handling
│   │   ├── scope_service.py     # Intent classification & safety guardrails
│   │   ├── conversation_service.py # Session memory & turn management
│   │   └── eligibility_service.py # Scheme matching logic
│   │
│   ├── models/                  # Pydantic schemas
│   │   ├── chat_models.py
│   │   ├── document_models.py
│   │   └── scheme_models.py
│   │
│   ├── core/                    # Core configuration & prompts
│   │   ├── prompts.py           # Gemini RAG system instruction & prompt templates
│   │   ├── language_config.py   # 9 languages mapping & localized disclaimers
│   │   └── exceptions.py       # Custom backend exceptions
│   │
│   └── utils/                   # Helper utilities
│       ├── pdf_utils.py         # PyMuPDF/PyPDF page-aware extraction
│       ├── text_utils.py        # Text cleaning & word chunking
│       └── source_utils.py      # Source formatting & deduplication
│
├── data/
│   ├── permanent_documents/     # Official health scheme PDFs
│   ├── temporary_documents/     # User uploaded personal document cache
│   └── vector_store/            # FAISS index & metadata JSON storage
│
├── tests/                       # Pytest automated test suite
├── requirements.txt
├── .env.example
├── .gitignore
├── render.yaml                  # Render deployment configuration
└── README.md
```

---

## 🛠️ Quick Setup & Installation

### 1. Prerequisites
* Python 3.10+ installed
* Git

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and set your `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

---

## 🚀 Running the Server Locally

Start the backend with Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive Swagger Docs: `http://localhost:8000/docs`
* ReDoc UI: `http://localhost:8000/redoc`

---

## 🧪 Running Automated Tests

Run the complete pytest test suite:
```bash
pytest -v
```

---

## 📡 API Endpoint Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health status, vector count & Gemini configuration status |
| `POST` | `/api/chat` | Main text RAG endpoint for 9 Indian languages |
| `POST` | `/api/documents/upload` | Upload temporary personal certificate (Income/Age proof) |
| `POST` | `/api/schemes/eligibility` | Evaluate scheme eligibility against user profile |
| `POST` | `/api/rag/ingest` | Re-ingest permanent health PDFs into FAISS index |
| `GET` | `/api/schemes` | Summary of indexed schemes & sources |

---

## 🌐 Deploying to Render

1. Connect your GitHub repository to Render.
2. Select **New Web Service**.
3. Choose Environment: **Python 3**.
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables on Render dashboard:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `GEMINI_MODEL`: `gemini-2.5-flash`
   - `ENVIRONMENT`: `production`

---

## 🔒 Safety & Limitations

* **No Official Approval**: The assistant explicitly states that eligibility must be confirmed with official authorities.
* **Medical Guardrails**: Medical diagnosis or dosage requests are intercepted and directed to medical professionals.
* **Data Isolation**: Uploaded user certificates remain temporary and are **never** appended to the permanent FAISS vector store.
