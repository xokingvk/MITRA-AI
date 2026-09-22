import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const DocumentResultEligibilityConfirmationPage = () => {
  const navigate = useNavigate();
  const { analysisResult, speakText, isPlayingAudio, stopAudio, t } = useApp();

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else {
      speakText(t("doc.speechVerified"));
    }
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("doc.docReady")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Verification Success Header */}
        <section className="bg-emerald-50 border border-emerald-200 rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
            <span className="material-symbols-outlined text-[28px]">check_circle</span>
          </div>
          <div className="min-w-0">
            <h2 className="font-headline-sm text-base font-bold text-emerald-950">
              {t("doc.docReady")} • {t("common.verified")}
            </h2>
            <p className="font-body-sm text-xs text-emerald-800 mt-0.5">
              {t("common.eligible")} • PM-KISAN
            </p>
          </div>
        </section>

        {/* Audio Summary Card */}
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

        {/* Extracted Document Details */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <h3 className="font-headline-sm text-sm font-bold text-text-charcoal uppercase tracking-wider">
            {t("doc.title")}
          </h3>

          <div className="flex flex-col gap-2.5 pt-1">
            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20 text-xs">
              <span className="text-text-slate font-medium">{t("doc.ownerName")}</span>
              <span className="text-text-charcoal font-semibold">{analysisResult.ownerName}</span>
            </div>

            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20 text-xs">
              <span className="text-text-slate font-medium">{t("doc.landSize")}</span>
              <span className="text-text-charcoal font-semibold">{analysisResult.landSize}</span>
            </div>

            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20 text-xs">
              <span className="text-text-slate font-medium">{t("doc.surveyNo")}</span>
              <span className="text-text-charcoal font-semibold">{analysisResult.surveyNo}</span>
            </div>

            <div className="flex justify-between items-center py-1.5 text-xs">
              <span className="text-text-slate font-medium">{t("doc.village")}</span>
              <span className="text-text-charcoal font-semibold">{analysisResult.village}</span>
            </div>
          </div>
        </section>

        {/* Next Action Buttons */}
        <section className="flex flex-col gap-3">
          <button
            onClick={() => navigate('/scheme/pm-kisan/result')}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            <span>{t("doc.askEligibility")}</span>
            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
          </button>

          <button
            onClick={() => navigate('/document-upload')}
            className="w-full py-3.5 rounded-full bg-surface-sand text-text-charcoal font-label-md text-sm font-semibold border border-border-warm-gray/50 hover:bg-surface-dim active:scale-[0.98] transition-all min-h-[48px]"
            type="button"
          >
            {t("doc.retry")}
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default DocumentResultEligibilityConfirmationPage;
