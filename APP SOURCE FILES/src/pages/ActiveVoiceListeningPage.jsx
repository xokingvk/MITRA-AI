import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const ActiveVoiceListeningPage = () => {
  const navigate = useNavigate();
  const { spokenQuery, setSpokenQuery, setSearchQuery, t } = useApp();
  const [analyzing, setAnalyzing] = useState(false);
  const [waveHeights, setWaveHeights] = useState([20, 36, 56, 44, 64, 40, 56, 28, 48, 60, 32, 16]);

  useEffect(() => {
    const interval = setInterval(() => {
      setWaveHeights(prev => prev.map(() => Math.floor(Math.random() * 45) + 12));
    }, 240);
    return () => clearInterval(interval);
  }, []);

  const handleDoneSpeaking = () => {
    setAnalyzing(true);
    setSearchQuery(spokenQuery || t("activeVoice.spokenQuery"));
    setTimeout(() => {
      navigate('/search-results');
    }, 1000);
  };

  const handleRestart = () => {
    setSpokenQuery(t("activeVoice.spokenQuery"));
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("activeVoice.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Top Status Bar */}
        <div className="flex items-center justify-between gap-2 pt-1">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-warm-white shadow-sm border border-border-warm-gray/30">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-secondary"></span>
            </span>
            <span className="font-label-sm text-xs font-semibold text-secondary">
              {t("activeVoice.listening")}
            </span>
          </div>

          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-warm-white shadow-sm border border-border-warm-gray/30">
            <span className="material-symbols-outlined text-[16px] text-emerald-600 font-bold">graphic_eq</span>
            <span className="font-label-sm text-xs text-text-charcoal font-medium">
              {t("activeVoice.goodClarity")}
            </span>
          </div>
        </div>

        {/* Dynamic Waveform Centerpiece */}
        <div className="relative flex flex-col items-center justify-center p-6 rounded-3xl bg-surface-warm-white shadow-sm overflow-hidden min-h-[180px] border border-border-warm-gray/40">
          <div className="flex flex-col items-center text-center z-10 mb-4">
            <p className="font-headline-sm text-base font-bold text-text-charcoal">
              {t("activeVoice.listening")}
            </p>
            <p className="font-body-sm text-xs text-text-slate mt-0.5">
              {t("home.speakSub")}
            </p>
          </div>

          <div className="flex items-center justify-center gap-1.5 h-16 w-full px-4 z-10">
            {waveHeights.map((h, i) => (
              <span
                key={i}
                className="w-1.5 rounded-full bg-primary-container transition-all duration-200"
                style={{ height: `${h}px` }}
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
            <span className="text-[11px] font-semibold text-secondary flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse"></span>
              {t("activeVoice.transcribingLive")}
            </span>
          </div>

          <div className="bg-surface-sand/60 p-4 rounded-2xl border border-border-warm-gray/30">
            <p className="font-body-md text-sm text-text-charcoal leading-relaxed">
              "{spokenQuery || t("activeVoice.spokenQuery")}"
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs font-semibold text-emerald-800 bg-emerald-50 px-3 py-2 rounded-xl border border-emerald-200">
            <span className="material-symbols-outlined text-[18px]">verified</span>
            <span>{t("activeVoice.potentialMatch")}</span>
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
              onClick={() => navigate('/')}
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
