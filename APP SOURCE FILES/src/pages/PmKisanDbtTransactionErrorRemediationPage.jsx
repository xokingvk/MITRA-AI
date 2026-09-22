import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const PmKisanDbtTransactionErrorRemediationPage = () => {
  const navigate = useNavigate();
  const { t } = useApp();

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("tracker.remediationTitle")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        <section className="bg-emerald-50 border border-emerald-200 rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
            <span className="material-symbols-outlined text-[28px]">build_circle</span>
          </div>
          <div className="min-w-0">
            <h2 className="font-headline-sm text-base font-bold text-emerald-950">
              {t("tracker.remediationTitle")}
            </h2>
            <p className="font-body-sm text-xs text-emerald-800 mt-0.5">
              {t("tracker.remediationSub")}
            </p>
          </div>
        </section>

        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3 text-xs">
          <div className="flex justify-between items-center py-2 border-b border-border-warm-gray/20">
            <span className="text-text-slate">Previous Error</span>
            <span className="text-rose-700 font-bold">Aadhaar Not Seeded</span>
          </div>
          <div className="flex justify-between items-center py-2 text-xs">
            <span className="text-text-slate">Current Status</span>
            <span className="text-emerald-700 font-bold">{t("common.verified")} ✓</span>
          </div>
        </section>

        <button
          onClick={() => navigate('/dbt-tracker')}
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

export default PmKisanDbtTransactionErrorRemediationPage;
