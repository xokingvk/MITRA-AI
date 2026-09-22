import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const EkycSuccessDbtConfirmationPage = () => {
  const navigate = useNavigate();
  const { userProfile, speakText, stopAudio, isPlayingAudio, t } = useApp();

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else {
      speakText(t("kyc.successSub"));
    }
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("kyc.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Success Card */}
        <section className="bg-emerald-50 border border-emerald-200 rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
            <span className="material-symbols-outlined text-[32px]">verified</span>
          </div>
          <div className="min-w-0">
            <h2 className="font-headline-sm text-base font-bold text-emerald-950">
              {t("kyc.successTitle")}
            </h2>
            <p className="font-body-sm text-xs text-emerald-800 mt-0.5">
              {t("kyc.successSub")}
            </p>
          </div>
        </section>

        {/* Details Card */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="flex justify-between items-center py-2 border-b border-border-warm-gray/20 text-xs">
            <span className="text-text-slate font-medium">Beneficiary Name</span>
            <span className="text-text-charcoal font-bold">{userProfile.name}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-border-warm-gray/20 text-xs">
            <span className="text-text-slate font-medium">Linked Bank</span>
            <span className="text-text-charcoal font-bold">{userProfile.linkedBank}</span>
          </div>
          <div className="flex justify-between items-center py-2 text-xs">
            <span className="text-text-slate font-medium">NPCI Seeding</span>
            <span className="text-emerald-700 font-bold">{t("kyc.npciSeeded")}</span>
          </div>

          <button
            onClick={toggleAudio}
            className="w-full py-2.5 rounded-2xl bg-surface-sand text-secondary font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors flex items-center justify-center gap-1.5 mt-2"
            type="button"
          >
            <span className="material-symbols-outlined text-[18px]">
              {isPlayingAudio ? 'stop' : 'volume_up'}
            </span>
            <span>{t("common.listen")}</span>
          </button>
        </section>

        {/* Actions */}
        <section className="flex flex-col gap-3">
          <button
            onClick={() => navigate('/kyc/npci-mandate')}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            <span>{t("kyc.previewMandate")}</span>
            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default EkycSuccessDbtConfirmationPage;
