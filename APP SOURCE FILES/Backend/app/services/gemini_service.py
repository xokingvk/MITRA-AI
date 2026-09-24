import json
import logging
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types

from app.config import settings
from app.core.prompts import (
    SYSTEM_INSTRUCTION,
    GEMINI_CHAT_PROMPT_TEMPLATE,
    DOCUMENT_EXTRACTION_PROMPT,
    SCHEME_MATCHING_PROMPT
)
from app.core.language_config import resolve_language, DISCLAIMERS
from app.core.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.client = None

        if self.api_key and self.api_key.strip():
            try:
                self.client = genai.Client(api_key=self.api_key.strip())
                logger.info(f"Gemini client initialized with model '{self.model_name}'")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY is not set. Gemini generation calls will fail until configured.")

    def is_configured(self) -> bool:
        """Returns True if the Gemini API key is set and client is ready."""
        return self.client is not None

    def generate_chat_response(
        self,
        question: str,
        language_code: str = "en",
        history_text: str = "",
        temp_context: str = ""
    ) -> str:
        """Generates a comprehensive grounded response using Google Gemini."""
        if not self.is_configured():
            raise GeminiAPIError("GEMINI_API_KEY is not configured in backend environment variables.")

        lang_info = resolve_language(language_code)
        language_name = lang_info["name"]

        prompt = GEMINI_CHAT_PROMPT_TEMPLATE.format(
            language_name=language_name,
            language_code=lang_info["code"],
            temp_context=temp_context or "[No temporary documents uploaded in this session]",
            history=history_text or "[No previous conversation turns]",
            question=question
        )

        try:
            logger.info(f"Sending chat prompt to Gemini model '{self.model_name}' (Language: {language_name})...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3,
                )
            )

            text_response = (response.text or "").strip()
            if not text_response:
                return f"I apologize, but I could not generate a response. Please rephrase your question regarding health schemes or requirements."

            return text_response

        except Exception as e:
            logger.error(f"Gemini API chat request failed: {str(e)}")
            raise GeminiAPIError(f"Gemini generation error: {str(e)}")

    def extract_profile_from_document(
        self,
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extracts structured profile fields from a document text or image using Gemini vision/text parsing."""
        default_profile = {
            "name": None,
            "age": None,
            "date_of_birth": None,
            "gender": None,
            "address": None,
            "state": None,
            "district": None,
            "annual_income": None,
            "occupation": None,
            "disability_status": None,
            "disability_percentage": None,
            "pregnancy_status": None,
            "marital_status": None,
            "family_info": None,
            "document_type": None,
            "document_number": None,
            "summary": "Document parsed."
        }

        if not self.is_configured():
            logger.warning("Gemini API key not configured for document extraction. Using basic heuristic parsing.")
            if text_content:
                lowered = text_content.lower()
                if "patta" in lowered or "land" in lowered:
                    default_profile["document_type"] = "Land Ownership Document"
                elif "income" in lowered or "salary" in lowered:
                    default_profile["document_type"] = "Income Certificate"
                elif "aadhaar" in lowered or "uidai" in lowered:
                    default_profile["document_type"] = "Aadhaar Card"
            return default_profile

        try:
            contents = [DOCUMENT_EXTRACTION_PROMPT]

            # If image bytes provided, use Gemini multimodal vision
            if file_bytes and mime_type and ("image" in mime_type or filename.lower().endswith((".jpg", ".jpeg", ".png"))):
                effective_mime = mime_type if "image" in mime_type else "image/jpeg"
                contents.append(types.Part.from_bytes(data=file_bytes, mime_type=effective_mime))
            elif text_content:
                contents.append(f"Document Text Content:\n{text_content[:6000]}")
            elif file_bytes:
                # Try decoding as text
                contents.append(f"Document Raw Text:\n{file_bytes.decode('utf-8', errors='ignore')[:6000]}")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction="You are an accurate OCR and data extraction system. Return only valid JSON.",
                    temperature=0.1
                )
            )

            raw_text = (response.text or "").strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                for k in default_profile:
                    if k in parsed:
                        default_profile[k] = parsed[k]
                return default_profile

        except Exception as e:
            logger.warning(f"Gemini document extraction notice ({str(e)}). Returning default empty profile.")

        return default_profile

    def match_confirmed_profile(
        self,
        confirmed_profile: Dict[str, Any],
        language_code: str = "en"
    ) -> List[Dict[str, Any]]:
        """Matches a user-confirmed profile dictionary against Indian health schemes using Gemini reasoning."""
        if not self.is_configured():
            # Fallback schemes list if Gemini key is missing
            return [
                {
                    "scheme_name": "Ayushman Bharat PM-JAY",
                    "eligibility_status": "Potentially eligible",
                    "why_it_matches": "Universal ₹5 Lakh hospital coverage for eligible families / senior citizens.",
                    "key_benefits": "Up to ₹5,00,000 cashless secondary and tertiary hospitalization per family/individual.",
                    "required_documents": ["Aadhaar Card", "Ration Card", "Income Certificate"],
                    "source_document": "PM-JAY Official Guidelines",
                    "page": 1
                }
            ]

        try:
            prompt = SCHEME_MATCHING_PROMPT.format(
                user_profile_json=json.dumps(confirmed_profile, indent=2)
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.2
                )
            )

            raw_text = (response.text or "").strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            parsed = json.loads(raw_text)
            if isinstance(parsed, list):
                return parsed

        except Exception as e:
            logger.error(f"Gemini scheme matching error: {str(e)}")

        return []
