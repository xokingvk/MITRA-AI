import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { sendChatMessage } from '../services/api';

export const ActiveVoiceListeningPage = () => {
  const navigate = useNavigate();
  const { 
    spokenQuery, 
    setSpokenQuery, 
    setSearchQuery, 
    isListening, 
    startListening, 
    stopListening, 
    speakText,
    language,
    t 
  } = useApp();

  const [analyzing, setAnalyzing] = useState(false);
  const [uiNotice, setUiNotice] = useState('');
  const [waveHeights, setWaveHeights] = useState([20, 36, 56, 44, 64, 40, 56, 28, 48, 60, 32, 16]);
  const hasSubmittedRef = useRef(false);

  useEffect(() => {
    startListening((fullText) => {
      if (fullText) setUiNotice('');
    }, (errorMsg) => {
      setUiNotice(errorMsg);
    });

    const interval = setInterval(() => {
      setWaveHeights(prev => prev.map(() => Math.floor(Math.random() * 45) + 12));
    }, 240);

    return () => {
      clearInterval(interval);
      stopListening();
    };
  }, []);

  const handleDoneSpeaking = async () => {
    if (hasSubmittedRef.current) return;

    const trimmedQuery = spokenQuery ? spokenQuery.trim() : "";
    if (!trimmedQuery) {
      console.warn("[VOICE] Submission blocked: empty transcript.");
      setUiNotice("Please speak into your microphone or type your query below before submitting.");
      return;
    }

    hasSubmittedRef.current = true;
    setAnalyzing(true);
    stopListening();

    setSearchQuery(trimmedQuery);

    try {
      const response = await sendChatMessage(trimmedQuery, language);
      if (response && response.answer) {
        speakText(response.answer);
      }
    } catch (err) {
      console.warn("Backend chat query notice:", err);
    } finally {
      navigate('/search-results');
    }
  };

  const handleRestart = () => {
    hasSubmittedRef.current = false;
    stopListening();
    setSpokenQuery('');
    setUiNotice('');
    setTimeout(() => {
      startListening();
    }, 200);
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("activeVoice.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Top Status Bar */}
        <div className="flex items-center justify-between gap-2 pt-1">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-warm-white shadow-sm border border-border-warm-gray/30">
            <span className="relative flex h-2.5 w-2.5">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isListening ? 'bg-secondary' : 'bg-slate-400'} opacity-75`}></span>
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${isListening ? 'bg-secondary' : 'bg-slate-400'}`}></span>
            </span>
            <span className={`font-label-sm text-xs font-semibold ${isListening ? 'text-secondary' : 'text-slate-600'}`}>
              {isListening ? t("activeVoice.listening") : "Paused"}
            </span>
          </div>

          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-warm-white shadow-sm border border-border-warm-gray/30">
            <span className="material-symbols-outlined text-[16px] text-emerald-600 font-bold">graphic_eq</span>
            <span className="font-label-sm text-xs text-text-charcoal font-medium">
              {t("activeVoice.goodClarity")}
            </span>
          </div>
        </div>

        {/* Notice Banner */}
        {uiNotice && (
          <div className="p-3 bg-amber-50 border border-amber-200 text-amber-900 rounded-2xl text-xs font-medium leading-relaxed">
            {uiNotice}
          </div>
        )}

        {/* Dynamic Waveform Centerpiece */}
        <div className="relative flex flex-col items-center justify-center p-6 rounded-3xl bg-surface-warm-white shadow-sm overflow-hidden min-h-[180px] border border-border-warm-gray/40">
          <div className="flex flex-col items-center text-center z-10 mb-4">
            <p className="font-headline-sm text-base font-bold text-text-charcoal">
              {isListening ? t("activeVoice.listening") : "Tap Done to Submit"}
            </p>
            <p className="font-body-sm text-xs text-text-slate mt-0.5">
              {t("home.speakSub")}
            </p>
          </div>

          <div className="flex items-center justify-center gap-1.5 h-16 w-full px-4 z-10">
            {waveHeights.map((h, i) => (
              <span
                key={i}
                className={`w-1.5 rounded-full transition-all duration-200 ${isListening ? 'bg-primary-container' : 'bg-slate-300'}`}
                style={{ height: isListening ? `${h}px` : '12px' }}
              />
            ))}
          </div>
        </div>

        {/* Real-time Transcript */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="flex items-center justify-between border-b border-border-warm-gray/30 pb-2.5">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[20px] text-primary-container">notes</span>
              <h3 className="font-headline-sm text-sm font-bold text-text-charcoal">
                {t("activeVoice.realtimeTranscript")}
              </h3>
            </div>
            {isListening && (
              <span className="text-[11px] font-semibold text-secondary flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse"></span>
                {t("activeVoice.transcribingLive")}
              </span>
            )}
          </div>

          <div className="bg-surface-sand/60 p-4 rounded-2xl border border-border-warm-gray/30 flex flex-col gap-2">
            <textarea
              id="voiceTranscriptInput"
              value={spokenQuery}
              onChange={(e) => setSpokenQuery(e.target.value)}
              placeholder="Listening... speak into your microphone or edit text here"
              rows={3}
              className="w-full bg-transparent font-body-md text-sm text-text-charcoal leading-relaxed focus:outline-none resize-none"
            />
          </div>
        </section>

        {/* Actions */}
        <section className="flex flex-col gap-3">
          <button
            onClick={handleDoneSpeaking}
            disabled={analyzing}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            {analyzing ? (
              <>
                <span className="material-symbols-outlined text-[20px] animate-spin">sync</span>
                <span>{t("activeVoice.analyzingSchemes")}</span>
              </>
            ) : (
              <>
                <span>{t("activeVoice.doneSpeaking")}</span>
                <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
              </>
            )}
          </button>

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={handleRestart}
              className="py-3 rounded-2xl bg-surface-sand text-text-charcoal font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors border border-border-warm-gray/40 min-h-[44px]"
              type="button"
            >
              {t("activeVoice.clearRestart")}
            </button>
            <button
              onClick={() => {
                stopListening();
                navigate('/');
              }}
              className="py-3 rounded-2xl bg-surface-sand text-text-charcoal font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors border border-border-warm-gray/40 min-h-[44px]"
              type="button"
            >
              {t("activeVoice.typeInstead")}
            </button>
          </div>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default ActiveVoiceListeningPage;
