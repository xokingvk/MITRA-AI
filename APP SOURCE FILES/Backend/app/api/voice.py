import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.voice_service import VoiceService
from app.dependencies import get_voice_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice Recognition & Synthesis"])

class SynthesisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to synthesize to audio")
    language_code: Optional[str] = Field("en-IN", description="Language code e.g. hi-IN, ta-IN, te-IN, en-IN")

class SynthesisResponse(BaseModel):
    audio_base64: Optional[str] = Field(None, description="Base64 encoded audio (WAV format)")
    format: str = Field("wav", description="Audio format")
    message: Optional[str] = Field(None, description="Status or fallback message")

class TranscriptionResponse(BaseModel):
    transcript: str = Field(..., description="Recognized speech text")
    language_code: Optional[str] = Field("en-IN", description="Resolved language code")
    provider: Optional[str] = Field("gemini", description="STT Provider used")

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_voice(
    file: UploadFile = File(..., description="Audio recording file from browser MediaRecorder"),
    language_code: Optional[str] = Form("en-IN", description="Expected audio language code"),
    voice_service: VoiceService = Depends(get_voice_service)
):
    """
    Receives recorded audio from the browser, transcribes it via Gemini audio understanding,
    and returns the recognized text for injection into the chat pipeline.
    """
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio recording submitted.")
        
        result = await voice_service.transcribe_audio(
            audio_bytes=audio_bytes,
            filename=file.filename or "recording.webm",
            mime_type=file.content_type or "audio/webm",
            language_code=language_code
        )
        return TranscriptionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing voice: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

@router.post("/synthesize", response_model=SynthesisResponse)
async def synthesize_speech(
    request: SynthesisRequest,
    voice_service: VoiceService = Depends(get_voice_service)
):
    """
    Synthesizes text into speech audio. Returns base64 audio data or browser TTS fallback signal.
    """
    try:
        result = await voice_service.synthesize_speech(
            text=request.text,
            target_language_code=request.language_code
        )
        return SynthesisResponse(**result)
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        return SynthesisResponse(audio_base64=None, format="wav", message=str(e))
