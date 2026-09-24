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

def test_voice_service_gemini_transcribe():
    print("\n=== TEST 3: Voice Service Gemini 3.5 Transcribe Flow ===")
    from unittest.mock import MagicMock, patch
    from app.services.voice_service import VoiceService

    voice_service = VoiceService()
    voice_service.gemini_api_key = "test-api-key"

    mock_client = MagicMock()
    mock_file = MagicMock()
    mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/test1234"
    mock_file.name = "files/test1234"
    mock_client.files.upload.return_value = mock_file

    mock_interaction = MagicMock()
    mock_interaction.output_text = "I am pregnant and need government health schemes"
    mock_client.interactions.create.return_value = mock_interaction

    with patch.object(voice_service, "_get_gemini_client", return_value=mock_client):
        res = asyncio.run(voice_service.transcribe_audio(
            audio_bytes=b"fake-webm-audio-bytes-header-data",
            filename="recording.webm",
            mime_type="audio/webm",
            language_code="ta-IN"
        ))

        assert res["transcript"] == "I am pregnant and need government health schemes"
        assert res["language"] == "ta-IN"
        assert res["provider"] == "gemini-3.5-transcribe"

        # Verify client.files.upload was called
        mock_client.files.upload.assert_called_once()
        # Verify client.interactions.create was called with gemini-3.5-transcribe and verbatim mode
        mock_client.interactions.create.assert_called_once()
        call_kwargs = mock_client.interactions.create.call_args.kwargs
        assert call_kwargs["model"] == "gemini-3.5-transcribe"
        assert call_kwargs["input"][0]["type"] == "audio"
        assert call_kwargs["input"][0]["uri"] == mock_file.uri
        assert call_kwargs["generation_config"]["transcription_config"]["mode"]["type"] == "verbatim"
        assert call_kwargs["generation_config"]["transcription_config"]["language_codes"] == ["ta-IN"]
        print("  OK: Gemini 3.5 Transcribe interactions call verified successfully!")

def test_document_extraction_gemini_interactions():
    print("\n=== TEST 4: Document Extraction Gemini Interactions Flow ===")
    from unittest.mock import MagicMock, patch
    from app.services.gemini_service import GeminiService

    gemini_service = GeminiService(api_key="test-api-key")

    mock_client = MagicMock()
    mock_file = MagicMock()
    mock_file.uri = "https://generativelanguage.googleapis.com/v1beta/files/doc1234"
    mock_file.name = "files/doc1234"
    mock_client.files.upload.return_value = mock_file

    mock_interaction = MagicMock()
    mock_interaction.output_text = '{"name": "Ananya Sharma", "age": 28, "gender": "Female", "state": "Tamil Nadu", "district": "Chennai", "pincode": "600001", "address": "12 Gandhi St", "annual_income": null, "pregnancy_status": null}'
    mock_client.interactions.create.return_value = mock_interaction

    gemini_service.client = mock_client

    extracted = gemini_service.extract_profile_from_document(
        file_bytes=b"fake-pdf-content",
        filename="aadhaar_card.pdf",
        mime_type="application/pdf"
    )

    assert extracted["name"] == "Ananya Sharma"
    assert extracted["age"] == 28
    assert extracted["gender"] == "Female"
    assert extracted["state"] == "Tamil Nadu"
    assert extracted["district"] == "Chennai"
    assert extracted["annual_income"] is None
    assert extracted["pregnancy_status"] is None

    mock_client.files.upload.assert_called_once()
    mock_client.interactions.create.assert_called_once()
    print("  OK: Document extraction verified successfully with null preservation!")

if __name__ == "__main__":
    test_multilingual_pipeline()
    test_voice_service_gemini_transcribe()
    test_document_extraction_gemini_interactions()
