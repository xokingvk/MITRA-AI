import React from 'react';
import { useApp } from '../../context/AppContext';

export const LanguageModal = () => {
  const { language, setLanguage, isLanguageModalOpen, setIsLanguageModalOpen, t } = useApp();

  if (!isLanguageModalOpen) return null;

  const languages = [
    { code: 'en' },
    { code: 'ta' },
    { code: 'hi' },
    { code: 'te' },
    { code: 'kn' },
    { code: 'ml' },
    { code: 'mr' },
    { code: 'bn' },
    { code: 'gu' }
  ];

  return (
    <div 
      className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center bg-text-charcoal/50 backdrop-blur-sm p-0 sm:p-4 animate-in fade-in duration-200"
      onClick={() => setIsLanguageModalOpen(false)}
    >
      <div 
        className="w-full max-w-md bg-surface-warm-white rounded-t-3xl sm:rounded-3xl shadow-2xl border border-border-warm-gray animate-in slide-in-from-bottom duration-300 max-h-[85vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-border-warm-gray/40">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-container text-[24px]">language</span>
            <h3 className="font-headline-sm text-base font-bold text-primary-container">
              {t("settings.language")}
            </h3>
          </div>
          <button
            onClick={() => setIsLanguageModalOpen(false)}
            aria-label={t("common.close")}
            className="min-h-[48px] min-w-[48px] flex items-center justify-center rounded-full hover:bg-surface-container active:bg-surface-dim text-text-slate"
            type="button"
          >
            <span className="material-symbols-outlined text-[22px]">close</span>
          </button>
        </div>

        <div className="overflow-y-auto p-4 space-y-2.5 flex-1 touch-pan-y">
          {languages.map((lang) => {
            const isSelected = language.toLowerCase() === lang.code;
            const langName = t(`lang.${lang.code}`);

            return (
              <button
                key={lang.code}
                onClick={() => {
                  setLanguage(lang.code);
                  setIsLanguageModalOpen(false);
                }}
                className={`w-full min-h-[52px] px-4 py-3 rounded-2xl flex items-center justify-between text-left transition-all ${
                  isSelected
                    ? 'bg-primary-container text-on-primary font-semibold shadow-md ring-2 ring-primary-container/30'
                    : 'bg-surface-sand/70 hover:bg-surface-sand active:bg-surface-dim text-text-charcoal border border-border-warm-gray/40'
                }`}
                type="button"
              >
                <span className="font-label-lg text-base font-medium">
                  {langName}
                </span>

                {isSelected && (
                  <span className="material-symbols-outlined text-[24px] text-on-primary">check_circle</span>
                )}
              </button>
            );
          })}
        </div>

        <div className="p-4 border-t border-border-warm-gray/40 flex justify-end">
          <button
            onClick={() => setIsLanguageModalOpen(false)}
            className="w-full py-3.5 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:opacity-95 active:scale-[0.98] transition-all shadow-md min-h-[48px]"
            type="button"
          >
            {t("common.done")}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LanguageModal;
