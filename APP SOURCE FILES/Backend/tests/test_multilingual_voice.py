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

    print("\n=== TEST 2: Grounded Fallback Multilingual Chat ===")
    gemini = GeminiService()
    test_cases = [
        ("en", "I am pregnant.", "English"),
        ("ta", "நான் கர்ப்பமாக இருக்கிறேன்.", "Tamil"),
        ("hi", "मैं गर्भवती हूँ।", "Hindi"),
        ("te", "నేను గర్భవతిని.", "Telugu"),
        ("kn", "ನಾನು ಗರ್ಭಿಣಿ.", "Kannada"),
        ("ml", "ഞാൻ ഗർഭിണിയാണ്.", "Malayalam"),
        ("mr", "मी गरोदर आहे.", "Marathi"),
        ("bn", "আমি গর্ভবতী।", "Bengali"),
        ("gu", "હું સગર્ભા છું.", "Gujarati"),
    ]

    for lang_code, query, lang_name in test_cases:
        res = gemini._build_fallback_chat_response(query, language_code=lang_code)
        intro_line = res["answer"].splitlines()[0]
        voice_line = res["voice_answer"]
        print(f"\n  [{lang_name} - {lang_code}]")
        print(f"    Query: {query}")
        print(f"    Intro: {intro_line}")
        print(f"    Voice: {voice_line}")
        assert len(intro_line) > 0
        assert len(voice_line) > 0

    print("\n=== TEST 3: Voice STT & TTS Pipeline ===")
    vs = VoiceService()

    async def run_voice():
        for lang_code, query, lang_name in test_cases:
            stt = await vs.transcribe_audio(b"sample_audio_data", "rec.webm", "audio/webm", language_code=f"{lang_code}-IN")
            print(f"  STT [{lang_name}]: {stt['transcript']} (code: {stt['language_code']})")
            assert len(stt["transcript"]) > 0

            tts = await vs.synthesize_speech("Hello", target_language_code=f"{lang_code}-IN")
            print(f"  TTS [{lang_name}]: format={tts['format']}, message={tts['message']}")

    asyncio.run(run_voice())
    print("\n>>> ALL MULTILINGUAL TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_multilingual_pipeline()
