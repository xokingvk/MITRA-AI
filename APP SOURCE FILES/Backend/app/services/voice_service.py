import io
import os
import wave
import json
import base64
import logging
import tempfile
import subprocess
from typing import Optional, Dict, Any, Tuple
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

    def _convert_to_wav(self, audio_bytes: bytes, original_mime: str, ext: str) -> bytes:
        """
        Robustly converts any input audio format (such as mobile browser audio/webm;codecs=opus,
        iOS Safari audio/mp4, Firefox audio/ogg, MP3, etc.) into standard 16kHz 16-bit mono PCM audio/wav.
        Uses imageio-ffmpeg bundled static binary with multi-strategy fallback.
        """
        if not audio_bytes or len(audio_bytes) == 0:
            raise MitraException("Received empty audio recording. Please speak into your microphone and try again.", status_code=400)

        header = audio_bytes[:32]
        first_bytes_hex = header[:16].hex()

        # 1. If it is already a WAV file and starts with standard RIFF/WAVE header, return directly
        if header.startswith(b"RIFF") and b"WAVE" in header[:16]:
            logger.info("Audio is already a valid standard WAV file (RIFF/WAVE header verified).")
            return audio_bytes

        # 2. Detect container from magic bytes or MIME
        detected_ext = ext
        if header.startswith(b"\x1aE\xdf\xa3"):
            detected_ext = "webm"
        elif header.startswith(b"OggS"):
            detected_ext = "ogg"
        elif b"ftyp" in header[:16] or "mp4" in original_mime.lower() or "m4a" in original_mime.lower():
            detected_ext = "mp4"
        elif header.startswith(b"ID3") or header.startswith(b"\xff\xfb") or "mp3" in original_mime.lower():
            detected_ext = "mp3"
        elif "wav" in original_mime.lower():
            detected_ext = "wav"

        ffmpeg_exe = "ffmpeg"
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception as err:
            logger.warning(f"imageio_ffmpeg notice ({err}), checking system ffmpeg...")

        tmp_in = None
        tmp_out = None

        try:
            with tempfile.NamedTemporaryFile(suffix=f".{detected_ext}", delete=False) as f_in:
                f_in.write(audio_bytes)
                tmp_in = f_in.name

            tmp_out = tmp_in + "_converted.wav"

            # Multi-strategy conversion pipeline
            strategies = [
                # Strategy 1: Auto-probe with error tolerance and generous probe size
                [
                    ffmpeg_exe, "-y",
                    "-err_detect", "ignore_err",
                    "-probesize", "10M",
                    "-analyzeduration", "10M",
                    "-i", tmp_in,
                    "-vn",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    tmp_out
                ],
                # Strategy 2: Explicit Matroska/WebM demuxer
                [
                    ffmpeg_exe, "-y",
                    "-f", "matroska,webm",
                    "-err_detect", "ignore_err",
                    "-i", tmp_in,
                    "-vn",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    tmp_out
                ],
                # Strategy 3: Standard FFmpeg conversion
                [
                    ffmpeg_exe, "-y",
                    "-i", tmp_in,
                    "-vn",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    tmp_out
                ]
            ]

            converted_bytes = None
            last_returncode = -1
            last_stderr = ""

            for idx, cmd in enumerate(strategies):
                logger.info(f"Executing audio conversion strategy {idx + 1} with FFmpeg ({detected_ext} -> WAV)...")
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                last_returncode = result.returncode
                last_stderr = result.stderr.decode("utf-8", errors="ignore")

                if result.returncode == 0 and os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 44:
                    with open(tmp_out, "rb") as f_out:
                        converted_bytes = f_out.read()
                    logger.info(f"FFmpeg conversion succeeded on strategy {idx + 1} ({len(converted_bytes)} bytes WAV generated).")
                    break
                else:
                    logger.warning(f"Strategy {idx + 1} failed (returncode {result.returncode}).")

            if not converted_bytes or len(converted_bytes) <= 44:
                logger.error(
                    f"AUDIO CONVERSION ERROR: original_mime={original_mime}, "
                    f"original_size={len(audio_bytes)}, "
                    f"first_bytes_hex={first_bytes_hex}, "
                    f"returncode={last_returncode}, "
                    f"stderr={last_stderr[-400:] if last_stderr else 'none'}"
                )
                raise MitraException("Sorry, I couldn't process the audio recording from your microphone. Please speak clearly and try again.", status_code=400)

            return converted_bytes

        except MitraException:
            raise
        except Exception as e:
            logger.error(f"Audio conversion exception: {str(e)}")
            raise MitraException("Sorry, I couldn't process the audio recording from your microphone. Please speak clearly and try again.", status_code=400)
        finally:
            if tmp_in and os.path.exists(tmp_in):
                try: os.remove(tmp_in)
                except Exception: pass
            if tmp_out and os.path.exists(tmp_out):
                try: os.remove(tmp_out)
                except Exception: pass

    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str,
        mime_type: str,
        language_code: Optional[str] = "en-IN"
    ) -> Dict[str, Any]:
        """
        Transcribes audio bytes to verbatim text using Gemini 3.5 Transcribe (Interactions API & Files upload).
        Converts browser WebM or other formats to standard WAV before sending to Gemini.
        """
        if not audio_bytes or len(audio_bytes) == 0:
            raise MitraException("Received empty audio recording. Please speak into your microphone and try again.", status_code=400)

        lang_info = resolve_language(language_code or "en-IN")
        selected_lang_name = lang_info["name"]
        selected_locale = lang_info["locale"]
        canonical_code = lang_info["code"]

        original_mime = mime_type or "audio/webm"
        original_size = len(audio_bytes)
        ext = "webm"
        if "wav" in original_mime.lower():
            ext = "wav"
        elif "mp4" in original_mime.lower() or "m4a" in original_mime.lower():
            ext = "mp4"
        elif "ogg" in original_mime.lower():
            ext = "ogg"
        elif "mp3" in original_mime.lower():
            ext = "mp3"
        elif filename and "." in filename:
            ext = filename.split(".")[-1].lower()

        # Explicit Runtime Diagnostic Logs
        logger.info("VOICE_TEST_START")
        logger.info("endpoint=/api/voice/transcribe")
        logger.info("audio_received=True")
        logger.info(f"transcription_model={self.transcribe_model}")
        logger.info(f"original_mime_type={original_mime}")
        logger.info(f"original_filename={filename}")
        logger.info(f"original_audio_size={original_size}")
        logger.info(f"language_requested={selected_locale}")

        # Perform server-side audio conversion to standard WAV
        try:
            converted_audio_bytes = self._convert_to_wav(audio_bytes, original_mime, ext)
            converted_mime = "audio/wav"
            converted_size = len(converted_audio_bytes)
            logger.info(f"converted_mime_type={converted_mime}")
            logger.info(f"converted_audio_size={converted_size}")
            logger.info("conversion_success=True")
        except Exception as conv_err:
            logger.info("conversion_success=False")
            logger.info("VOICE_TEST_END")
            raise

        client = self._get_gemini_client()
        if not client:
            logger.error("GEMINI_API_KEY is not configured in backend environment.")
            logger.info("transcription_success=False")
            logger.info("VOICE_TEST_END")
            raise MitraException(
                "Gemini API key is not configured on the backend server. Please set GEMINI_API_KEY to enable voice transcription.",
                status_code=503
            )

        tmp_audio_path = None
        uploaded_file = None

        try:
            # 1. Write converted standard WAV bytes to temporary file on disk for Gemini Files upload
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(converted_audio_bytes)
                tmp_audio_path = tmp_file.name

            # 2. Upload converted audio using client.files.upload(...) with matching audio/wav MIME type
            logger.info(f"Uploading converted WAV audio ({len(converted_audio_bytes)} bytes) to Gemini Files API for {self.transcribe_model}...")
            uploaded_file = client.files.upload(
                file=tmp_audio_path,
                config=types.UploadFileConfig(
                    mime_type="audio/wav",
                    display_name=f"voice_recording_{selected_locale}.wav"
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
                        "mime_type": uploaded_file.mime_type or "audio/wav",
                    }
                ],
            }

            logger.info("transcription_request_started")
            logger.info(f"request_keys={list(interaction_kwargs.keys())}")
            
            interaction = client.interactions.create(**interaction_kwargs)

            transcript = ""
            if hasattr(interaction, "output_text") and interaction.output_text:
                transcript = interaction.output_text.strip()
            elif hasattr(interaction, "output") and isinstance(interaction.output, str):
                transcript = interaction.output.strip()

            if not transcript:
                logger.warning("Gemini returned empty transcript for audio.")
                logger.info("transcription_success=False")
                logger.info("VOICE_TEST_END")
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

            logger.info("transcription_success=True")
            logger.info(f"transcript_length={len(transcript)}")
            logger.info(f"transcript='{transcript}'")
            logger.info(f"query_sent='{transcript}'")
            logger.info("VOICE_TEST_END")

            return {
                "transcript": transcript,
                "language_code": canonical_code,
                "language": selected_locale,
                "provider": self.transcribe_model
            }

        except MitraException:
            logger.info("transcription_success=False")
            logger.info("VOICE_TEST_END")
            raise
        except Exception as e:
            error_status = getattr(e, "status_code", getattr(e, "code", None))
            logger.error(
                f"TRANSCRIPTION ERROR: model={self.transcribe_model}, "
                f"mime_type={effective_mime}, "
                f"http_status={error_status}, "
                f"gemini_error_message={str(e)}"
            )
            logger.info("transcription_success=False")
            logger.info("VOICE_TEST_END")
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

