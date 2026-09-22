import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const AiResponseSchemeResultsPage = () => {
  const navigate = useNavigate();
  const { spokenQuery, speakText, stopAudio, isPlayingAudio, t } = useApp();

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else {
      speakText(t("results.querySub"));
    }
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("results.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Spoken Query Header Pill */}
        <div className="w-full bg-surface-warm-white rounded-3xl p-4 shadow-sm flex items-center justify-between gap-3 border border-border-warm-gray/40">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-full bg-secondary text-on-secondary flex items-center justify-center flex-shrink-0">
              <span className="material-symbols-outlined text-[18px]">mic</span>
            </div>
            <div className="min-w-0">
              <span className="font-label-sm text-[11px] text-text-slate block uppercase tracking-wider font-semibold">
                {t("activeVoice.spokenQuery")}
              </span>
              <p className="font-label-md text-xs font-bold text-text-charcoal truncate">
                "{spokenQuery || t("activeVoice.spokenQuery")}"
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate('/active-voice')}
            aria-label={t("common.retry")}
            className="p-2 rounded-full hover:bg-surface-sand text-secondary flex-shrink-0"
            type="button"
          >
            <span className="material-symbols-outlined text-[20px]">edit</span>
          </button>
        </div>

        {/* Audio Player Card */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-secondary-container/30 text-secondary flex items-center justify-center flex-shrink-0">
              <span className="material-symbols-outlined text-[22px]">volume_up</span>
            </div>
            <div className="min-w-0">
              <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                {t("results.verifiedGuidance")}
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

        {/* Recommended Schemes Section */}
        <section className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <h2 className="font-headline-sm text-base font-bold text-text-charcoal flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary text-[20px]">verified</span>
              {t("results.recommendedSchemes")}
            </h2>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold">
              {t("results.autoMatched")}
            </span>
          </div>

          <div className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <span className="inline-block px-2.5 py-0.5 rounded-full bg-surface-sand text-secondary text-[11px] font-semibold mb-1">
                  {t("results.highMatch")}
                </span>
                <h3 className="font-headline-sm text-base font-bold text-text-charcoal">
                  {t("schemes.pmKisan.title")}
                </h3>
              </div>
              <span className="px-2.5 py-1 rounded-xl bg-emerald-100 text-emerald-800 text-xs font-bold whitespace-nowrap flex-shrink-0">
                {t("schemes.pmKisan.benefitAmount")}
              </span>
            </div>

            <p className="font-body-sm text-xs text-text-slate leading-relaxed">
              {t("schemes.pmKisan.shortDescription")}
            </p>

            {/* Checklist */}
            <div className="flex flex-col gap-2 pt-2 border-t border-border-warm-gray/30">
              <span className="font-label-sm text-xs font-semibold text-text-slate uppercase tracking-wider">
                {t("results.eligibilityChecklist")}
              </span>

              <div className="flex items-center gap-2 text-xs text-emerald-800">
                <span className="material-symbols-outlined text-[18px] text-emerald-600">check_circle</span>
                <span>{t("results.marginalFarmer")}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-emerald-800">
                <span className="material-symbols-outlined text-[18px] text-emerald-600">check_circle</span>
                <span>{t("results.matchesLand")}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-amber-800">
                <span className="material-symbols-outlined text-[18px] text-amber-600">pending</span>
                <span>{t("results.needsDoc")}</span>
              </div>
            </div>

            <div className="flex items-center gap-2 pt-3 border-t border-border-warm-gray/30">
              <button
                onClick={() => navigate('/scheme/pm-kisan')}
                className="flex-1 py-2.5 rounded-2xl bg-surface-sand text-text-charcoal font-label-sm text-xs font-semibold hover:bg-surface-dim transition-all flex items-center justify-center gap-1 min-h-[44px]"
                type="button"
              >
                <span>{t("schemes.viewDetails")}</span>
              </button>
              <button
                onClick={() => navigate('/document-upload')}
                className="flex-1 py-2.5 rounded-2xl bg-primary-container text-on-primary font-label-sm text-xs font-semibold hover:bg-primary transition-all flex items-center justify-center gap-1 shadow-sm min-h-[44px]"
                type="button"
              >
                <span>{t("doc.uploadDoc")}</span>
              </button>
            </div>
          </div>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default AiResponseSchemeResultsPage;
