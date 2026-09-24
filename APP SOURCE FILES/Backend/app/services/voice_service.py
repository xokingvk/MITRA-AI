import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from app.config import settings
from app.core.exceptions import MitraException

logger = logging.getLogger(__name__)


class VoiceService:
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""

    def _get_gemini_client(self):
        """Returns a Gemini client if API key is configured."""
        if not self.gemini_api_key:
            return None
        return genai.Client(api_key=self.gemini_api_key)

    async def transcribe_audio(self, audio_bytes: bytes, filename: str, mime_type: str, language_code: Optional[str] = "en-IN") -> Dict[str, Any]:
        """
        Transcribes audio bytes to text using Gemini multimodal audio understanding.
        """
        if not audio_bytes or len(audio_bytes) == 0:
            raise MitraException("Received empty audio recording. Please speak into your microphone and try again.", status_code=400)

        client = self._get_gemini_client()
        if not client:
            raise MitraException("Voice transcription service is unavailable. Please configure GEMINI_API_KEY in backend environment.", status_code=503)

        try:
            logger.info(f"Transcribing audio ({len(audio_bytes)} bytes) via Gemini ({settings.GEMINI_MODEL})...")

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

    async def synthesize_speech(self, text: str, target_language_code: Optional[str] = "en-IN") -> Dict[str, Any]:
        """
        Synthesizes text into audio using browser Web Speech API (client-side).
        Returns a message indicating the frontend should use browser speech synthesis.
        """
        if not text or not text.strip():
            return {"audio_base64": None, "format": "wav", "message": "Empty text"}

        # With no external TTS service, instruct the frontend to use browser speech synthesis
        return {
            "audio_base64": None,
            "format": "wav",
            "message": "Use browser speech synthesis for TTS playback."
        }
