import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';

export const Header = ({ title, showBack = false }) => {
  const navigate = useNavigate();
  const { language, setIsLanguageModalOpen, t } = useApp();

  const getLanguageNativeLabel = (code) => {
    return t(`lang.${code.toLowerCase()}`);
  };

  const pageTitle = title || t("header.title");

  return (
    <header className="fixed top-0 left-0 right-0 z-50 pt-safe bg-surface-warm-white/95 backdrop-blur-xl shadow-[0_1px_8px_rgba(73,53,72,0.06)] border-b border-border-warm-gray/30">
      <div className="max-w-md mx-auto h-16 px-gutter flex items-center justify-between gap-space-sm">
        <div className="flex items-center gap-space-sm min-w-0">
          {showBack ? (
            <button
              onClick={() => navigate(-1)}
              aria-label={t("common.back")}
              className="min-h-[48px] min-w-[48px] flex items-center justify-center rounded-full hover:bg-surface-container active:bg-surface-dim transition-colors text-primary-container -ml-2"
              type="button"
            >
              <span className="material-symbols-outlined text-[24px]">arrow_back</span>
            </button>
          ) : (
            <button 
              onClick={() => navigate('/')} 
              className="flex items-center gap-space-sm text-left focus:outline-none"
              type="button"
            >
              <img
                alt="MITRA AI Logo"
                className="h-8 w-auto object-contain"
                src="https://lh3.googleusercontent.com/aida/AEtjO1U1x0cG93KNoW-ggmST5HBPp7vZ1bkZw9pvyluhxuVet-04cPE_WhQMk9u8bUdNARM2W0SMxXatFDbbh-mmqcYooHuSNUkT89URL4ea6RqThqyUlS5jyeOL2v4WToLAVXs9NOlu2nxJxKsEv5UPEkkMTCDHEpWH0_C9hXiLhLFNJRvDWreu76zo782vmWT6-EIFohLLB-qiepShFYHGCa5dZyqfzz2lqZhLUJt4Dgcc8SrSF97ltmflg2Y"
              />
            </button>
          )}

          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-space-xs">
              <span 
                onClick={() => navigate('/')} 
                className="font-headline-sm text-headline-sm text-primary-container tracking-tight truncate cursor-pointer"
              >
                MITRA AI
              </span>
            </div>
            <span className="font-label-sm text-label-sm text-text-slate truncate">{pageTitle}</span>
          </div>
        </div>

        <div className="flex items-center gap-space-xs flex-shrink-0">
          <button
            onClick={() => setIsLanguageModalOpen(true)}
            aria-label={t("settings.language")}
            className="h-10 px-3 rounded-full bg-surface-sand text-text-charcoal flex items-center gap-1.5 active:bg-surface-dim transition-colors border border-border-warm-gray/40 shadow-sm"
            type="button"
          >
            <span className="material-symbols-outlined text-[18px] text-primary-container">language</span>
            <span className="font-label-sm text-[12px] font-semibold text-primary-container">{getLanguageNativeLabel(language)}</span>
          </button>
          
          <button
            onClick={() => navigate('/settings')}
            aria-label={t("nav.settings")}
            className="w-10 h-10 rounded-full bg-primary-container text-on-primary flex items-center justify-center hover:opacity-90 active:scale-95 transition-all shadow-sm"
            type="button"
          >
            <span className="material-symbols-outlined text-[20px]">settings</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
