from typing import Dict, Any

# Supported language codes & names
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"code": "en", "locale": "en-IN", "name": "English", "native_name": "English"},
    "hi": {"code": "hi", "locale": "hi-IN", "name": "Hindi", "native_name": "हिंदी"},
    "ta": {"code": "ta", "locale": "ta-IN", "name": "Tamil", "native_name": "தமிழ்"},
    "te": {"code": "te", "locale": "te-IN", "name": "Telugu", "native_name": "తెలుగు"},
    "kn": {"code": "kn", "locale": "kn-IN", "name": "Kannada", "native_name": "ಕನ್ನಡ"},
    "ml": {"code": "ml", "locale": "ml-IN", "name": "Malayalam", "native_name": "മലയാളം"},
    "mr": {"code": "mr", "locale": "mr-IN", "name": "Marathi", "native_name": "मराठी"},
    "bn": {"code": "bn", "locale": "bn-IN", "name": "Bengali", "native_name": "বাংলা"},
    "gu": {"code": "gu", "locale": "gu-IN", "name": "Gujarati", "native_name": "ગુજરાતી"},
}

# Alias mapping for backward compatibility and various client inputs
LANGUAGE_ALIASES: Dict[str, str] = {
    "en": "en", "en-in": "en", "english": "en",
    "hi": "hi", "hi-in": "hi", "hindi": "hi",
    "ta": "ta", "ta-in": "ta", "tamil": "ta",
    "te": "te", "te-in": "te", "telugu": "te",
    "kn": "kn", "kn-in": "kn", "kannada": "kn",
    "ml": "ml", "ml-in": "ml", "malayalam": "ml",
    "mr": "mr", "mr-in": "mr", "marathi": "mr",
    "bn": "bn", "bn-in": "bn", "bengali": "bn",
    "gu": "gu", "gu-in": "gu", "gujarati": "gu",
}

def resolve_language(lang_input: str) -> Dict[str, str]:
    """Resolves an input language string to a supported language configuration."""
    if not lang_input:
        return SUPPORTED_LANGUAGES["en"]
    
    clean_input = str(lang_input).strip().lower()
    canonical_code = LANGUAGE_ALIASES.get(clean_input, "en")
    return SUPPORTED_LANGUAGES.get(canonical_code, SUPPORTED_LANGUAGES["en"])

# Intent messages localized
GREETING_MESSAGES: Dict[str, str] = {
    "en": "Hello! I am MITRA AI, your healthcare scheme assistant. How can I help you today?",
    "hi": "नमस्ते! मैं मित्रा एआई हूं, आपका स्वास्थ्य योजना सहायक। आज मैं आपकी क्या सहायता कर सकता हूं?",
    "ta": "வணக்கம்! நான் மித்ரா AI, உங்கள் அரசு சுகாதாரத் திட்ட உதவியாளன். உங்களுக்கு எவ்வாறு உதவலாம்?",
    "te": "నమస్కారం! నేను మిత్రా AI, మీ ఆరోగ్య పథకం సహాయకుడిని. నేడు నేను మీకు ఎలా సహాయపడగలను?",
    "kn": "ನಮಸ್ಕಾರ! ನಾನು ಮಿತ್ರ AI, ನಿಮ್ಮ ಸರ್ಕಾರಿ ಆರೋಗ್ಯ ಯೋಜನೆಗಳ ಸಹಾಯಕ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    "ml": "നമസ്കാരം! ഞാൻ മിത്ര AI ആണ്, നിങ്ങളുടെ ആരോഗ്യ പദ്ധതി സഹായി. ഇന്ന് ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കണം?",
    "mr": "नमस्कार! मी मित्रा AI आहे. शासकीय आरोग्य योजनेबद्दल मी तुम्हाला कशी मदत करू शकतो?",
    "bn": "নমস্কার! আমি মিত্র AI, আপনার সরকারি স্বাস্থ্য প্রকল্প সহকারী। কীভাবে আপনাকে সাহায্য করতে পারি?",
    "gu": "નમસ્તે! હું મિત્રા AI છું, તમારો સરકારી સ્વાસ્થ્ય યોજના સહાયક. આજે હું તમને કેવી રીતે મદદ કરી શકું?",
}

SAFETY_MESSAGES: Dict[str, str] = {
    "en": "I cannot diagnose medical conditions, prescribe medicines, or provide dosages. For medical emergencies or treatment, please consult a qualified doctor or visit a hospital. I am here to assist with government health schemes.",
    "hi": "मैं बीमारियों का निदान, दवाइयां या खुराक नहीं दे सकता। चिकित्सा आपात स्थिति में कृपया डॉक्टर या अस्पताल से संपर्क करें। मैं सरकारी स्वास्थ्य योजनाओं में सहायता के लिए हूँ।",
    "ta": "நான் நோய்களைக் கண்டறியவோ, மருந்துகளைப் பரிந்துரைக்கவோ முடியாது. அவசர மருத்துவ சிகிச்சை பெற மருத்துவரை அணுகவும். அரசு சுகாதாரத் திட்டங்கள் குறித்த தகவல்களை மட்டுமே வழங்க முடியும்.",
    "te": "నేను వైద్య పరిస్థితులను నిర్ధారించలేను లేదా మందులను సూచించలేను. అత్యవసర వైద్య సాయం కోసం దయచేసి వైద్యుడిని సంప్రదించండి.",
    "kn": "ನಾನು ವೈದ್ಯಕೀಯ ಸ್ಥಿತಿಯನ್ನು নির্ণಯಿಸಲು അല്ലെങ്കിൽ ಔಷಧ ನೀಡಲು ಸಾಧ್ಯವಿಲ್ಲ. ಸರ್ಕಾರಿ ಆರೋಗ್ಯ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಸಹಾಯ ಮಾಡಲು ಇಲ್ಲಿದ್ದೇನೆ.",
    "ml": "എനിക്ക് രോഗനിർണ്ണയം നടത്താനോ മരുന്നുകൾ നിർദ്ദേശിക്കാനോ കഴിയില്ല. സർക്കാർ ആരോഗ്യ പദ്ധതികളെക്കുറിച്ചുള്ള വിവരങ്ങൾ നൽകാൻ എനിക്ക് സാധിക്കും.",
    "mr": "मी कोणत्याही आजाराचे निदान करू शकत नाही किंवा औषध लिहून देऊ शकत नाही. सरकारी आरोग्य योजनांसाठी मी मदत करू शकतो.",
    "bn": "আমি কোনো রোগের চিকিৎসা বা ওষুধ প্রেসক্রাইব করতে পারি না। আমি শুধুমাত্র সরকারি স্বাস্থ্য প্রকল্পের তথ্য দিতে সাহায্য করতে পারি।",
    "gu": "હું તબીબી પરિસ્થિતિઓનું નિદાન કે દવાઓ લખી આપતો નથી. હું સરકારી સ્વાસ્થ્ય યોજનાઓની માહિતી આપી શકું છું.",
}

OUT_OF_SCOPE_MESSAGES: Dict[str, str] = {
    "en": "I can only assist with government health schemes, healthcare benefits, eligibility criteria, and required documents. Please ask a question related to health schemes.",
    "hi": "मैं केवल सरकारी स्वास्थ्य योजनाओं, पात्रता, लाभों और आवश्यक दस्तावेजों के बारे में प्रश्नों में सहायता कर सकता हूँ।",
    "ta": "நான் அரசு சுகாதாரத் திட்டங்கள், தகுதிகள், நன்மைகள் மற்றும் தேவையான ஆவணங்கள் குறித்த கேள்விகளுக்கு மட்டுமே உதவ முடியும்.",
    "te": "నేను ప్రభుత్వ ఆరోగ్య పథకాలు, అర్హతలు మరియు అవసరమైన పత్రాల గురించి మాత్రమే సమాచారం అందించగలను.",
    "kn": "ನಾನು ಸರ್ಕಾರಿ ಆರೋಗ್ಯ ಯೋಜನೆಗಳು, ಅರ್ಹತೆಗಳು ಮತ್ತು ಅಗತ್ಯ ದಾಖಲೆಗಳ ಕುರಿತು మాత్రమే ಸಹಾಯ ಮಾಡಬಹುದು.",
    "ml": "സർക്കാർ ആരോഗ്യ പദ്ധതികൾ, യോഗ്യതകൾ, ആനുകൂല്യങ്ങൾ എന്നിവയെക്കുറിച്ച് മാത്രമേ എനിക്ക് വിവരം നൽകാനാകൂ.",
    "mr": "मी फक्त शासकीय आरोग्य योजना, पात्रता आणि आवश्यक कागदपत्रांबद्दल मदत करू शकतो.",
    "bn": "আমি শুধুমাত্র সরকারি স্বাস্থ্য প্রকল্প, যোগ্যতা এবং প্রয়োজনীয় নথিপত্র সম্পর্কিত প্রশ্নের উত্তর দিতে পারি।",
    "gu": "હું ફક્ત સરકારી સ્વાસ્થ્ય યોજનાઓ, પાત્રતા અને જરૂરી દસ્તાવેજો અંગે મદદ કરી શકું છું.",
}

DISCLAIMERS: Dict[str, str] = {
    "en": "Disclaimer: Information provided is derived from available official health scheme documentation for guidance only. Official approval and final eligibility must be verified with government scheme authorities.",
    "hi": "अस्वीकरण: प्रदान की गई जानकारी केवल मार्गदर्शन के लिए है। अंतिम पात्रता आधिकारिक सरकारी अधिकारियों द्वारा सत्यापित की जानी चाहिए।",
    "ta": "பொறுப்புத் துறப்பு: இந்தத் தகவல் அரசுத் திட்ட வழிகாட்டுதலுக்காக மட்டுமே. அதிகாரப்பூர்வத் தகுதியை அரசுத் துறை மூலம் உறுதிசெய்யவும்.",
    "te": "గమనిక: సమాచారం కేవలం మార్గదర్శకత్వం కోసం మాత్రమే. అంతిమ అర్హతను ప్రభుత్వ అధికారుల వద్ద దృవీకరించుకోవాలి.",
    "kn": "ಹಕ್ಕುತ್ಯಾಗ: ನೀಡಲಾದ ಮಾಹಿತಿಯು ಮಾರ್ಗದರ್ಶನಕ್ಕಾಗಿ ಮಾತ್ರ. ಅಧಿಕೃತ ಅರ್ಹತೆಯನ್ನು ಸರ್ಕಾರಿ ಪ್ರಾಧಿಕಾರದಿಂದ ದೃಢಪಡಿಸಿಕೊಳ್ಳಬೇಕು.",
    "ml": "നിരാകരണം: നൽകിയിട്ടുള്ള വിവരങ്ങൾ മാർഗ്ഗനിർദ്ദേശത്തിന് മാത്രമുള്ളതാണ്. ഔദ്യോഗിക യോഗ്യത സർക്കാർ അധികാരികളിൽ നിന്ന് ഉറപ്പുവരുത്തുക.",
    "mr": "अस्वीकरण: ही माहिती केवळ मार्गदर्शनासाठी आहे. अंतिम पात्रता शासकीय अधिकाऱ्यांकडून तपासून घ्यावी.",
    "bn": "দাবি পরিত্যাগ: এই তথ্য শুধুমাত্র নির্দেশনার জন্য। চূড়ান্ত যোগ্যতা সরকারি কর্তৃপক্ষের মাধ্যমে যাচাই করতে হবে।",
    "gu": "ડિસ્ક્લેમર: પૂરી પાડવામાં આવેલ માહિતી માત્ર માર્ગદર્શન માટે છે. આખરી પાત્રતા સરકારી સત્તાવાળાઓ દ્વારા ચકાસવી જોઈએ.",
}
