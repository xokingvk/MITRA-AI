import logging
import base64
import httpx
from typing import Optional, Dict, Any
from app.config import settings
from app.core.exceptions import MitraException

logger = logging.getLogger(__name__)

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

class VoiceService:
    def __init__(self):
        self.sarvam_api_key = settings.SARVAM_API_KEY.strip()
        self.stT_model = settings.SARVAM_STT_MODEL
        self.tts_model = settings.SARVAM_TTS_MODEL

    async def transcribe_audio(self, audio_bytes: bytes, filename: str, mime_type: str, language_code: Optional[str] = "en-IN") -> Dict[str, Any]:
        """
        Transcribes audio bytes to text using Sarvam STT if configured, or Gemini multimodal audio transcription as fallback.
        """
        if not audio_bytes or len(audio_bytes) == 0:
            raise MitraException("Received empty audio recording. Please speak into your microphone and try again.", status_code=400)

        # 1. Try Sarvam STT if API Key is configured
        if self.sarvam_api_key:
            try:
                logger.info(f"Transcribing audio ({len(audio_bytes)} bytes) via Sarvam AI ({self.stT_model})...")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {
                        "api-subscription-key": self.sarvam_api_key
                    }
                    data = {
                        "model": self.stT_model,
                        "language_code": language_code or "en-IN"
                    }
                    files = {
                        "file": (filename or "recording.webm", audio_bytes, mime_type or "audio/webm")
                    }
                    response = await client.post(SARVAM_STT_URL, headers=headers, data=data, files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        transcript = result.get("transcript", "").strip()
                        detected_lang = result.get("language_code", language_code)
                        logger.info(f"Sarvam transcription successful: '{transcript}'")
                        return {
                            "transcript": transcript,
                            "language_code": detected_lang,
                            "provider": "sarvam"
                        }
                    else:
                        logger.warning(f"Sarvam STT failed with status {response.status_code}: {response.text}")
            except Exception as e:
                logger.warning(f"Sarvam STT exception: {str(e)}. Falling back to Gemini audio understanding...")

        # 2. Multimodal Audio Transcription via Gemini
        if settings.GEMINI_API_KEY:
            try:
                logger.info("Transcribing audio via Google Gemini audio model...")
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                
                # Determine standard MIME type for Gemini
                effective_mime = mime_type or "audio/webm"
                if "webm" in effective_mime:
                    effective_mime = "audio/webm"
                elif "mp4" in effective_mime or "m4a" in effective_mime:
                    effective_mime = "audio/mp4"
                elif "wav" in effective_mime:
                    effective_mime = "audio/wav"
                elif "ogg" in effective_mime:
                    effective_mime = "audio/ogg"

                audio_part = types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=effective_mime
                )

                prompt = (
                    "Listen to this audio recording and transcribe the user's speech accurately. "
                    "Return ONLY the plain transcript text. Do not add explanations, notes, or markdown."
                )

                response = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=[audio_part, prompt]
                )

                transcript = (response.text or "").strip()
                logger.info(f"Gemini transcription successful: '{transcript}'")
                return {
                    "transcript": transcript,
                    "language_code": language_code or "en-IN",
                    "provider": "gemini"
                }

            except Exception as e:
                logger.error(f"Gemini audio transcription failed: {str(e)}")
                raise MitraException(f"Voice transcription failed: {str(e)}", status_code=500)

        raise MitraException("Voice transcription service is unavailable. Please configure SARVAM_API_KEY or GEMINI_API_KEY in backend environment.", status_code=503)

    async def synthesize_speech(self, text: str, target_language_code: Optional[str] = "en-IN") -> Dict[str, Any]:
        """
        Synthesizes text into audio using Sarvam TTS if configured.
        """
        if not text or not text.strip():
            return {"audio_base64": None, "format": "wav", "message": "Empty text"}

        if not self.sarvam_api_key:
            return {"audio_base64": None, "format": "wav", "message": "Sarvam API key not configured"}

        try:
            logger.info(f"Synthesizing text ({len(text)} chars) via Sarvam AI TTS...")
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "api-subscription-key": self.sarvam_api_key,
                    "Content-Type": "application/json"
                }
                # Limit text chunk to 500 chars for TTS
                payload = {
                    "inputs": [text[:490].strip()],
                    "target_language_code": target_language_code or "en-IN",
                    "speaker": "meera",
                    "model": self.tts_model
                }
                response = await client.post(SARVAM_TTS_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    audios = data.get("audios", [])
                    if audios and len(audios) > 0:
                        return {
                            "audio_base64": audios[0],
                            "format": "wav",
                            "provider": "sarvam"
                        }
                logger.warning(f"Sarvam TTS failed with status {response.status_code}: {response.text}")
                return {"audio_base64": None, "format": "wav", "message": "TTS synthesis failed"}
        except Exception as e:
            logger.warning(f"Sarvam TTS exception: {str(e)}")
            return {"audio_base64": None, "format": "wav", "message": str(e)}
