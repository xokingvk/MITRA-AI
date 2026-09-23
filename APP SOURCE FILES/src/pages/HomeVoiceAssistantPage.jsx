import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const HomeVoiceAssistantPage = () => {
  const navigate = useNavigate();
  const { 
    isListening, 
    toggleListening, 
    setSpokenQuery, 
    setSearchQuery,
    setUploadedDoc,
    t,
    userProfile
  } = useApp();

  const [inputVal, setInputVal] = useState('');
  const [toastMsg, setToastMsg] = useState('');
  const fileInputRef = useRef(null);

  const showToast = (msg) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(''), 3000);
  };

  const handlePromptClick = (query) => {
    setSpokenQuery(query);
    setSearchQuery(query);
    showToast(`Searching: "${query}"`);
    navigate('/search-results');
  };

  const handleFileUpload = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadedDoc(file);
      showToast(`${t("doc.uploading")} ${file.name}`);
      setTimeout(() => {
        navigate('/document-analyzing');
      }, 1000);
    }
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (inputVal.trim()) {
      setSpokenQuery(inputVal.trim());
      setSearchQuery(inputVal.trim());
      setInputVal('');
      navigate('/search-results');
    } else {
      toggleListening();
    }
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("nav.home")} />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col items-center gap-6">
        
        {/* Civic Welcoming Greeting (Centered) */}
        <section className="w-full flex flex-col items-center text-center gap-1 pt-2">
          <h1 className="font-headline-lg text-[28px] font-bold text-text-charcoal tracking-tight">
            {t("home.greeting").replace("Ramesh", userProfile.name.split(" ")[0])}
          </h1>
          <p className="font-headline-sm text-lg font-semibold text-primary-container">
            {t("home.question")}
          </p>
        </section>

        {/* Primary Action Card: Speak & Type (Centered) */}
        <section className="w-full bg-surface-warm-white rounded-3xl p-6 shadow-sm flex flex-col items-center text-center border border-border-warm-gray/40">
          
          {/* Dynamic Voice Waveform or Status */}
          {isListening && (
            <div className="flex items-center justify-center gap-1.5 h-10 mb-3 px-4 py-1.5 bg-surface-sand rounded-full animate-pulse">
              <span className="w-1.5 h-4 bg-primary-container rounded-full animate-bounce"></span>
              <span className="w-1.5 h-7 bg-secondary rounded-full animate-pulse"></span>
              <span className="w-1.5 h-9 bg-primary-container rounded-full animate-bounce"></span>
              <span className="w-1.5 h-5 bg-secondary rounded-full animate-pulse"></span>
            </div>
          )}

          <div className="mb-4 text-center">
            <p className={`font-label-lg text-base font-bold ${isListening ? 'text-secondary' : 'text-text-charcoal'}`}>
              {isListening ? t("voice.listening") : t("home.speak")}
            </p>
            <p className="font-body-sm text-xs text-text-slate mt-0.5 max-w-xs mx-auto">
              {t("home.speakSub")}
            </p>
          </div>

          {/* Large Circular 72px Touch Button (Centered) */}
          <div className="relative flex items-center justify-center my-2 mx-auto">
            {isListening && (
              <div className="absolute w-24 h-24 rounded-full bg-secondary/20 animate-ping"></div>
            )}
            <button
              onClick={() => navigate('/active-voice')}
              aria-label={t("home.speak")}
              className={`relative z-10 min-w-[72px] min-h-[72px] w-20 h-20 rounded-full text-on-primary flex flex-col items-center justify-center shadow-lg active:scale-95 transition-all focus:outline-none ${
                isListening ? 'bg-secondary animate-pulse-ring' : 'bg-primary-container hover:bg-primary'
              }`}
              type="button"
            >
              <span className="material-symbols-outlined text-[36px]">
                {isListening ? 'graphic_eq' : 'mic'}
              </span>
            </button>
          </div>

          {/* Single Centered Upload Document Action */}
          <div className="w-full flex justify-center mt-6 pt-4 border-t border-border-warm-gray/30">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full max-w-xs min-h-[48px] px-4 py-3 rounded-2xl bg-surface-sand text-text-charcoal flex items-center justify-center gap-2 font-label-md text-sm font-semibold hover:bg-surface-dim active:scale-[0.98] transition-all border border-border-warm-gray/40 shadow-sm"
              type="button"
            >
              <span className="material-symbols-outlined text-[20px] text-secondary">upload_file</span>
              <span>{t("common.upload")}</span>
            </button>
          </div>
        </section>

        {/* Query Input Bar Form (Centered) */}
        <form onSubmit={handleSubmit} className="w-full bg-surface-warm-white rounded-full p-2 border border-border-warm-gray/50 shadow-md flex items-center gap-2">
          <input
            id="userQueryInput"
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder={t("home.typePlaceholder")}
            className="flex-1 min-w-0 bg-transparent text-text-charcoal font-body-md text-sm placeholder:text-text-slate focus:outline-none px-3 py-1 text-left"
            autoComplete="off"
          />
          <button
            type="submit"
            aria-label={t("chat.send")}
            className="w-11 h-11 rounded-full bg-primary-container text-on-primary flex items-center justify-center flex-shrink-0 active:scale-95 transition-transform"
          >
            <span className="material-symbols-outlined text-[20px]">
              {inputVal.trim().length > 0 ? 'send' : 'mic'}
            </span>
          </button>
        </form>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,image/*"
          onChange={handleFileUpload}
          className="hidden"
        />

        {/* Toast Notification */}
        {toastMsg && (
          <div className="fixed top-20 left-1/2 -translate-x-1/2 z-50 bg-primary-container text-on-primary px-4 py-2 rounded-full text-xs font-semibold shadow-lg transition-all animate-bounce">
            <span>{toastMsg}</span>
          </div>
        )}

      </main>

      <BottomNav />
    </div>
  );
};

export default HomeVoiceAssistantPage;
