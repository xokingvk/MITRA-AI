import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import MitraException
from app.api import health, chat, documents, schemes, voice

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
    Lightweight Gemini-only architecture with zero heavy embedding models or vector index loading.
    """
    logger.info("Initializing MITRA AI Gemini Backend service...")
    yield
    logger.info("Shutting down MITRA AI Gemini Backend service.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Lightweight Multilingual Health Schemes Assistant Backend powered directly by Google Gemini.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend integration
origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"]
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
app.include_router(voice.router)
app.include_router(schemes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
