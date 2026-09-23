import re
from typing import Tuple, Optional
from app.core.language_config import (
    resolve_language,
    GREETING_MESSAGES,
    SAFETY_MESSAGES,
    OUT_OF_SCOPE_MESSAGES
)

GREETING_TERMS = {
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "thank you", "thanks", "namaste", "vanakkam", "namaskara", "namaskar"
}

MEDICAL_SAFETY_TERMS = {
    "diagnose", "diagnosis", "prescription", "dosage", "dose", "medicine to take",
    "cure", "treatment for symptoms", "fever treatment", "painkiller", "side effects",
    "what medicine should i take", "remedy for"
}

HEALTH_SCHEME_TERMS = {
    "health", "scheme", "schemes", "hospital", "medicine", "maternity", "pregnant",
    "pregnancy", "vaccination", "tb", "cancer", "mental health", "disability",
    "insurance", "treatment", "healthcare", "eligibility", "government hospital",
    "card", "ayushman", "pmjay", "janani", "suraksha", "bima", "income limit",
    "free treatment", "coverage", "senior citizen", "child healthcare"
}

def normalize_text(text: str) -> str:
    """Normalizes raw input text for intent matching."""
    return re.sub(r"\s+", " ", text.lower().strip())

class ScopeService:
    @staticmethod
    def classify_intent(text: str, has_conversation_context: bool = False) -> str:
        """Classifies the intent of user input text."""
        normalized = normalize_text(text)
        
        if not normalized:
            return "empty"
        
        if normalized in GREETING_TERMS:
            return "greeting"
        
        if any(term in normalized for term in MEDICAL_SAFETY_TERMS):
            return "medical_safety"
        
        if has_conversation_context and len(normalized.split()) <= 8 and not any(term in normalized for term in MEDICAL_SAFETY_TERMS):
            return "follow_up"
        
        if any(term in normalized for term in HEALTH_SCHEME_TERMS):
            return "health_scheme"
        
        # General check: if words contain scheme/health questions in non-English script or context
        if len(normalized.split()) > 2:
            return "health_scheme"
            
        return "out_of_scope"

    @staticmethod
    def get_static_response(intent: str, lang_code: str) -> Optional[str]:
        """Returns localized static message for non-RAG intents (greetings, safety, out of scope)."""
        lang_info = resolve_language(lang_code)
        code = lang_info["code"]

        if intent == "greeting":
            return GREETING_MESSAGES.get(code, GREETING_MESSAGES["en"])
        elif intent == "medical_safety":
            return SAFETY_MESSAGES.get(code, SAFETY_MESSAGES["en"])
        elif intent == "out_of_scope":
            return OUT_OF_SCOPE_MESSAGES.get(code, OUT_OF_SCOPE_MESSAGES["en"])
        return None
