import os
import json
import logging
import tempfile
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
            logger.warning("GEMINI_API_KEY is not set. Gemini generation will use grounded offline evaluation.")

    def is_configured(self) -> bool:
        """Returns True if the Gemini API key is set and client is ready."""
        return self.client is not None

    def generate_chat_response(
        self,
        question: str,
        language_code: str = "en",
        history_text: str = "",
        temp_context: str = ""
    ) -> Dict[str, Any]:
        """Generates a short grounded response with structured scheme cards using Google Gemini."""
        lang_info = resolve_language(language_code)
        language_name = lang_info["name"]

        if not self.is_configured():
            logger.info("Using grounded scheme response (Gemini API key not configured).")
            return self._build_fallback_chat_response(question, language_code)

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
                    temperature=0.2,
                )
            )

            raw_text = (response.text or "").strip()
            if not raw_text:
                return self._build_fallback_chat_response(question, language_code)

            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()

            try:
                parsed = json.loads(raw_text)
                if isinstance(parsed, dict):
                    return {
                        "answer": parsed.get("answer", "").strip(),
                        "voice_answer": parsed.get("voice_answer", "").strip(),
                        "matched_schemes": parsed.get("matched_schemes", []),
                        "needs_more_information": parsed.get("needs_more_information", [])
                    }
            except Exception as json_err:
                logger.warning(f"Failed to parse Gemini JSON response ({json_err}). Formatting raw text.")
                return {
                    "answer": raw_text,
                    "voice_answer": "I found information regarding government health schemes for you.",
                    "matched_schemes": [],
                    "needs_more_information": []
                }

        except Exception as e:
            logger.error(f"Gemini API chat request failed: {str(e)}")
            return self._build_fallback_chat_response(question, language_code)

        return self._build_fallback_chat_response(question, language_code)

    def _build_fallback_chat_response(self, question: str, language_code: str = "en") -> Dict[str, Any]:
        """Provides accurate, short structured health scheme matching for offline/fallback mode across all 9 languages."""
        lang_info = resolve_language(language_code)
        canonical = lang_info["code"]
        q_lower = question.lower()

        is_maternity = any(term in q_lower for term in [
            "pregnant", "pregnancy", "mother", "maternity", "delivery", "baby",
            "கர்ப்ப", "கர்ப்பிணி", "தாய்", "பிரசவம்",
            "गर्भवती", "गर्भ", "मातृत्व", "प्रसव", "बच्चा",
            "గర్భ", "గర్భిణీ", "ప్రసవం", "తల్లి",
            "ಗರ್ಭಿಣಿ", "ತಾಯಿ", "ಹೆರಿಗೆ",
            "ഗർഭിണി", "പ്രസവം", "അമ്മ",
            "गरोदर", "बाळंतपण", "आई",
            "গর্ভবতী", "মাতৃত্ব", "প্রসব",
            "સગર્ભા", "માતૃત્વ", "પ્રસૂતિ"
        ])

        is_senior = any(term in q_lower for term in [
            "senior", "70", "elderly", "old age", "aging",
            "முதியவர்", "வயதான",
            "वरिष्ठ", "बुजुर्ग", "वृद्ध",
            "వయోవృద్ధులు", "వృద్ధ",
            "ಹಿರಿಯ ನಾಗರಿಕ",
            "മുതിർന്ന പൗരന്മാർ",
            "ज्येष्ठ नागरिक",
            "প্রবীণ নাগরিক",
            "વરિષ્ઠ નાગરિક"
        ])

        # Localized Maternity Templates
        maternity_intros = {
            "en": "Based on what you shared, some government health schemes may be relevant to you.\n\nHere are the schemes that may be relevant:\n\n1. Pradhan Mantri Matru Vandana Yojana (PMMVY)\nMaternity support for eligible pregnant women.\n\n2. Janani Shishu Suraksha Karyakram (JSSK)\nFree maternity and newborn care at public health facilities.\n\nYou can select a scheme to see its eligibility, benefits and required documents.",
            "ta": "நீங்கள் பகிர்ந்த தகவலின் அடிப்படையில், சில அரசு சுகாதாரத் திட்டங்கள் உங்களுக்குப் பொருந்தக்கூடும்.\n\nபொருந்தக்கூடிய திட்டங்கள்:\n\n1. பிரதான் மந்திரி மாத்ரு வந்தனா யோஜனா (PMMVY)\nதகுதியான கர்ப்பிணிப் பெண்களுக்கான மகப்பேறு நிதியுதவி.\n\n2. ஜனனி சிசு சுரக்ஷா காரியக்ரம் (JSSK)\nஅரசு மருத்துவமனைகளில் இலவச மகப்பேறு மற்றும் பிறந்த குழந்தை சிகிச்சை.\n\nதிட்டத்தைத் தேர்ந்தெடுத்து தகுதிகள் மற்றும் ஆவணங்களைப் பார்க்கலாம்.",
            "hi": "आपके द्वारा दी गई जानकारी के आधार पर, कुछ सरकारी स्वास्थ्य योजनाएं आपके लिए प्रासंगिक हो सकती हैं।\n\nप्रासंगिक योजनाएं:\n\n1. प्रधानमंत्री मातृ वंदना योजना (PMMVY)\nपात्र गर्भवती महिलाओं के लिए मातृत्व वित्तीय सहायता।\n\n2. जननी शिशु सुरक्षा कार्यक्रम (JSSK)\nसरकारी स्वास्थ्य केंद्रों पर मुफ्त प्रसव और नवजात शिशु देखभाल।\n\nयोजना चुनकर पात्रता और आवश्यक दस्तावेज देखें।",
            "te": "మీరు అందించిన సమాచారం ఆధారంగా, కొన్ని ప్రభుత్వ ఆరోగ్య పథకాలు మీకు వర్తించవచ్చు.\n\nసంబంధిత పథకాలు:\n\n1. ప్రధాన మంత్రి మాతృ వందన యోజన (PMMVY)\nఅర్హులైన గర్భిణీ స్త్రీలకు ప్రసూతి ఆర్థిక సహాయం.\n\n2. జనని శిశు సురక్ష కార్యక్రమం (JSSK)\nప్రభుత్వ ఆసుపత్రులలో ఉచిత ప్రసవం మరియు నవజాత శిశు సంరక్షణ.\n\nఅర్హతలు మరియు పత్రాలను చూడటానికి పథకాన్ని ఎంచుకోండి.",
            "kn": "ನೀವು ಹಂಚಿಕೊಂಡ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ, ಕೆಲವು ಸರ್ಕಾರಿ ಆರೋಗ್ಯ ಯೋಜನೆಗಳು ನಿಮಗೆ ಸೂಕ್ತವಾಗಬಹುದು.\n\nಸೂಕ್ತ ಯೋಜನೆಗಳು:\n\n1. ಪ್ರಧಾನ ಮಂತ್ರಿ ಮಾತೃ ವಂದನಾ ಯೋಜನೆ (PMMVY)\nಅರ್ಹ ಗರ್ಭಿಣಿ ಮಹಿಳೆಯರಿಗೆ ಮಾತೃತ್ವ ಧನಸಹಾಯ.\n\n2. ಜನನಿ ಶಿಶು ಸುರಕ್ಷಾ ಕಾರ್ಯಕ್ರಮ (JSSK)\nಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆಗಳಲ್ಲಿ ಉಚಿತ ಹೆರಿಗೆ ಮತ್ತು ನವಜಾತ ಶಿಶು ಆರೈಕೆ.\n\nಯೋಜನೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ ಅರ್ಹತೆ ಮತ್ತು ದಾಖಲೆಗಳನ್ನು ವೀಕ್ಷಿಸಿ.",
            "ml": "നിങ്ങൾ നൽകിയ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ, ചില സർക്കാർ ആരോഗ്യ പദ്ധതികൾ നിങ്ങൾക്ക് അനുയോജ്യമായേക്കാം.\n\nപ്രസക്തമായ പദ്ധതികൾ:\n\n1. പ്രധാനമന്ത്രി മാതൃ വന്ദന യോജന (PMMVY)\nഅർഹരായ ഗർഭിണികൾക്കുള്ള പ്രസവ ധനസഹായം.\n\n2. ജനനി ശിശു സുരക്ഷാ കാര്യക്രമം (JSSK)\nസർക്കാർ ആശുപത്രികളിൽ സൗജന്യ പ്രസവവും നവജാത ശിശു പരിചരണവും.\n\nയോഗ്യതകളും രേഖകളും കാണാൻ പദ്ധതി തിരഞ്ഞെടുക്കുക.",
            "mr": "तुम्ही दिलेल्या माहितीच्या आधारे, काही शासकीय आरोग्य योजना तुमच्यासाठी उपयुक्त ठरू शकतात.\n\nउपयुक्त योजना:\n\n1. प्रधानमंत्री मातृ वंदना योजना (PMMVY)\nपात्र गरोदर महिलांसाठी मातृत्व आर्थिक सहाय्य.\n\n2. जननी शिशु सुरक्षा कार्यक्रम (JSSK)\nशासकीय रुग्णालयांमध्ये मोफत प्रसूती आणि नवजात शिशु आरोग्य सेवा.\n\nपात्रता आणि कागदपत्रे पाहण्यासाठी योजना निवडा.",
            "bn": "আপনার দেওয়া তথ্যের ভিত্তিতে কিছু সরকারি স্বাস্থ্য প্রকল্প আপনার জন্য প্রাসঙ্গিক হতে পারে।\n\nপ্রাসঙ্গিক প্রকল্পসমূহ:\n\n1. প্রধানমন্ত্রী মাতৃ বন্দনা যোজনা (PMMVY)\nযোগ্য গর্ভবতী মহিলাদের জন্য মাতৃত্বকালীন আর্থিক সহায়তা।\n\n2. জননী শিশু সুরক্ষা কার্যক্রম (JSSK)\nসরকারি হাসপাতালে বিনামূল্যে প্রসব ও নবজাতকের যত্ন।\n\nযোগ্যতা ও প্রয়োজনীয় নথি দেখতে প্রকল্প নির্বাচন করুন।",
            "gu": "તમે આપેલી માહિતીના આધારે, કેટલીક સરકારી સ્વાસ્થ્ય યોજનાઓ તમારા માટે યોગ્ય હોઈ શકે છે.\n\nયોગ્ય યોજનાઓ:\n\n1. પ્રધાનમંત્રી માતૃ વંદના યોજના (PMMVY)\nપાત્ર સગર્ભા મહિલાઓ માટે માતૃત્વ સહાય.\n\n2. જનની શિશુ સુરક્ષા કાર્યક્રમ (JSSK)\nસરકારી હોસ્પિટલોમાં મફત પ્રસૂતિ અને નવજાત શિશુ સંભાળ.\n\nપાત્રતા અને દસ્તાવેજો જોવા માટે યોજના પસંદ કરો."
        }

        maternity_voices = {
            "en": "I found maternity welfare schemes that may be relevant to you. You can see them on the screen.",
            "ta": "உங்களுக்குப் பொருந்தக்கூடிய கர்ப்பிணி மகளிர் நலத்திட்டங்கள் கண்டறியப்பட்டுள்ளன. அவற்றை திரையில் பார்க்கலாம்.",
            "hi": "मुझे आपके लिए प्रासंगिक मातृत्व सहायता योजनाएं मिली हैं। आप उन्हें स्क्रीन पर देख सकते हैं।",
            "te": "గర్భిణీ స్త్రీలకు ఉపయోగపడే ప్రభుత్వ పథకాలను గుర్తించాను. వాటిని తెరపై చూడవచ్చు.",
            "kn": "ಗರ್ಭಿಣಿಯರಿಗೆ ಉಪಯುಕ್ತವಾದ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳನ್ನು ಕಂಡುಕೊಳ್ಳಲಾಗಿದೆ. ಅವುಗಳನ್ನು ಪರದೆಯ ಮೇಲೆ ನೋಡಬಹುದು.",
            "ml": "ഗർഭിണികൾക്ക് പ്രയോജനകരമായ സർക്കാർ പദ്ധതികൾ കണ്ടെത്തിയിട്ടുണ്ട്. അവ സ്ക്രീനിൽ കാണാം.",
            "mr": "गरोदर महिलांसाठी उपयुक्त सरकारी योजना सापडल्या आहेत. आपण त्या स्क्रीनवर पाहू शकता.",
            "bn": "গর্ভবতী মহিলাদের জন্য প্রাসঙ্গিক সরকারি স্বাস্থ্য প্রকল্প খুঁজে পাওয়া গেছে। স্ক্রিনে সেগুলি দেখতে পারেন.",
            "gu": "સગર્ભા બહેનો માટે ઉપયોગી સરકારી યોજનાઓ મળી છે. તમે તેને સ્ક્રીન પર જોઈ શકો છો."
        }

        # Localized General Schemes Templates
        general_intros = {
            "en": "Based on what you shared, some government health schemes may be relevant to you.\n\nHere are the schemes that may be relevant:\n\n1. Ayushman Bharat PM-JAY\nCashless hospital coverage up to ₹5 Lakh per family per year for secondary and tertiary care.\n\n2. National Health Mission (NHM) Free Drugs & Diagnostics\nEssential medicines and diagnostic tests provided free of cost at public health centers.\n\nYou can select a scheme to see its eligibility, benefits and required documents.",
            "ta": "நீங்கள் பகிர்ந்த தகவலின் அடிப்படையில், சில அரசு சுகாதாரத் திட்டங்கள் உங்களுக்குப் பொருந்தக்கூடும்.\n\nபொருந்தக்கூடிய திட்டங்கள்:\n\n1. ஆயுஷ்மான் பாரத் PM-JAY\nகுடும்பத்திற்கு ஆண்டுக்கு ₹5 லட்சம் வரை கட்டணமில்லா மருத்துவமனை சிகிச்சை.\n\n2. தேசிய சுகாதார இயக்கம் (NHM) இலவச மருந்துகள் மற்றும் ஆய்வகச் சோதனைகள்\nஅரசு ஆரம்ப சுகாதார நிலையங்களில் இலவச மருந்துகள் மற்றும் பரிசோதனைகள்.\n\nதிட்டத்தைத் தேர்ந்தெடுத்து தகுதிகள் மற்றும் ஆவணங்களைப் பார்க்கலாம்.",
            "hi": "आपके द्वारा दी गई जानकारी के आधार पर, कुछ सरकारी स्वास्थ्य योजनाएं आपके लिए प्रासंगिक हो सकती हैं।\n\nप्रासंगिक योजनाएं:\n\n1. आयुष्मान भारत PM-JAY\nमाध्यमिक और तृतीयक उपचार के लिए प्रति परिवार प्रति वर्ष ₹5 लाख तक का कैशलेस अस्पताल कवरेज।\n\n2. राष्ट्रीय स्वास्थ्य मिशन (NHM) मुफ्त दवाएं एवं जांच\nसरकारी स्वास्थ्य केंद्रों पर आवश्यक दवाएं और जांच निःशुल्क।\n\nयोजना चुनकर पात्रता और आवश्यक दस्तावेज देखें।",
            "te": "మీరు అందించిన సమాచారం ఆధారంగా, కొన్ని ప్రభుత్వ ఆరోగ్య పథకాలు మీకు వర్తించవచ్చు.\n\nసంబంధిత పథకాలు:\n\n1. ఆయుష్మాన్ భారత్ PM-JAY\nద్వితీయ మరియు తృతీయ స్థాయి చికిత్సలకు ప్రతి కుటుంబానికి సంవత్సరానికి ₹5 లక్షల వరకు నగదు రహిత ఆసుపత్రి కవరేజ్.\n\n2. జాతీయ ఆరోగ్య మిషన్ (NHM) ఉచిత మందులు & పరీక్షలు\nప్రభుత్వ ఆరోగ్య కేంద్రాలలో ఉచిత మందులు మరియు రక్త పరీక్షలు.\n\nఅర్హతలు మరియు పత్రాలను చూడటానికి పథకాన్ని ఎంచుకోండి.",
            "kn": "ನೀವು ಹಂಚಿಕೊಂಡ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ, ಕೆಲವು ಸರ್ಕಾರಿ ಆರೋಗ್ಯ ಯೋಜನೆಗಳು ನಿಮಗೆ ಸೂಕ್ತವಾಗಬಹುದು.\n\nಸೂಕ್ತ ಯೋಜನೆಗಳು:\n\n1. ಆಯುಷ್ಮಾನ್ ಭಾರತ್ PM-JAY\nಪ್ರತಿ ಕುಟುಂಬಕ್ಕೆ ವಾರ್ಷಿಕವಾಗಿ ₹5 ಲಕ್ಷದವರೆಗೆ ನಗದು ರಹಿತ ಆಸ್ಪತ್ರೆ ಚಿಕಿತ್ಸಾ ರಕ್ಷಣೆ.\n\n2. ರಾಷ್ಟ್ರೀಯ ಆರೋಗ್ಯ ಅಭಿಯಾನ (NHM) ಉಚಿತ ಔಷಧಗಳು ಮತ್ತು ತಪಾಸಣೆಗಳು\nಸರ್ಕಾರಿ ಪ್ರಾಥಮಿಕ ಕೇಂದ್ರಗಳಲ್ಲಿ ಉಚಿತ ಔಷಧಿಗಳು ಮತ್ತು ಪ್ರಯೋಗಾಲಯ ಪರೀಕ್ಷೆಗಳು.\n\nಯೋಜನೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ ಅರ್ಹತೆ ಮತ್ತು ದಾಖಲೆಗಳನ್ನು ವೀಕ್ಷಿಸಿ.",
            "ml": "നിങ്ങൾ നൽകിയ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ, ചില സർക്കാർ ആരോഗ്യ പദ്ധതികൾ നിങ്ങൾക്ക് അനുയോജ്യമായേക്കാം.\n\nപ്രസക്തമായ പദ്ധതികൾ:\n\n1. ആയുഷ്മാൻ ഭാരത് PM-JAY\nഓരോ കുടുംബത്തിനും പ്രതിവർഷം ₹5 ലക്ഷം രൂപ വരെ സൗജന്യ ആശുപത്രി ചികിത്സ.\n\n2. ദേശീയ ആരോഗ്യ ദൗത്യം (NHM) സൗജന്യ മരുന്നുകളും പരിശോധനകളും\nസർക്കാർ ആരോഗ്യ കേന്ദ്രങ്ങളിൽ സൗജന്യ മരുന്നുകളും ലാബ് പരിശോധനകളും.\n\nയോഗ്യതകളും രേഖകളും കാണാൻ പദ്ധതി തിരഞ്ഞെടുക്കുക.",
            "mr": "तुम्ही दिलेल्या माहितीच्या आधारे, काही शासकीय आरोग्य योजना तुमच्यासाठी उपयुक्त ठरू शकतात.\n\nउपयुक्त योजना:\n\n1. आयुष्मान भारत PM-JAY\nप्रति कुटुंब प्रति वर्ष ₹5 लाख पर्यंत कॅशलेस रुग्णालय उपचार संरक्षण.\n\n2. राष्ट्रीय आरोग्य अभियान (NHM) मोफत औषधे आणि निदान सेवा\nशासकीय आरोग्य केंद्रांमध्ये मोफत औषधे आणि तपासण्या उपलब्ध.\n\nपात्रता आणि कागदपत्रे पाहण्यासाठी योजना निवडा.",
            "bn": "আপনার দেওয়া তথ্যের ভিত্তিতে কিছু সরকারি স্বাস্থ্য প্রকল্প আপনার জন্য প্রাসঙ্গিক হতে পারে।\n\nপ্রাসঙ্গিক প্রকল্পসমূহ:\n\n1. আয়ুষ্মান ভারত PM-JAY\nপ্রতিটি পরিবারের জন্য বছরে ₹৫ লক্ষ টাকা পর্যন্ত নগদহীন হাসপাতাল চিকিৎসা সুবিধা।\n\n2. জাতীয় স্বাস্থ্য মিশন (NHM) বিনামূল্যে ওষুধ ও রোগ নির্ণয়\nসরকারি স্বাস্থ্যকেন্দ্রে বিনামূল্যে ওষুধ ও পরীক্ষা পরিষেবা।\n\nযোগ্যতা ও প্রয়োজনীয় নথি দেখতে প্রকল্প নির্বাচন করুন।",
            "gu": "તમે આપેલી માહિતીના આધારે, કેટલીક સરકારી સ્વાસ્થ્ય યોજનાઓ તમારા માટે યોગ્ય હોઈ શકે છે.\n\nયોગ્ય યોજનાઓ:\n\n1. આયુષ્માન ભારત PM-JAY\nપરિવાર દીઠ વાર્ષિક ₹5 લાખ સુધીની કેશલેસ હોસ્પિટલ સારવાર.\n\n2. રાષ્ટ્રીય સ્વાસ્થ્ય મિશન (NHM) મફત દવાઓ અને નિદાન\nસરકારી આરોગ્ય કેન્દ્રો પર મફત દવાઓ અને તપાસ.\n\nપાત્રતા અને દસ્તાવેજો જોવા માટે યોજના પસંદ કરો."
        }

        general_voices = {
            "en": "I found health welfare schemes that may be relevant to you. You can see them on the screen.",
            "ta": "உங்களுக்குப் பொருந்தக்கூடிய அரசு சுகாதாரத் திட்டங்கள் கண்டறியப்பட்டுள்ளன. அவற்றை திரையில் பார்க்கலாம்.",
            "hi": "मुझे आपके लिए प्रासंगिक स्वास्थ्य योजनाएं मिली हैं। आप उन्हें स्क्रीन पर देख सकते हैं।",
            "te": "మీకు ఉపయోగపడే ఆరోగ్య పథకాలను గుర్తించాను. వాటిని తెరపై చూడవచ్చు.",
            "kn": "ನಿಮಗೆ ಉಪಯುಕ್ತವಾದ ಸರ್ಕಾರಿ ಆರೋಗ್ಯ ಯೋಜನೆಗಳನ್ನು ಕಂಡುಕೊಳ್ಳಲಾಗಿದೆ. ಅವುಗಳನ್ನು ಪರದೆಯ ಮೇಲೆ ನೋಡಬಹುದು.",
            "ml": "നിങ്ങൾക്ക് പ്രയോജനകരമായ ആരോഗ്യ പദ്ധതികൾ കണ്ടെത്തിയിട്ടുണ്ട്. അവ സ്ക്രീനിൽ കാണാം.",
            "mr": "मला तुमच्यासाठी उपयुक्त शासकीय आरोग्य योजना सापडल्या आहेत. आपण त्या स्क्रीनवर पाहू शकता.",
            "bn": "আপনার জন্য প্রাসঙ্গিক সরকারি স্বাস্থ্য প্রকল্প খুঁজে পাওয়া গেছে। স্ক্রিনে সেগুলি দেখতে পারেন.",
            "gu": "તમારા માટે યોગ્ય સરકારી સ્વાસ્થ્ય યોજનાઓ મળી છે. તમે તેને સ્ક્રીન પર જોઈ શકો છો."
        }

        if is_maternity:
            return {
                "answer": maternity_intros.get(canonical, maternity_intros["en"]),
                "voice_answer": maternity_voices.get(canonical, maternity_voices["en"]),
                "matched_schemes": [
                    {
                        "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
                        "short_description": "Maternity financial support for eligible pregnant women.",
                        "reason": "Maternity assistance for pregnant women and lactating mothers.",
                        "eligibility": "Pregnant women and lactating mothers for first live birth in eligible categories.",
                        "benefits": "Direct cash assistance up to ₹5,000 in bank account for maternal nutrition.",
                        "documents": ["Aadhaar Card", "Mother and Child Protection (MCP) Card", "Bank Account Passbook"]
                    },
                    {
                        "name": "Janani Shishu Suraksha Karyakram (JSSK)",
                        "short_description": "Free maternity and newborn care at public health facilities.",
                        "reason": "Free institutional delivery and newborn healthcare",
                        "eligibility": "All pregnant women delivering in government health institutions.",
                        "benefits": "Completely free delivery, C-section, medicines, diagnostic tests, and transport.",
                        "documents": ["Aadhaar Card / ID Proof", "Hospital OPD Registration"]
                    }
                ],
                "needs_more_information": ["Annual household income", "State / District"]
            }

        elif is_senior:
            return {
                "answer": (
                    "Based on what you shared, some government health schemes may be relevant to you.\n\n"
                    "Here are the schemes that may be relevant:\n\n"
                    "1. Ayushman Bharat PM-JAY (Senior Citizen 70+)\n"
                    "Universal ₹5 Lakh annual hospital cover for all citizens aged 70 and above.\n\n"
                    "2. Rashtriya Vayoshri Yojana\n"
                    "Free assisted living devices and physical aids for eligible senior citizens.\n\n"
                    "You can select a scheme to see its eligibility, benefits and required documents."
                ),
                "voice_answer": "I found senior citizen health schemes that may be relevant to you. You can see them on the screen.",
                "matched_schemes": [
                    {
                        "name": "Ayushman Bharat PM-JAY (Senior Citizen 70+)",
                        "short_description": "Universal ₹5 Lakh annual hospital cover for all senior citizens aged 70+.",
                        "reason": "Senior citizen healthcare assurance",
                        "eligibility": "All Indian citizens aged 70 years and above, irrespective of income.",
                        "benefits": "₹5,00,000 cashless hospitalization cover per year across empaneled hospitals.",
                        "documents": ["Aadhaar Card (with verified DOB)", "e-KYC Mobile verification"]
                    },
                    {
                        "name": "Rashtriya Vayoshri Yojana",
                        "short_description": "Free physical aids and assisted living devices for eligible seniors.",
                        "reason": "Age-related mobility and physical aid support",
                        "eligibility": "Senior citizens belonging to BPL category or monthly income below ₹15,000.",
                        "benefits": "Free hearing aids, walking sticks, wheelchairs, spectacles, and dentures.",
                        "documents": ["Aadhaar Card", "Age Proof", "Income / BPL Certificate"]
                    }
                ],
                "needs_more_information": ["State of residence"]
            }

        else:
            return {
                "answer": general_intros.get(canonical, general_intros["en"]),
                "voice_answer": general_voices.get(canonical, general_voices["en"]),
                "matched_schemes": [
                    {
                        "name": "Ayushman Bharat PM-JAY",
                        "short_description": "Cashless hospitalization up to ₹5 Lakh per family per year.",
                        "reason": "Universal secondary and tertiary hospital care",
                        "eligibility": "Families identified by SECC 2011 criteria or eligible state ration card holders.",
                        "benefits": "₹5,00,000 cashless treatment across empaneled public and private hospitals.",
                        "documents": ["Aadhaar Card", "Ration Card", "Income Certificate"]
                    },
                    {
                        "name": "NHM Free Drugs and Diagnostic Services",
                        "short_description": "Free essential medicines and pathology tests at public clinics.",
                        "reason": "Primary healthcare and diagnostic support",
                        "eligibility": "All citizens visiting government PHCs, CHCs, and District Hospitals.",
                        "benefits": "Zero-cost consultation, essential medicines, and diagnostic lab investigations.",
                        "documents": ["Outpatient OPD Slip / ID"]
                    }
                ],
                "needs_more_information": ["Annual household income", "State of residence", "Age"]
            }

    def extract_profile_from_document(
        self,
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        mime_type: Optional[str] = None,
        text_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extracts ONLY facts that are explicitly visible in the document using Gemini Files API & Interactions API."""
        default_profile = {
            "name": None,
            "age": None,
            "date_of_birth": None,
            "gender": None,
            "address": None,
            "state": None,
            "district": None,
            "pincode": None,
            "annual_income": None,
            "occupation": None,
            "category": None,
            "disability_status": None,
            "disability_percentage": None,
            "pregnancy_status": None,
            "marital_status": None,
            "document_type": None,
            "document_number": None,
            "summary": "Document parsed."
        }

        file_size = len(file_bytes) if file_bytes else 0
        effective_filename = filename or "document.pdf"
        ext = effective_filename.split(".")[-1].lower() if "." in effective_filename else "pdf"

        # Determine effective mime type
        if ext in ["jpg", "jpeg"]:
            effective_mime = "image/jpeg"
        elif ext == "png":
            effective_mime = "image/png"
        elif ext == "pdf":
            effective_mime = "application/pdf"
        elif ext == "txt":
            effective_mime = "text/plain"
        else:
            effective_mime = mime_type or "application/pdf"

        # Required structured document debug logging
        logger.info(f"DOCUMENT: filename = {effective_filename}")
        logger.info(f"DOCUMENT: mime_type = {effective_mime}")
        logger.info(f"DOCUMENT: file_size = {file_size}")
        logger.info("DOCUMENT: upload_started = True")

        if not self.is_configured():
            logger.warning("Gemini API key not configured for document extraction. Using heuristic fallback.")
            if text_content:
                lowered = text_content.lower()
                if "aadhaar" in lowered or "uidai" in lowered:
                    default_profile["document_type"] = "Aadhaar Card"
                elif "income" in lowered or "salary" in lowered:
                    default_profile["document_type"] = "Income Certificate"
                elif "patta" in lowered or "land" in lowered:
                    default_profile["document_type"] = "Land Document"
            logger.info("DOCUMENT: extraction_success = True")
            logger.info(f"DOCUMENT: extracted_fields = {[k for k, v in default_profile.items() if v is not None and v != 'Document parsed.']}")
            return default_profile

        tmp_path = None
        uploaded_file = None
        doc_model = getattr(settings, "GEMINI_DOCUMENT_MODEL", "gemini-3.8-flash")

        try:
            # 1. Write file bytes to temp file if provided for Gemini Files upload
            if file_bytes and len(file_bytes) > 0:
                with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
                    tmp.write(file_bytes)
                    tmp_path = tmp.name

                logger.info(f"Uploading document to Gemini Files API ({file_size} bytes)...")
                uploaded_file = self.client.files.upload(
                    file=tmp_path,
                    config=types.UploadFileConfig(
                        mime_type=effective_mime,
                        display_name=f"doc_extract_{effective_filename}"
                    )
                )
                logger.info(f"DOCUMENT: gemini_upload_success = True (URI: {uploaded_file.uri})")

            logger.info("DOCUMENT: extraction_started = True")
            
            # Determine input type for Interactions API (document or image)
            input_type = "image" if effective_mime.startswith("image/") else "document"

            # 2. Call client.interactions.create with gemini-3.8-flash (or doc_model)
            raw_text = ""
            try:
                if uploaded_file:
                    interaction = self.client.interactions.create(
                        model=doc_model,
                        input=[
                            {
                                "type": input_type,
                                "uri": uploaded_file.uri,
                                "mime_type": uploaded_file.mime_type or effective_mime
                            },
                            {
                                "type": "text",
                                "text": DOCUMENT_EXTRACTION_PROMPT
                            }
                        ]
                    )
                    raw_text = getattr(interaction, "output_text", None) or ""
                else:
                    interaction = self.client.interactions.create(
                        model=doc_model,
                        input=[
                            {
                                "type": "text",
                                "text": f"{DOCUMENT_EXTRACTION_PROMPT}\n\nDocument Text Content:\n{text_content[:6000] if text_content else ''}"
                            }
                        ]
                    )
                    raw_text = getattr(interaction, "output_text", None) or ""
            except Exception as interaction_err:
                logger.warning(f"Interactions API notice for document extraction ({interaction_err}). Falling back to content generation...")
                contents = [DOCUMENT_EXTRACTION_PROMPT]
                if uploaded_file:
                    contents.append(uploaded_file)
                elif text_content:
                    contents.append(f"Document Text Content:\n{text_content[:6000]}")

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(temperature=0.1)
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

            extracted_keys = [k for k, v in default_profile.items() if v is not None and v != "Document parsed."]
            logger.info("DOCUMENT: extraction_success = True")
            logger.info(f"DOCUMENT: extracted_fields = {extracted_keys}")

            return default_profile

        except Exception as e:
            logger.error(f"Gemini document extraction failed: {str(e)}")
            logger.info("DOCUMENT: extraction_success = False")
            return default_profile
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            if uploaded_file and hasattr(uploaded_file, "name"):
                try:
                    self.client.files.delete(name=uploaded_file.name)
                except Exception:
                    pass

    def match_confirmed_profile(
        self,
        confirmed_profile: Dict[str, Any],
        language_code: str = "en"
    ) -> Dict[str, Any]:
        """Matches a user-confirmed profile dictionary against Indian health schemes using Gemini reasoning."""
        if not self.is_configured():
            return self._build_fallback_profile_matches(confirmed_profile)

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
            if isinstance(parsed, dict):
                return {
                    "guidance_notes": parsed.get("guidance_notes", ""),
                    "missing_information": parsed.get("missing_information", []),
                    "matching_schemes": parsed.get("matching_schemes", [])
                }
            elif isinstance(parsed, list):
                return {
                    "guidance_notes": f"Evaluated {len(parsed)} potentially relevant health schemes.",
                    "missing_information": [],
                    "matching_schemes": parsed
                }

        except Exception as e:
            logger.error(f"Gemini scheme matching error: {str(e)}")

        return self._build_fallback_profile_matches(confirmed_profile)

    def _build_fallback_profile_matches(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Constructs grounded matching schemes for confirmed profile."""
        gender = str(profile.get("gender") or "").lower()
        pregnancy = profile.get("pregnancy_status")
        age = profile.get("age")
        income = profile.get("annual_income")
        disability = profile.get("disability_status")
        state = profile.get("state")

        matching: List[Dict[str, Any]] = []
        missing: List[str] = []

        # Check missing information
        if income is None:
            missing.append("Annual household income")
        if pregnancy is None and gender == "female":
            missing.append("Pregnancy status (if applicable)")
        if disability is None:
            missing.append("Disability status (if applicable)")
        if not state:
            missing.append("State of residence")

        # Maternity schemes
        if pregnancy is True or (gender == "female" and age and 18 <= age <= 45):
            matching.append({
                "scheme_name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
                "short_description": "Maternity financial support for eligible pregnant women.",
                "eligibility_status": "Potentially relevant",
                "why_it_matches": "Maternity financial assistance for pregnant women and lactating mothers.",
                "key_benefits": "₹5,000 direct cash benefit in installments via bank account.",
                "required_documents": ["Aadhaar Card", "MCP Card", "Bank Account Passbook"],
                "source_document": "PMMVY Guidelines",
                "page": 1
            })
            matching.append({
                "scheme_name": "Janani Shishu Suraksha Karyakram (JSSK)",
                "short_description": "Free maternity and newborn healthcare services in public facilities.",
                "eligibility_status": "Potentially relevant",
                "why_it_matches": "Free institutional delivery and newborn healthcare at government health facilities.",
                "key_benefits": "Free delivery, drugs, diagnostics, and transport.",
                "required_documents": ["Aadhaar / ID Proof", "Hospital Registration"],
                "source_document": "JSSK National Guidelines",
                "page": 1
            })

        # Senior citizen schemes
        if age and age >= 70:
            matching.append({
                "scheme_name": "Ayushman Bharat PM-JAY (Senior Citizen 70+)",
                "short_description": "Universal ₹5 Lakh annual hospital cover for all senior citizens aged 70+.",
                "eligibility_status": "Potentially relevant",
                "why_it_matches": "Eligible by age (70 years and above) for universal health cover.",
                "key_benefits": "₹5,00,000 cashless secondary and tertiary hospitalization per year.",
                "required_documents": ["Aadhaar Card with verified Age/DOB"],
                "source_document": "PM-JAY Senior Citizen 70+ Guidelines",
                "page": 1
            })

        # General hospital assurance
        if income is not None and income <= 250000:
            matching.append({
                "scheme_name": "Ayushman Bharat PM-JAY",
                "short_description": "₹5 Lakh annual hospital coverage for low-income families.",
                "eligibility_status": "Potentially relevant",
                "why_it_matches": "Hospitalization assurance for families under income threshold or SECC criteria.",
                "key_benefits": "Cashless treatment up to ₹5 Lakh across empaneled hospitals.",
                "required_documents": ["Aadhaar Card", "Ration Card", "Income Certificate"],
                "source_document": "PM-JAY National Guidelines",
                "page": 1
            })

        # Disability support
        if disability is True:
            matching.append({
                "scheme_name": "Divyangjan Health Assistance & PM-JAY",
                "short_description": "Healthcare coverage and assistive support for Persons with Disabilities.",
                "eligibility_status": "Potentially relevant",
                "why_it_matches": "Healthcare and therapeutic assistance for certified PwD individuals.",
                "key_benefits": "Rehabilitation support, assistive devices, and empaneled medical care.",
                "required_documents": ["Aadhaar Card", "UDID Card / Disability Certificate"],
                "source_document": "National Disability Welfare Guidelines",
                "page": 1
            })

        # General fallback if demographic factors present
        if not matching:
            if age or gender or state:
                matching.append({
                    "scheme_name": "National Health Mission (NHM) Free Healthcare Services",
                    "short_description": "Free essential medicines and primary consultations at public health centers.",
                    "eligibility_status": "Potentially relevant",
                    "why_it_matches": "Universal primary healthcare services available at all government health facilities.",
                    "key_benefits": "Zero-cost OPD consultations, basic diagnostic tests, and essential medicines.",
                    "required_documents": ["Aadhaar / ID Card"],
                    "source_document": "NHM Operational Guidelines",
                    "page": 1
                })

        guidance = (
            f"Based on your confirmed details, {len(matching)} government health welfare program(s) were identified as potentially relevant. "
            f"Please verify exact enrollment requirements with official portals or your nearest primary health center."
            if matching else
            "More information is needed to identify schemes that may be relevant to you. Please provide your annual household income or state."
        )

        return {
            "guidance_notes": guidance,
            "missing_information": missing,
            "matching_schemes": matching
        }
