import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import MitraException
from app.api import health, chat, documents, rag, schemes
from app.dependencies import get_retrieval_service, get_document_service

# Setup logging configuration
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mitra_backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifespan context.
    On startup: Automatically loads persistent FAISS index or ingests default PDF if index is missing.
    """
    logger.info("Initializing MITRA AI Backend service...")
    retrieval_svc = get_retrieval_service()
    doc_svc = get_document_service()

    # Attempt loading pre-existing FAISS vector store
    if not retrieval_svc.load_index():
        logger.info("FAISS vector store not found. Attempting automatic ingestion of permanent scheme PDFs...")
        try:
            doc_svc.ingest_permanent_documents()
        except Exception as e:
            logger.error(f"Failed automatic initial ingestion of scheme PDFs: {str(e)}")
    
    yield
    logger.info("Shutting down MITRA AI Backend service.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Multilingual RAG Backend for MITRA AI Health Schemes Assistant using Google Gemini & FAISS.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend integration
origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(MitraException)
async def mitra_exception_handler(request: Request, exc: MitraException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details
        }
    )

# Include API Routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(rag.router)
app.include_router(schemes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
