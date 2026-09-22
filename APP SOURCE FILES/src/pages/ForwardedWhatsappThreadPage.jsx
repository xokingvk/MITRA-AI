import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const ForwardedWhatsappThreadPage = () => {
  const navigate = useNavigate();
  const { t } = useApp();

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("whatsapp.threadTitle")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        <div className="flex flex-col gap-1 pt-1">
          <h1 className="font-headline-sm text-xl font-bold text-text-charcoal">
            {t("whatsapp.threadTitle")}
          </h1>
        </div>

        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="p-3 bg-surface-sand/60 rounded-2xl border border-border-warm-gray/30 text-xs">
            <span className="font-semibold text-text-charcoal block">
              PM-KISAN Document Verification Instructions
            </span>
            <span className="text-text-slate block mt-1">
              Please submit land Patta passbook and Aadhaar OTP at bank counter.
            </span>
          </div>

          <button
            onClick={() => navigate('/whatsapp-voice-dialog')}
            className="w-full py-3.5 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[48px]"
            type="button"
          >
            <span>{t("whatsapp.voiceNoteTitle")}</span>
            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default ForwardedWhatsappThreadPage;
