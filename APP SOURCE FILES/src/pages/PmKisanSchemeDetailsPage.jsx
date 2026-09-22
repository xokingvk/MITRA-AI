import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { getSchemeById } from '../services/schemeService';

export const PmKisanSchemeDetailsPage = () => {
  const navigate = useNavigate();
  const { schemeId } = useParams();
  const { speakText, stopAudio, isPlayingAudio, setSearchQuery, setSpokenQuery, t } = useApp();

  const scheme = getSchemeById(schemeId || 'pm-kisan', t);

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else {
      speakText(`${scheme.title}. ${scheme.shortDescription}`);
    }
  };

  const handleAskMitra = () => {
    const prompt = `Tell me more about ${scheme.title} and how to access its benefits`;
    setSearchQuery(prompt);
    setSpokenQuery(prompt);
    navigate('/search-results');
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("schemeDetails.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Scheme Header Card */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold">
              {t("common.verified")}
            </span>
            <span className="px-3 py-1 rounded-full bg-surface-sand text-primary-container font-label-sm text-xs font-semibold border border-border-warm-gray/40">
              {scheme.category}
            </span>
          </div>

          <h1 className="font-headline-sm text-xl font-bold text-text-charcoal leading-snug">
            {scheme.title}
          </h1>
          
          <div className="flex items-center justify-between gap-2 pt-1 border-t border-border-warm-gray/30 text-xs text-text-slate">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px] text-primary-container">groups</span>
              <span>{t("schemeDetails.genderEligible")}: <strong>{scheme.genderEligible}</strong></span>
            </span>
            <span className="px-2.5 py-1 rounded-xl bg-emerald-50 text-emerald-800 font-bold">
              {scheme.benefitAmount}
            </span>
          </div>

          <button
            onClick={toggleAudio}
            className="w-full py-3 rounded-2xl bg-surface-sand text-secondary font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors flex items-center justify-center gap-2 min-h-[44px]"
            type="button"
          >
            <span className="material-symbols-outlined text-[18px]">
              {isPlayingAudio ? 'stop' : 'volume_up'}
            </span>
            <span>{t("common.listen")}</span>
          </button>
        </section>

        {/* Benefits Section */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <h2 className="font-headline-sm text-base font-bold text-text-charcoal flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary text-[20px]">health_and_safety</span>
            {t("schemeDetails.benefits")}
          </h2>

          <p className="font-body-sm text-xs text-text-slate leading-relaxed">
            {scheme.keyBenefits || scheme.shortDescription}
          </p>
        </section>

        {/* Eligibility Criteria / Target Group */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <h2 className="font-headline-sm text-base font-bold text-text-charcoal flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-container text-[20px]">checklist</span>
            {t("schemeDetails.eligibility")}
          </h2>

          <ul className="flex flex-col gap-2 text-xs text-text-charcoal">
            {Array.isArray(scheme.eligibilityCriteria) ? (
              scheme.eligibilityCriteria.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-emerald-600 text-[18px] flex-shrink-0">check_circle</span>
                  <span>{item}</span>
                </li>
              ))
            ) : (
              <li className="flex items-start gap-2">
                <span className="material-symbols-outlined text-emerald-600 text-[18px] flex-shrink-0">check_circle</span>
                <span>{scheme.eligibilityCriteria}</span>
              </li>
            )}
          </ul>
        </section>

        {/* Official Source & Authority */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <h2 className="font-headline-sm text-base font-bold text-text-charcoal flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-container text-[20px]">verified</span>
            {t("schemeDetails.officialSource")}
          </h2>

          <div className="flex flex-col gap-2 text-xs text-text-slate">
            <p className="font-semibold text-text-charcoal">{scheme.officialSource}</p>
            {scheme.sourceUrl && (
              <a
                href={scheme.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-primary-container font-semibold hover:underline mt-1 break-all"
              >
                <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                <span>{scheme.sourceUrl}</span>
              </a>
            )}
          </div>
        </section>

        {/* Production Notice */}
        <div className="bg-amber-50 p-4 rounded-2xl border border-amber-200 text-amber-900 text-xs leading-relaxed flex items-start gap-2">
          <span className="material-symbols-outlined text-amber-700 text-[18px] flex-shrink-0 mt-0.5">info</span>
          <span>Based on published government scheme guidelines. Check current official guidelines before applying.</span>
        </div>

        {/* Actions */}
        <section className="flex flex-col gap-3">
          <button
            onClick={handleAskMitra}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            <span className="material-symbols-outlined text-[20px]">forum</span>
            <span>{t("schemeDetails.askMitra")}</span>
          </button>

          <button
            onClick={() => navigate('/scheme/pm-kisan/check')}
            className="w-full py-3.5 rounded-full bg-surface-sand text-text-charcoal font-label-md text-sm font-semibold hover:bg-surface-dim active:scale-[0.98] transition-all border border-border-warm-gray/40 flex items-center justify-center gap-2 min-h-[48px]"
            type="button"
          >
            <span>{t("schemes.checkEligibilityBtn")}</span>
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default PmKisanSchemeDetailsPage;

