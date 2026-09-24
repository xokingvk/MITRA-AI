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
    "thank you", "thanks", "namaste", "vanakkam", "namaskara", "namaskar",
    "வணக்கம்", "नमस्ते", "నమస్కారం", "ನಮಸ್ಕಾರ", "നമസ്കാരം", "नमस्कार", "নমস্কার", "નમસ્તે"
}

MEDICAL_SAFETY_TERMS = {
    "diagnose", "diagnosis", "prescription", "dosage", "dose", "medicine to take",
    "cure", "treatment for symptoms", "fever treatment", "painkiller", "side effects",
    "what medicine should i take", "remedy for", "how many tablets", "prescribe"
}

# Non-health domain terms that must be marked OUT OF SCOPE immediately
NON_HEALTH_TERMS = {
    # Agriculture & Farming
    "farmer", "farmers", "farming", "agriculture", "crop", "crops", "kisan", "fertilizer",
    "irrigation", "tractor", "harvest", "paddy", "wheat", "soil", "pm-kisan",
    "விவசாய", "விவசாயி", "விவசாயிகள்", "பயிர்", "உழவர்",
    "किसान", "कृषि", "खेती", "फसल", "खाद", "सिंचाई",
    "రైతు", "రైతులు", "వ్యవసాయం", "పంట",
    "ರೈತ", "ಕೃಷಿ", "ಬೆಳೆ",
    "കർഷകൻ", "കൃഷി",
    "शेतकरी", "शेती", "पीक",
    "কৃষক", "কৃষি", "ফসল",
    "ખેડૂત", "ખેતી", "પાક",

    # Education & Scholarships
    "scholarship", "scholarships", "student", "students", "college", "school", "admission",
    "tuition", "exam", "education", "degree", "university", "fee waiver",
    "கல்வி", "மாணவர்", "மாணவர்கள்", "படிப்பு", "உதவித்தொகை",
    "छात्रवृत्ति", "छात्र", "विद्यार्थी", "कॉलेज", "स्कूल", "शिक्षा", "पढ़ाई",
    "స్కాలర్‌షిప్", "విద్యార్థి", "చదువు", "కాలేజ్",
    "ವಿದ್ಯಾರ್ಥಿವೇತನ", "ವಿದ್ಯಾರ್ಥಿ", "ಶಿಕ್ಷಣ",
    "സ്കോളർഷിപ്പ്", "വിദ്യാർത്ഥി",
    "शिष्यवृत्ती", "विद्यार्थी", "शिक्षण",
    "ছাত্রবৃত্তি", "ছাত্র", "শিক্ষা",
    "શિષ્યવૃત્તિ", "વિદ્યાર્થી", "શિક્ષણ",

    # Jobs, Employment & Finance
    "job", "jobs", "employment", "recruitment", "salary", "vacancy", "loan", "loans",
    "business", "credit", "banking", "stocks", "crypto", "investment", "housing loan",
    "வேலை", "வேலைவாய்ப்பு", "கடன்", "தொழில்",
    "नौकरी", "रोजगार", "भर्ती", "कर्ज", "ऋण", "व्यापार", "लोन",
    "ఉద్యోగం", "ఉపాధి", "రుణం", "వ్యాపారం",
    "ಉದ್ಯೋಗ", "ಸಾಲ", "ವ್ಯಾಪಾರ",
    "ജോലി", "വായ്പ",
    "नोकरी", "रोजगार", "कर्ज",
    "চাকরি", "ঋণ", "ব্যবসা",
    "નોકરી", "લોન", "વેપાર",

    # Entertainment, Politics & Misc
    "movie", "movies", "song", "cricket", "sports", "politics", "election", "minister",
    "party", "weather", "forecast", "news", "horoscope"
}

# Health-specific domain terms
HEALTH_SCHEME_TERMS = {
    "health", "healthcare", "hospital", "medicine", "medicines", "treatment", "doctor",
    "maternity", "pregnant", "pregnancy", "mother", "mothers", "baby", "newborn", "child",
    "children", "vaccine", "vaccination", "tb", "cancer", "dialysis", "card",
    "insurance", "ayushman", "pmjay", "pm-jay", "janani", "suraksha", "jssk", "pmmvy",
    "rashtriya", "disability", "disabled", "senior citizen", "senior", "elderly", "70+", "70",
    "cashless", "clinic", "phc", "chc", "medical assistance", "illness", "disease",
    "surgery", "operation", "coverage", "bpl health",
    # Tamil
    "சுகாதாரம்", "மருத்துவம்", "மருத்துவமனை", "கர்ப்ப", "கர்ப்பிணி", "கர்ப்பம்", "தாய்",
    "குழந்தை", "ஆயுஷ்மான்", "சிகிச்சை", "நோய்", "மருந்து", "மகப்பேறு",
    # Hindi
    "स्वास्थ्य", "चिकित्सा", "अस्पताल", "दवा", "दवाएं", "इलाज", "गर्भवती", "मातृत्व",
    "बच्चा", "शिशु", "आयुष्मान", "बीमा", "रोग", "बीमारी", "प्रसव",
    # Telugu
    "ఆరోగ్య", "ఆరోగ్యం", "వైద్య", "ఆసుపత్రి", "మందులు", "చికిత్స", "గర్భిణీ", "గర్భవతి",
    "మాతృత్వ", "ఆయుష్మాన్", "బీమా", "జబ్బు",
    # Kannada
    "ಆರೋಗ್ಯ", "ವೈದ್ಯಕೀಯ", "ಆಸ್ಪತ್ರೆ", "ಔಷಧ", "ಚಿಕಿತ್ಸೆ", "ಗರ್ಭಿಣಿ", "ತಾಯಿ", "ಮಗು", "ಆಯುಷ್ಮಾನ್",
    # Malayalam
    "ആരോഗ്യം", "ചികിത്സ", "ആശുപത്രി", "മരുന്ന്", "ഗർഭിണി", "പ്രസവം", "കുഞ്ഞ്", "ആയുഷ്മാൻ",
    # Marathi
    "आरोग्य", "वैद्यकीय", "रुग्णालय", "औषध", "उपचार", "गरोदर", "बाळंतपण", "आयुष्मान",
    # Bengali
    "স্বাস্থ্য", "চিকিৎসা", "হাসপাতাল", "ওষুধ", "গর্ভবতী", "প্রসব", "শিশু", "আয়ুষ্মান",
    # Gujarati
    "સ્વાસ્થ્ય", "તબીબી", "હોસ્પિટલ", "દવા", "સારવાર", "સગર્ભા", "પ્રસૂતિ", "બાળક", "આયુષ્માન"
}

def normalize_text(text: str) -> str:
    """Normalizes raw input text for intent matching."""
    return re.sub(r"\s+", " ", text.lower().strip())

class ScopeService:
    @staticmethod
    def classify_intent(text: str, has_conversation_context: bool = False) -> str:
        """
        Classifies the intent of user input text.
        Strictly enforces HEALTH-ONLY assistance scope.
        """
        normalized = normalize_text(text)
        
        if not normalized:
            return "empty"
        
        if normalized in GREETING_TERMS:
            return "greeting"
        
        if any(term in normalized for term in MEDICAL_SAFETY_TERMS):
            return "medical_safety"
        
        # Check explicit non-health terms (farming, education, jobs, business, etc.)
        is_non_health = any(term in normalized for term in NON_HEALTH_TERMS)
        is_health = any(term in normalized for term in HEALTH_SCHEME_TERMS)

        if is_non_health and not is_health:
            return "out_of_scope"

        if is_health:
            return "health_scheme"

        if has_conversation_context and len(normalized.split()) <= 6:
            return "follow_up"

        # If query contains explicit health terms in other formats or context
        if any(term in normalized for term in ["health", "hospital", "scheme", "medical", "doctor", "clinic", "ayushman"]):
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
