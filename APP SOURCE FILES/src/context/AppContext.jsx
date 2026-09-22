import React, { createContext, useContext, useState, useEffect } from 'react';
import { voiceService } from '../services/voiceService';
import { getTranslation } from '../i18n/translations';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // Canonical language state ('en', 'ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn', 'gu')
  const [language, setLanguageState] = useState(() => {
    const stored = localStorage.getItem('mitra_language');
    return stored ? stored.toLowerCase() : 'en';
  });
  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState(false);

  const setLanguage = (newLang) => {
    const canonical = (newLang || 'en').toLowerCase();
    setLanguageState(canonical);
    localStorage.setItem('mitra_language', canonical);
  };

  const t = (key) => getTranslation(language, key);

  // User Profile
  const [userProfile, setUserProfile] = useState({
    name: "Ramesh Kumar",
    tamilName: "ரமேஷ் குமார்",
    aadhaarLast4: "4892",
    mobile: "+91 98765 43210",
    aadhaarMasked: "XXXX-XXXX-4892",
    isEkycVerified: false,
    isNpciSeeded: false,
    linkedBank: "State Bank of India (A/C ****4091)",
    village: "Vaduvur",
    district: "Thanjavur",
    state: "Tamil Nadu"
  });

  // Voice Assistant
  const [isListening, setIsListening] = useState(false);
  const [spokenQuery, setSpokenQuery] = useState("2 acres land in Thanjavur - Financial aid & seeds");
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioTranscript, setAudioTranscript] = useState(
    "Based on your 2-acre land holding in Thanjavur, you qualify for PM-Kisan Samman Nidhi (₹6,000/yr) and subsidized paddy seeds."
  );

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  // Document Upload
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [analysisResult, setAnalysisResult] = useState({
    documentType: "Land Ownership Certificate (Patta Passbook)",
    ownerName: "Ramesh Kumar",
    landSize: "1.85 Acres (0.75 Hectares)",
    surveyNo: "241/3B",
    village: "Vaduvur, Thanjavur",
    isEligible: true
  });

  // Accessibility
  const [accessibility, setAccessibility] = useState({
    largeText: false,
    highContrast: false,
    voiceSpeed: "Normal",
    screenReader: false
  });

  useEffect(() => {
    const rootEl = document.documentElement;
    if (accessibility.largeText) {
      rootEl.classList.add('large-text-mode');
    } else {
      rootEl.classList.remove('large-text-mode');
    }

    if (accessibility.highContrast) {
      rootEl.classList.add('dark');
    } else {
      rootEl.classList.remove('dark');
    }
  }, [accessibility]);

  // Voice Interactions
  const toggleListening = () => {
    if (isListening) {
      voiceService.stopListening();
      setIsListening(false);
    } else {
      setIsListening(true);
      voiceService.startListening(
        (transcript) => {
          setSpokenQuery(transcript);
        },
        (error) => {
          console.error("Voice input error:", error);
          setIsListening(false);
        },
        () => {
          setIsListening(false);
        }
      );
    }
  };

  const speakText = (text) => {
    setIsPlayingAudio(true);
    voiceService.speak(text, () => {
      setIsPlayingAudio(false);
    });
  };

  const stopAudio = () => {
    voiceService.stopSpeaking();
    setIsPlayingAudio(false);
  };

  return (
    <AppContext.Provider
      value={{
        language,
        setLanguage,
        t,
        isLanguageModalOpen,
        setIsLanguageModalOpen,
        userProfile,
        setUserProfile,
        isListening,
        setIsListening,
        spokenQuery,
        setSpokenQuery,
        isPlayingAudio,
        audioTranscript,
        toggleListening,
        speakText,
        speak: speakText,
        isSpeaking: isPlayingAudio,
        stopAudio,
        searchQuery,
        setSearchQuery,
        selectedCategory,
        setSelectedCategory,
        uploadedDoc,
        setUploadedDoc,
        analysisResult,
        setAnalysisResult,
        accessibility,
        setAccessibility,
        accessibilitySettings: accessibility,
        setAccessibilitySettings: setAccessibility
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
