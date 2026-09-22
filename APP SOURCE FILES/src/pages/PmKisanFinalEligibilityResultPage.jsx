import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const PmKisanFinalEligibilityResultPage = () => {
  const navigate = useNavigate();
  const { speakText, stopAudio, isPlayingAudio, t } = useApp();

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else {
      speakText(t("eligibilityResult.qualifyDesc"));
    }
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("eligibilityResult.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Success Banner */}
        <section className="bg-emerald-50 border border-emerald-200 rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
            <span className="material-symbols-outlined text-[32px]">check_circle</span>
          </div>
          <div className="min-w-0">
            <h2 className="font-headline-sm text-lg font-bold text-emerald-950">
              {t("eligibilityResult.qualified")}
            </h2>
            <p className="font-body-sm text-xs text-emerald-800 mt-0.5 leading-relaxed">
              {t("eligibilityResult.qualifyDesc")}
            </p>
          </div>
        </section>

        {/* Audio Player Card */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-secondary-container/30 text-secondary flex items-center justify-center flex-shrink-0">
              <span className="material-symbols-outlined text-[22px]">volume_up</span>
            </div>
            <div className="min-w-0">
              <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                {t("common.listen")}
              </span>
              <span className="font-body-sm text-xs text-text-slate block">
                {t("results.querySub")}
              </span>
            </div>
          </div>
          <button
            onClick={toggleAudio}
            className="w-10 h-10 rounded-full bg-primary-container text-on-primary flex items-center justify-center flex-shrink-0 active:scale-95 transition-transform"
            type="button"
          >
            <span className="material-symbols-outlined text-[20px]">
              {isPlayingAudio ? 'stop' : 'play_arrow'}
            </span>
          </button>
        </section>

        {/* Action Button */}
        <section className="flex flex-col gap-3">
          <button
            onClick={() => navigate('/kyc/aadhaar-otp')}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            <span>{t("eligibilityResult.nextKyc")}</span>
            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default PmKisanFinalEligibilityResultPage;
