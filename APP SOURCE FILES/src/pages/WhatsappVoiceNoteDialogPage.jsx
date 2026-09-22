import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const WhatsappVoiceNoteDialogPage = () => {
  const navigate = useNavigate();
  const { t, speakText, isPlayingAudio, stopAudio } = useApp();

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else {
      speakText(t("results.querySub"));
    }
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("whatsapp.voiceNoteTitle")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        <div className="flex flex-col gap-1 pt-1">
          <h1 className="font-headline-sm text-xl font-bold text-text-charcoal">
            {t("whatsapp.voiceNoteTitle")}
          </h1>
        </div>

        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center justify-between p-3 bg-surface-sand/60 rounded-2xl border border-border-warm-gray/30">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary text-[22px]">graphic_eq</span>
              <span className="font-label-md text-xs font-semibold text-text-charcoal">
                WhatsApp Voice Note
              </span>
            </div>
            <button
              onClick={toggleAudio}
              className="w-9 h-9 rounded-full bg-primary-container text-on-primary flex items-center justify-center"
              type="button"
            >
              <span className="material-symbols-outlined text-[18px]">
                {isPlayingAudio ? 'stop' : 'play_arrow'}
              </span>
            </button>
          </div>

          <button
            onClick={() => navigate('/')}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            <span>{t("common.done")}</span>
            <span className="material-symbols-outlined text-[20px]">check</span>
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default WhatsappVoiceNoteDialogPage;
