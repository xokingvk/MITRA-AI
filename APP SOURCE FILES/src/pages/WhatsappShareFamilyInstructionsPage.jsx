import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const WhatsappShareFamilyInstructionsPage = () => {
  const navigate = useNavigate();
  const { t } = useApp();

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("whatsapp.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        <div className="flex flex-col gap-1 pt-1">
          <h1 className="font-headline-sm text-xl font-bold text-text-charcoal">
            {t("whatsapp.title")}
          </h1>
          <p className="font-body-sm text-xs text-text-slate">
            {t("whatsapp.shareSub")}
          </p>
        </div>

        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center gap-3 p-3 bg-emerald-50 rounded-2xl border border-emerald-200">
            <span className="material-symbols-outlined text-emerald-600 text-[24px]">send</span>
            <span className="font-label-md text-sm font-bold text-emerald-950">
              Share Instructions
            </span>
          </div>

          <button
            onClick={() => navigate('/whatsapp-thread')}
            className="w-full py-3.5 rounded-full bg-emerald-600 text-white font-label-md text-sm font-semibold hover:bg-emerald-700 active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[48px]"
            type="button"
          >
            <span>{t("common.share")}</span>
            <span className="material-symbols-outlined text-[20px]">share</span>
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default WhatsappShareFamilyInstructionsPage;
