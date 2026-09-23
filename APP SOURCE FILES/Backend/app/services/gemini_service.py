import logging
from typing import Optional
from google import genai
from app.config import settings
from app.core.prompts import SYSTEM_INSTRUCTION, USER_RAG_PROMPT_TEMPLATE
from app.core.language_config import resolve_language
from app.core.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        
        self.client = None
        if self.api_key and self.api_key.strip():
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Gemini client initialized with model {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY is not set. Gemini generation calls will fail until configured.")

    def is_configured(self) -> bool:
        """Returns True if the Gemini API key is set and client is ready."""
        return self.client is not None

    def generate_rag_response(
        self,
        question: str,
        language_code: str,
        context: str,
        history_text: str = "",
        temp_context: str = ""
    ) -> str:
        """Generates a grounded RAG answer using Google Gemini."""
        if not self.is_configured():
            raise GeminiAPIError("GEMINI_API_KEY is not configured in backend environment variables.")

        lang_info = resolve_language(language_code)
        language_name = lang_info["name"]

        prompt = USER_RAG_PROMPT_TEMPLATE.format(
            language_name=language_name,
            language_code=lang_info["code"],
            context=context or "[No official context available]",
            temp_context=temp_context or "[No temporary personal documents attached]",
            history=history_text or "[No previous conversation turns]",
            question=question
        )

        try:
            logger.info(f"Sending RAG prompt to Gemini model '{self.model_name}' (Language: {language_name})...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"system_instruction": SYSTEM_INSTRUCTION}
            )
            
            text_response = (response.text or "").strip()
            if not text_response:
                return f"I apologize, but I could not generate a response. Please verify the official health scheme documentation or rephrase your question."
            
            return text_response

        except Exception as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise GeminiAPIError(f"Gemini generation error: {str(e)}")
