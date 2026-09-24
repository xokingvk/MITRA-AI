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

def test_multilingual_pipeline():
    print("=== TEST 1: Language Config Resolution ===")
    test_languages = ['en', 'hi', 'ta', 'te', 'kn', 'ml', 'mr', 'bn', 'gu']
    for lang in test_languages:
        info = resolve_language(lang)
        assert info["code"] == lang
        print(f"  OK: {lang} -> {info['locale']} ({info['name']})")

    print("\n=== TEST 2: Health-Only Scope and Out-of-Scope Filtering ===")
    from app.services.scope_service import ScopeService
    from app.services.chat_service import ChatService
    from app.services.gemini_service import GeminiService
    from app.services.conversation_service import ConversationService
    from app.services.document_service import DocumentService
    from app.models.chat_models import ChatRequest

    gemini_service = GeminiService()
    chat_service = ChatService(
        gemini_service=gemini_service,
        conversation_service=ConversationService(),
        document_service=DocumentService()
    )

    # 1. Pregnancy Health Query
    req1 = ChatRequest(message="I am pregnant and I need government health schemes.", language="en")
    res1 = chat_service.process_chat_message(req1)
    print("\n[TEST 1 - Pregnancy Health Query]")
    print(f"  Intent: {res1.intent}")
    print(f"  Answer: {res1.answer.splitlines()[0]}")
    assert res1.intent in ["health_scheme", "follow_up"]

    # 2. Tamil Pregnancy Health Query
    req2 = ChatRequest(message="எனக்கு கர்ப்ப காலத்திற்கான அரசு சுகாதார திட்டங்கள் வேண்டும்", language="ta")
    res2 = chat_service.process_chat_message(req2)
    print("\n[TEST 2 - Tamil Health Query]")
    print(f"  Intent: {res2.intent}")
    print(f"  Answer: {res2.answer.splitlines()[0]}")
    assert res2.intent in ["health_scheme", "follow_up"]

    # 3. Child Health Query
    req3 = ChatRequest(message="I need health support for my child.", language="en")
    res3 = chat_service.process_chat_message(req3)
    print("\n[TEST 3 - Child Health Query]")
    print(f"  Intent: {res3.intent}")
    print(f"  Answer: {res3.answer.splitlines()[0]}")
    assert res3.intent in ["health_scheme", "follow_up"]

    # 4. Farmer Schemes (Non-Health) -> Must be Out of Scope
    req4 = ChatRequest(message="What government schemes are available for farmers?", language="en")
    res4 = chat_service.process_chat_message(req4)
    print("\n[TEST 4 - Farmer Query (Non-Health)]")
    print(f"  Intent: {res4.intent}")
    print(f"  Answer: {res4.answer}")
    assert res4.intent == "out_of_scope"
    assert "health-related" in res4.answer.lower()
    assert len(res4.matched_schemes) == 0

    # 5. Scholarship / College Students (Non-Health) -> Must be Out of Scope
    req5 = ChatRequest(message="What scholarships are available for college students?", language="en")
    res5 = chat_service.process_chat_message(req5)
    print("\n[TEST 5 - Scholarship Query (Non-Health)]")
    print(f"  Intent: {res5.intent}")
    print(f"  Answer: {res5.answer}")
    assert res5.intent == "out_of_scope"
    assert "health-related" in res5.answer.lower()
    assert len(res5.matched_schemes) == 0

    # 6. Tamil Non-Health Query
    req6 = ChatRequest(message="விவசாயிகளுக்கான அரசு திட்டங்கள் என்ன?", language="ta")
    res6 = chat_service.process_chat_message(req6)
    print("\n[TEST 6 - Tamil Farmer Query (Non-Health)]")
    print(f"  Intent: {res6.intent}")
    print(f"  Answer: {res6.answer}")
    assert res6.intent == "out_of_scope"
    assert len(res6.matched_schemes) == 0

    print("\n>>> ALL HEALTH-ONLY AND MULTILINGUAL SCOPE TESTS PASSED! <<<")

if __name__ == "__main__":
    test_multilingual_pipeline()
