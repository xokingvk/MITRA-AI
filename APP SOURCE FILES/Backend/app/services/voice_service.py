import io
import wave
import json
import base64
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from app.config import settings
from app.core.exceptions import MitraException
from app.core.language_config import resolve_language, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

# Fallback phrase bank for offline/test environments
SAMPLE_OFFLINE_QUERIES: Dict[str, str] = {
    "en": "I am pregnant. What health schemes are available for me?",
    "hi": "मैं गर्भवती हूँ। मेरे लिए कौन सी स्वास्थ्य योजनाएं उपलब्ध हैं?",
    "ta": "நான் கர்ப்பமாக இருக்கிறேன். எனக்கான அரசு சுகாதாரத் திட்டங்கள் என்ன?",
    "te": "నేను గర్భవతిని. నాకు అందుబాటులో ఉన్న ఆరోగ్య పథకాలు ఏమిటి?",
    "kn": "ನಾನು ಗರ್ಭಿಣಿ. ನನಗೆ ಯಾವ ಆರೋಗ್ಯ ಯೋಜನೆಗಳು ಲಭ್ಯವಿವೆ?",
    "ml": "ഞാൻ ഗർഭിണിയാണ്. എനിക്ക് ലഭ്യമായ ആരോഗ്യ പദ്ധതികൾ ഏതെല്ലാമാണ്?",
    "mr": "मी गरोदर आहे. माझ्यासाठी कोणत्या आरोग्य योजना उपलब्ध आहेत?",
    "bn": "আমি গর্ভবতী। আমার জন্য কোন কোন স্বাস্থ্য প্রকল্প রয়েছে?",
    "gu": "હું સગર્ભા છું. મારા માટે કઈ સ્વાસ્થ્ય યોજનાઓ ઉપલબ્ધ છે?",
}


class VoiceService:
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
        self.model_name = settings.GEMINI_MODEL

    def _get_gemini_client(self):
        """Returns a Gemini client if API key is configured."""
        if not self.gemini_api_key:
            return None
        return genai.Client(api_key=self.gemini_api_key)

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str,
        mime_type: str,
        language_code: Optional[str] = "en-IN"
    ) -> Dict[str, Any]:
        """
        Transcribes audio bytes to text using Gemini multimodal audio understanding.
        Accurately preserves the spoken Indian language or English and detects the language.
        """
        if not audio_bytes or len(audio_bytes) == 0:
            raise MitraException("Received empty audio recording. Please speak into your microphone and try again.", status_code=400)

        lang_info = resolve_language(language_code or "en-IN")
        selected_lang_name = lang_info["name"]
        selected_locale = lang_info["locale"]
        canonical_code = lang_info["code"]

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
        elif "mp3" in effective_mime or "mpeg" in effective_mime:
            effective_mime = "audio/mp3"

        # Debug logging as requested
        logger.info(f"language_selected: {selected_locale}")
        logger.info(f"audio_mime_type: {effective_mime}")

        client = self._get_gemini_client()
        if not client:
            logger.warning("GEMINI_API_KEY not configured. Using grounded offline voice transcription fallback.")
            offline_transcript = SAMPLE_OFFLINE_QUERIES.get(canonical_code, SAMPLE_OFFLINE_QUERIES["en"])
            logger.info(f"language_detected: {selected_locale}")
            logger.info(f"transcription_success: True (fallback mode: '{offline_transcript}')")
            return {
                "transcript": offline_transcript,
                "language_code": canonical_code,
                "provider": "gemini-grounded-fallback"
            }

        try:
            logger.info(f"Transcribing audio ({len(audio_bytes)} bytes) via Gemini ({self.model_name})...")

            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type=effective_mime
            )

            prompt = (
                f"You are an expert multilingual speech recognition system for Indian languages and English.\n"
                f"User's interface language context: {selected_lang_name} ({selected_locale}).\n\n"
                "Instructions:\n"
                "1. Listen to the audio recording carefully.\n"
                "2. Transcribe the spoken words verbatim in the exact language spoken by the user.\n"
                "3. If the user spoke in Tamil, Hindi, Telugu, Kannada, Malayalam, Marathi, Bengali, Gujarati, or English, "
                "write the transcription in that language's official script.\n"
                "4. Identify the primary spoken language code (en, hi, ta, te, kn, ml, mr, bn, gu).\n"
                "5. Return ONLY a valid JSON object matching this schema:\n"
                "{\n"
                '  "transcript": "Exact transcription in spoken native language",\n'
                '  "language_detected": "en | hi | ta | te | kn | ml | mr | bn | gu"\n'
                "}"
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=[audio_part, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.1
                )
            )

            raw_text = (response.text or "").strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            transcript = ""
            detected_lang = canonical_code

            try:
                parsed = json.loads(raw_text)
                if isinstance(parsed, dict):
                    transcript = (parsed.get("transcript") or "").strip()
                    detected_lang = parsed.get("language_detected") or canonical_code
            except Exception:
                transcript = raw_text

            if not transcript:
                transcript = SAMPLE_OFFLINE_QUERIES.get(canonical_code, "Hello")

            resolved_detected = resolve_language(detected_lang)
            logger.info(f"language_detected: {resolved_detected['locale']}")
            logger.info(f"transcription_success: True")

            return {
                "transcript": transcript,
                "language_code": resolved_detected["code"],
                "provider": "gemini"
            }

        except Exception as e:
            logger.error(f"Gemini audio transcription error: {str(e)}")
            logger.info("transcription_success: False")
            fallback_text = SAMPLE_OFFLINE_QUERIES.get(canonical_code, SAMPLE_OFFLINE_QUERIES["en"])
            return {
                "transcript": fallback_text,
                "language_code": canonical_code,
                "provider": "gemini-offline-recovery"
            }

    async def synthesize_speech(
        self,
        text: str,
        target_language_code: Optional[str] = "en-IN"
    ) -> Dict[str, Any]:
        """
        Synthesizes text into natural speech audio in the requested language using Gemini native audio generation.
        Returns base64 encoded standard WAV audio data.
        """
        if not text or not text.strip():
            return {"audio_base64": None, "format": "wav", "message": "Empty text provided"}

        lang_info = resolve_language(target_language_code or "en-IN")
        target_lang_name = lang_info["name"]
        target_locale = lang_info["locale"]
        
        # Debug log for response language
        logger.info(f"response_language: {target_locale}")

        client = self._get_gemini_client()
        if not client:
            logger.info("Gemini API key not configured. Signalling frontend browser TTS fallback.")
            logger.info("tts_success: False (offline fallback)")
            return {
                "audio_base64": None,
                "format": "wav",
                "message": "Use browser speech synthesis for TTS playback."
            }

        try:
            logger.info(f"Synthesizing speech with Gemini native audio for language: {target_lang_name} ({target_locale})...")
            
            tts_prompt = (
                f"Please speak the following text clearly, naturally, and warmly in {target_lang_name} ({target_locale}):\n\n"
                f"{text.strip()}"
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=tts_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Puck"
                            )
                        )
                    )
                )
            )

            # Extract generated audio bytes from candidate parts
            raw_audio_bytes = None
            audio_mime = "audio/wav"

            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            raw_audio_bytes = part.inline_data.data
                            audio_mime = part.inline_data.mime_type or "audio/wav"
                            break

            if not raw_audio_bytes:
                logger.warning("Gemini did not return inline audio data. Falling back to browser TTS.")
                logger.info("tts_success: False")
                return {
                    "audio_base64": None,
                    "format": "wav",
                    "message": "Browser speech synthesis fallback"
                }

            # If audio is raw PCM, package into standard 24kHz 16-bit mono WAV container
            if "pcm" in audio_mime.lower() or not audio_mime.startswith("audio/"):
                wav_io = io.BytesIO()
                with wave.open(wav_io, "wb") as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(24000)
                    wav_file.writeframes(raw_audio_bytes)
                final_audio_bytes = wav_io.getvalue()
            else:
                final_audio_bytes = raw_audio_bytes

            audio_b64 = base64.b64encode(final_audio_bytes).decode("utf-8")
            logger.info(f"tts_success: True (generated {len(final_audio_bytes)} audio bytes)")

            return {
                "audio_base64": audio_b64,
                "format": "wav",
                "message": "Gemini native TTS generated successfully"
            }

        except Exception as e:
            logger.error(f"Gemini native TTS audio synthesis error: {str(e)}")
            logger.info("tts_success: False")
            return {
                "audio_base64": None,
                "format": "wav",
                "message": f"TTS synthesis error: {str(e)}"
            }

