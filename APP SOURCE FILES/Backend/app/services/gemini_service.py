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
        """Provides accurate, short structured health scheme matching for offline/fallback mode."""
        q_lower = question.lower()

        if any(term in q_lower for term in ["pregnant", "pregnancy", "mother", "maternity", "delivery", "baby"]):
            return {
                "answer": (
                    "Based on what you shared, some government health schemes may be relevant to you.\n\n"
                    "Here are the schemes that may be relevant:\n\n"
                    "1. Pradhan Mantri Matru Vandana Yojana (PMMVY)\n"
                    "Maternity support for eligible pregnant women.\n\n"
                    "2. Janani Shishu Suraksha Karyakram (JSSK)\n"
                    "Free maternity and newborn services at eligible public health facilities.\n\n"
                    "You can select a scheme to see its eligibility, benefits and required documents."
                ),
                "voice_answer": "I found two schemes that may be relevant to you. You can see them on the screen.",
                "matched_schemes": [
                    {
                        "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
                        "short_description": "Maternity financial support for eligible pregnant women.",
                        "reason": "Pregnancy-related maternity welfare",
                        "eligibility": "Pregnant women and lactating mothers for first live birth in eligible socioeconomic categories.",
                        "benefits": "Direct cash assistance up to ₹5,000 in bank account for maternal nutrition.",
                        "documents": ["Aadhaar Card", "Mother and Child Protection (MCP) Card", "Bank Account Passbook"]
                    },
                    {
                        "name": "Janani Shishu Suraksha Karyakram (JSSK)",
                        "short_description": "Free maternity and newborn care at eligible public health facilities.",
                        "reason": "Free institutional delivery and newborn healthcare",
                        "eligibility": "All pregnant women delivering in public health institutions.",
                        "benefits": "Completely free normal delivery and C-section, free drugs, diagnostics, diet, and transport.",
                        "documents": ["Aadhaar Card / ID Proof", "Hospital Registration"]
                    }
                ],
                "needs_more_information": ["Annual household income", "State / District"]
            }

        elif any(term in q_lower for term in ["senior", "70", "elderly", "old age"]):
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
                "voice_answer": "I found two schemes that may be relevant to you. You can see them on the screen.",
                "matched_schemes": [
                    {
                        "name": "Ayushman Bharat PM-JAY (Senior Citizen 70+)",
                        "short_description": "Universal ₹5 Lakh annual hospital cover for all senior citizens aged 70+.",
                        "reason": "Senior citizen healthcare assurance",
                        "eligibility": "All Indian citizens aged 70 years and above, irrespective of income.",
                        "benefits": "₹5,00,000 cashless secondary and tertiary hospitalization cover per year.",
                        "documents": ["Aadhaar Card (with verified DOB)", "e-KYC Mobile verification"]
                    },
                    {
                        "name": "Rashtriya Vayoshri Yojana",
                        "short_description": "Free physical aids and assisted living devices for eligible seniors.",
                        "reason": "Age-related physical disability / mobility support",
                        "eligibility": "Senior citizens belonging to BPL category or monthly income below ₹15,000.",
                        "benefits": "Free hearing aids, walking sticks, wheelchairs, spectacles, and dentures.",
                        "documents": ["Aadhaar Card", "Age Proof", "Income / BPL Certificate"]
                    }
                ],
                "needs_more_information": ["State of residence"]
            }

        else:
            return {
                "answer": (
                    "Based on what you shared, some government health schemes may be relevant to you.\n\n"
                    "Here are the schemes that may be relevant:\n\n"
                    "1. Ayushman Bharat PM-JAY\n"
                    "Cashless hospital coverage up to ₹5 Lakh per family per year for secondary and tertiary care.\n\n"
                    "2. National Health Mission (NHM) Free Drugs & Diagnostics\n"
                    "Essential medicines and diagnostic tests provided free of cost at public health centers.\n\n"
                    "You can select a scheme to see its eligibility, benefits and required documents."
                ),
                "voice_answer": "I found schemes that may be relevant to you. You can see them on the screen.",
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
        """Extracts ONLY facts that are explicitly visible in the document using Gemini vision/text."""
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

        if not self.is_configured():
            logger.warning("Gemini API key not configured for document extraction. Using basic heuristic parsing.")
            if text_content:
                lowered = text_content.lower()
                if "aadhaar" in lowered or "uidai" in lowered:
                    default_profile["document_type"] = "Aadhaar Card"
                elif "income" in lowered or "salary" in lowered:
                    default_profile["document_type"] = "Income Certificate"
                elif "patta" in lowered or "land" in lowered:
                    default_profile["document_type"] = "Land Document"
            return default_profile

        try:
            contents = [DOCUMENT_EXTRACTION_PROMPT]

            # Multimodal support for image and PDF files
            if file_bytes and filename:
                fn_lower = filename.lower()
                if fn_lower.endswith((".jpg", ".jpeg")):
                    contents.append(types.Part.from_bytes(data=file_bytes, mime_type="image/jpeg"))
                elif fn_lower.endswith(".png"):
                    contents.append(types.Part.from_bytes(data=file_bytes, mime_type="image/png"))
                elif fn_lower.endswith(".pdf"):
                    contents.append(types.Part.from_bytes(data=file_bytes, mime_type="application/pdf"))

            if text_content:
                contents.append(f"Document Text Content:\n{text_content[:6000]}")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction="You are an accurate OCR and data extraction system. Extract ONLY visible facts. Return only valid JSON.",
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
