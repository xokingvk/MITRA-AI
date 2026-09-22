import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const PmKisanConversationalEligibilityPage = () => {
  const navigate = useNavigate();
  const { t } = useApp();
  const [selectedOption, setSelectedOption] = useState('A');

  const handleNext = () => {
    navigate('/document-upload');
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("eligibility.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Progress Step Header */}
        <div className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-2">
          <div className="flex justify-between items-center font-label-sm text-xs">
            <span className="font-bold text-text-charcoal flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[18px] text-secondary">checklist</span>
              {t("eligibility.title")}
            </span>
            <span className="text-secondary font-bold">
              {t("eligibility.stepText")}
            </span>
          </div>
          <div className="w-full bg-surface-sand rounded-full h-2 overflow-hidden border border-border-warm-gray/30">
            <div className="bg-secondary h-full rounded-full w-1/3 transition-all duration-300"></div>
          </div>
        </div>

        {/* Question & Options */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <h2 className="font-headline-sm text-base font-bold text-text-charcoal leading-snug">
            {t("eligibility.landQuestion")}
          </h2>

          <div className="flex flex-col gap-3">
            <button
              onClick={() => setSelectedOption('A')}
              className={`p-4 rounded-2xl border text-left flex items-center justify-between transition-all min-h-[56px] ${
                selectedOption === 'A'
                  ? 'bg-primary-container text-on-primary font-semibold shadow-sm border-primary-container'
                  : 'bg-surface-sand/60 text-text-charcoal border-border-warm-gray/40 hover:bg-surface-sand'
              }`}
              type="button"
            >
              <span className="font-label-md text-xs">{t("eligibility.landOpt1")}</span>
              {selectedOption === 'A' && (
                <span className="material-symbols-outlined text-[20px] text-on-primary">check_circle</span>
              )}
            </button>

            <button
              onClick={() => setSelectedOption('B')}
              className={`p-4 rounded-2xl border text-left flex items-center justify-between transition-all min-h-[56px] ${
                selectedOption === 'B'
                  ? 'bg-primary-container text-on-primary font-semibold shadow-sm border-primary-container'
                  : 'bg-surface-sand/60 text-text-charcoal border-border-warm-gray/40 hover:bg-surface-sand'
              }`}
              type="button"
            >
              <span className="font-label-md text-xs">{t("eligibility.landOpt2")}</span>
              {selectedOption === 'B' && (
                <span className="material-symbols-outlined text-[20px] text-on-primary">check_circle</span>
              )}
            </button>

            <button
              onClick={() => setSelectedOption('C')}
              className={`p-4 rounded-2xl border text-left flex items-center justify-between transition-all min-h-[56px] ${
                selectedOption === 'C'
                  ? 'bg-primary-container text-on-primary font-semibold shadow-sm border-primary-container'
                  : 'bg-surface-sand/60 text-text-charcoal border-border-warm-gray/40 hover:bg-surface-sand'
              }`}
              type="button"
            >
              <span className="font-label-md text-xs">{t("eligibility.landOpt3")}</span>
              {selectedOption === 'C' && (
                <span className="material-symbols-outlined text-[20px] text-on-primary">check_circle</span>
              )}
            </button>
          </div>
        </section>

        {/* Action Button */}
        <button
          onClick={handleNext}
          className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
          type="button"
        >
          <span>{t("common.continue")}</span>
          <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
        </button>

      </main>

      <BottomNav />
    </div>
  );
};

export default PmKisanConversationalEligibilityPage;
