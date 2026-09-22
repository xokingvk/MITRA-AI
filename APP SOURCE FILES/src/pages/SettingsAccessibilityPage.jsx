import React from 'react';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { LanguageModal } from '../components/layout/LanguageModal';
import { useApp } from '../context/AppContext';

export default function SettingsAccessibilityPage() {
  const {
    userProfile,
    language,
    t,
    setIsLanguageModalOpen,
    accessibility,
    setAccessibility
  } = useApp();

  const toggleLargeText = () => {
    setAccessibility((prev) => ({
      ...prev,
      largeText: !prev.largeText
    }));
  };

  const toggleHighContrast = () => {
    setAccessibility((prev) => ({
      ...prev,
      highContrast: !prev.highContrast
    }));
  };

  const toggleVoiceSpeed = () => {
    setAccessibility((prev) => ({
      ...prev,
      voiceSpeed: prev.voiceSpeed === 'Normal' ? 'Slow' : 'Normal'
    }));
  };

  const getLangNativeName = (code) => {
    return t(`lang.${(code || 'en').toLowerCase()}`);
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("settings.title")} />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Profile Card */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-bold text-xl flex-shrink-0 shadow-md">
              {userProfile.name.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <h2 className="font-headline-sm text-lg font-bold text-text-charcoal truncate">
                  {userProfile.name}
                </h2>
                <span className="bg-emerald-100 text-emerald-800 text-[11px] font-bold px-2.5 py-0.5 rounded-full flex-shrink-0 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                  {t("common.verified")}
                </span>
              </div>
              <p className="font-body-sm text-xs text-text-slate truncate mt-0.5">
                {userProfile.mobile} • {userProfile.village}, {userProfile.district}
              </p>
              <p className="font-mono text-[11px] text-text-slate mt-0.5">
                Aadhaar: {userProfile.aadhaarMasked}
              </p>
            </div>
          </div>
        </section>

        {/* SECTION 1: Language Switcher */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-container text-[24px]">language</span>
            <h3 className="font-headline-sm text-base font-bold text-text-charcoal">
              {t("settings.language")}
            </h3>
          </div>

          <div className="flex items-center justify-between p-3.5 bg-surface-sand/80 rounded-2xl border border-border-warm-gray/30">
            <div>
              <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                {getLangNativeName(language)}
              </span>
              <span className="font-body-sm text-xs text-text-slate block mt-0.5">
                {t("settings.languageSub")}
              </span>
            </div>
            <button
              onClick={() => setIsLanguageModalOpen(true)}
              className="px-4 py-2 rounded-full bg-primary-container text-on-primary font-label-sm text-xs font-semibold hover:bg-primary active:scale-95 transition-all shadow-sm min-h-[40px]"
              type="button"
            >
              {t("common.change")}
            </button>
          </div>
        </section>

        {/* SECTION 2: Accessibility Options */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-container text-[24px]">accessibility_new</span>
            <h3 className="font-headline-sm text-base font-bold text-text-charcoal">
              {t("settings.accessibility")}
            </h3>
          </div>

          <div className="flex flex-col gap-3">
            {/* Large Text Mode Toggle */}
            <div className="flex items-center justify-between p-3.5 bg-surface-sand/60 rounded-2xl border border-border-warm-gray/30">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-text-slate text-[22px]">text_fields</span>
                <div>
                  <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                    {t("settings.largeText")}
                  </span>
                  <span className="font-body-sm text-xs text-text-slate block">
                    {t("settings.largeTextSub")}
                  </span>
                </div>
              </div>
              <button
                onClick={toggleLargeText}
                className={`w-12 h-7 rounded-full p-1 transition-colors duration-200 focus:outline-none ${
                  accessibility.largeText ? 'bg-primary-container' : 'bg-surface-dim'
                }`}
                type="button"
                aria-label={t("settings.largeText")}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-surface-warm-white shadow-md transform transition-transform duration-200 ${
                    accessibility.largeText ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            {/* High Contrast Mode Toggle */}
            <div className="flex items-center justify-between p-3.5 bg-surface-sand/60 rounded-2xl border border-border-warm-gray/30">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-text-slate text-[22px]">contrast</span>
                <div>
                  <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                    {t("settings.highContrast")}
                  </span>
                  <span className="font-body-sm text-xs text-text-slate block">
                    {t("settings.highContrastSub")}
                  </span>
                </div>
              </div>
              <button
                onClick={toggleHighContrast}
                className={`w-12 h-7 rounded-full p-1 transition-colors duration-200 focus:outline-none ${
                  accessibility.highContrast ? 'bg-primary-container' : 'bg-surface-dim'
                }`}
                type="button"
                aria-label={t("settings.highContrast")}
              >
                <div
                  className={`w-5 h-5 rounded-full bg-surface-warm-white shadow-md transform transition-transform duration-200 ${
                    accessibility.highContrast ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            {/* Voice Speed Toggle */}
            <div className="flex items-center justify-between p-3.5 bg-surface-sand/60 rounded-2xl border border-border-warm-gray/30">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-text-slate text-[22px]">speed</span>
                <div>
                  <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                    {t("settings.voiceSpeed")}
                  </span>
                  <span className="font-body-sm text-xs text-text-slate block">
                    {accessibility.voiceSpeed}
                  </span>
                </div>
              </div>
              <button
                onClick={toggleVoiceSpeed}
                className="px-3 py-1.5 rounded-full bg-surface-sand text-primary-container border border-border-warm-gray/50 font-label-sm text-xs font-semibold active:bg-surface-dim transition-colors"
                type="button"
              >
                {accessibility.voiceSpeed}
              </button>
            </div>
          </div>
        </section>

        {/* SECTION 3: Additional Links */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-primary-container text-[24px]">info</span>
            <h3 className="font-headline-sm text-base font-bold text-text-charcoal">
              {t("settings.about")}
            </h3>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between p-3 bg-surface-sand/50 rounded-xl">
              <span className="font-label-md text-sm text-text-charcoal">{t("settings.help")}</span>
              <span className="font-label-sm text-xs text-text-slate font-mono">1800-11-1555</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-sand/50 rounded-xl">
              <span className="font-label-md text-sm text-text-charcoal">{t("settings.privacy")}</span>
              <span className="font-label-sm text-xs text-emerald-700 font-medium">{t("common.secured")}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-surface-sand/50 rounded-xl">
              <span className="font-label-md text-sm text-text-charcoal">{t("common.version")}</span>
              <span className="font-mono text-xs text-text-slate">v2.4.0 (Stitch)</span>
            </div>
          </div>
        </section>

      </main>

      <LanguageModal />
      <BottomNav />
    </div>
  );
}
