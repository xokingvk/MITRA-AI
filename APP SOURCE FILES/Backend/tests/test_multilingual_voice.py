import sys
import asyncio
from app.core.language_config import resolve_language, SUPPORTED_LANGUAGES
from app.services.gemini_service import GeminiService
from app.services.voice_service import VoiceService

sys.stdout.reconfigure(encoding='utf-8')

def test_multilingual_pipeline():
    print("=== TEST 1: Language Config Resolution ===")
    test_languages = ['en', 'hi', 'ta', 'te', 'kn', 'ml', 'mr', 'bn', 'gu']
    for lang in test_languages:
        info = resolve_language(lang)
        assert info["code"] == lang
        print(f"  OK: {lang} -> {info['locale']} ({info['name']})")

    print("\n=== TEST 2: Diverse Topic Query Routing (Farmer / Student / Senior / Maternity) ===")
    gemini = GeminiService()
    test_queries = [
        ("en", "I need schemes for farmers", "Farmer Query", ["kisan", "farmer", "agriculture", "ayushman", "health"]),
        ("en", "What help is available for students?", "Student Query", ["health", "mission", "ayushman", "student"]),
        ("en", "I am pregnant.", "Maternity Query", ["matru", "vandana", "jssk", "maternity", "pregnant"]),
        ("ta", "எனக்கு விவசாயிகளுக்கான அரசு திட்டங்கள் வேண்டும்", "Tamil Farmer Query", ["திட்டங்கள்", "ஆரோக்கிய"]),
        ("hi", "किसानों के लिए कौन सी योजनाएं हैं?", "Hindi Farmer Query", ["योजनाएं", "स्वास्थ्य"]),
        ("te", "నేను గర్భవతిని.", "Telugu Maternity Query", ["పథకాలు", "ఆరోగ్య"]),
    ]

    for lang_code, query, desc, expected_keywords in test_queries:
        res = gemini._build_fallback_chat_response(query, language_code=lang_code)
        intro_line = res["answer"].splitlines()[0]
        voice_line = res["voice_answer"]
        print(f"\n  [{desc} ({lang_code})]")
        print(f"    Query: '{query}'")
        print(f"    Intro: '{intro_line}'")
        print(f"    Voice: '{voice_line}'")
        assert len(intro_line) > 0
        assert len(voice_line) > 0
        # Verify student or farmer query does NOT mention pregnancy in intro
        if "farmer" in query.lower() or "student" in query.lower():
            assert "pregnant" not in intro_line.lower()
            assert "maternity" not in intro_line.lower()

    print("\n>>> ALL MULTILINGUAL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_multilingual_pipeline()
