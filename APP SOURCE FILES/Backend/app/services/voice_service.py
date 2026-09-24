import io
import os
import wave
import json
import base64
import logging
import tempfile
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from app.config import settings
from app.core.exceptions import MitraException
from app.core.language_config import resolve_language, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.gemini_api_key = settings.GEMINI_API_KEY.strip() if settings.GEMINI_API_KEY else ""
        self.model_name = settings.GEMINI_MODEL
        self.transcribe_model = settings.GEMINI_TRANSCRIBE_MODEL

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
        Transcribes audio bytes to verbatim text using Gemini 3.5 Transcribe (Interactions API & Files upload).
        Accurately transcribes verbatim whatever the user actually spoke in their native language or English.
        """
        if not audio_bytes or len(audio_bytes) == 0:
            raise MitraException("Received empty audio recording. Please speak into your microphone and try again.", status_code=400)

        lang_info = resolve_language(language_code or "en-IN")
        selected_lang_name = lang_info["name"]
        selected_locale = lang_info["locale"]
        canonical_code = lang_info["code"]

        # Determine standard MIME type and file extension for Gemini
        effective_mime = mime_type or "audio/webm"
        ext = "webm"
        if "webm" in effective_mime:
            effective_mime = "audio/webm"
            ext = "webm"
        elif "mp4" in effective_mime or "m4a" in effective_mime:
            effective_mime = "audio/mp4"
            ext = "mp4"
        elif "wav" in effective_mime:
            effective_mime = "audio/wav"
            ext = "wav"
        elif "ogg" in effective_mime:
            effective_mime = "audio/ogg"
            ext = "ogg"
        elif "mp3" in effective_mime or "mpeg" in effective_mime:
            effective_mime = "audio/mp3"
            ext = "mp3"

        # Required structured debug logging
        logger.info(f"VOICE: audio_received = True, audio_mime_type = {effective_mime}, audio_size = {len(audio_bytes)}")
        logger.info(f"TRANSCRIPTION: model = {self.transcribe_model}")
        logger.info(f"TRANSCRIPTION: language = {selected_locale}")

        client = self._get_gemini_client()
        if not client:
            logger.error("GEMINI_API_KEY is not configured in backend environment.")
            raise MitraException(
                "Gemini API key is not configured on the backend server. Please set GEMINI_API_KEY to enable voice transcription.",
                status_code=503
            )

        tmp_audio_path = None
        uploaded_file = None

        try:
            # 1. Write audio bytes to temporary file on disk for Gemini Files upload
            with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_audio_path = tmp_file.name

            # 2. Upload audio using client.files.upload(...)
            logger.info(f"Uploading audio file ({len(audio_bytes)} bytes) to Gemini Files API for {self.transcribe_model}...")
            uploaded_file = client.files.upload(
                file=tmp_audio_path,
                config=types.UploadFileConfig(
                    mime_type=effective_mime,
                    display_name=f"voice_recording_{selected_locale}.{ext}"
                )
            )
            logger.info(f"Audio file uploaded successfully (URI: {uploaded_file.uri}, Name: {uploaded_file.name})")

            # 3. Call client.interactions.create with minimal request structure
            interaction_kwargs = {
                "model": self.transcribe_model,
                "input": [
                    {
                        "type": "audio",
                        "uri": uploaded_file.uri,
                        "mime_type": uploaded_file.mime_type or effective_mime,
                    }
                ],
            }

            logger.info(f"TRANSCRIPTION: model = {self.transcribe_model}")
            logger.info(f"TRANSCRIPTION: audio_mime_type = {uploaded_file.mime_type or effective_mime}")
            logger.info(f"TRANSCRIPTION: request_keys = {list(interaction_kwargs.keys())}")
            logger.info(f"TRANSCRIPTION: language = {selected_locale}")
            
            interaction = client.interactions.create(**interaction_kwargs)

            transcript = ""
            if hasattr(interaction, "output_text") and interaction.output_text:
                transcript = interaction.output_text.strip()
            elif hasattr(interaction, "output") and isinstance(interaction.output, str):
                transcript = interaction.output.strip()

            if not transcript:
                logger.warning("Gemini returned empty transcript for audio.")
                raise MitraException("Sorry, I couldn't understand the voice recording. Please speak clearly and try again.", status_code=400)

            # Clean any JSON or markdown wrapper if present
            if "```json" in transcript:
                transcript = transcript.split("```json")[1].split("```")[0].strip()
            elif "```" in transcript:
                transcript = transcript.split("```")[1].split("```")[0].strip()

            try:
                parsed = json.loads(transcript)
                if isinstance(parsed, dict) and "transcript" in parsed:
                    transcript = str(parsed["transcript"]).strip()
            except Exception:
                pass

            logger.info(f"TRANSCRIPTION: transcript = '{transcript}'")
            logger.info(f"QUERY: query_sent = '{transcript}'")

            return {
                "transcript": transcript,
                "language_code": canonical_code,
                "language": selected_locale,
                "provider": self.transcribe_model
            }

        except MitraException:
            raise
        except Exception as e:
            error_status = getattr(e, "status_code", getattr(e, "code", None))
            logger.error(
                f"TRANSCRIPTION ERROR: model={self.transcribe_model}, "
                f"mime_type={effective_mime}, "
                f"http_status={error_status}, "
                f"gemini_error_message={str(e)}"
            )
            raise MitraException(f"Sorry, I couldn't understand the voice recording: {str(e)}. Please try again.", status_code=500)
        finally:
            # Clean up local temporary file
            if tmp_audio_path and os.path.exists(tmp_audio_path):
                try:
                    os.remove(tmp_audio_path)
                except Exception:
                    pass
            # Clean up uploaded file from Gemini storage
            if uploaded_file and hasattr(uploaded_file, "name"):
                try:
                    client.files.delete(name=uploaded_file.name)
                except Exception:
                    pass

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
        logger.info(f"TTS: tts_language = {target_locale}")

        client = self._get_gemini_client()
        if not client:
            logger.info("Gemini API key not configured. Signalling frontend browser TTS fallback.")
            logger.info("TTS: tts_success = False (offline fallback)")
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
                logger.info("TTS: tts_success = False")
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
            logger.info(f"TTS: tts_success = True ({len(final_audio_bytes)} audio bytes generated)")

            return {
                "audio_base64": audio_b64,
                "format": "wav",
                "message": "Gemini native TTS generated successfully"
            }

        except Exception as e:
            logger.error(f"Gemini native TTS audio synthesis error: {str(e)}")
            logger.info("TTS: tts_success = False")
            return {
                "audio_base64": None,
                "format": "wav",
                "message": f"TTS synthesis error: {str(e)}"
            }

