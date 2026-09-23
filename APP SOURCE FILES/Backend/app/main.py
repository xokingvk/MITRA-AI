import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import MitraException
from app.api import health, chat, documents, rag, schemes
from app.dependencies import get_retrieval_service

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
    Fast startup: Loads lightweight pre-built FAISS index metadata if present.
    Does NOT trigger expensive PDF ingestion or model loading at startup.
    """
    logger.info("Initializing MITRA AI Backend service...")
    retrieval_svc = get_retrieval_service()

    # Load pre-built FAISS vector store if available (memory footprint < 5MB)
    try:
        if retrieval_svc.load_index():
            logger.info("FAISS vector store metadata loaded successfully.")
        else:
            logger.info("No pre-built FAISS index found. Vector search will load when available.")
    except Exception as e:
        logger.warning(f"Note on initial vector index load: {str(e)}")
    
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
