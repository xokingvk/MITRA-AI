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

  // User Profile (Initialized to null - NO default demo user)
  const [userProfile, setUserProfile] = useState(null);

  const clearSession = () => {
    setUserProfile(null);
    setUploadedDoc(null);
    setAnalysisResult(null);
    setSpokenQuery("");
    setSearchQuery("");
  };

  // Voice Assistant
  const [isListening, setIsListening] = useState(false);
  const [spokenQuery, setSpokenQuery] = useState("");
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioTranscript, setAudioTranscript] = useState("");

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  // Document Upload
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

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
  const startRecordingAudio = async () => {
    try {
      setIsListening(true);
      await voiceService.startRecording();
    } catch (err) {
      setIsListening(false);
      console.error("[AppContext] startRecording error:", err);
      throw err;
    }
  };

  const stopRecordingAudio = async () => {
    try {
      setIsListening(false);
      const audioBlob = await voiceService.stopRecording();
      return audioBlob;
    } catch (err) {
      setIsListening(false);
      console.error("[AppContext] stopRecording error:", err);
      throw err;
    }
  };

  const speakText = (text) => {
    if (!text) return;
    setIsPlayingAudio(true);
    voiceService.speak(text, () => {
      setIsPlayingAudio(false);
    }, language);
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
        clearSession,
        isListening,
        setIsListening,
        spokenQuery,
        setSpokenQuery,
        isPlayingAudio,
        audioTranscript,
        startListening: startRecordingAudio,
        stopListening: stopRecordingAudio,
        startRecordingAudio,
        stopRecordingAudio,
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
