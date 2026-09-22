import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const PmKisanDbtTrackingInstallmentStatusPage = () => {
  const navigate = useNavigate();
  const { t } = useApp();

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("tracker.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="flex items-center justify-between border-b border-border-warm-gray/30 pb-3">
            <h1 className="font-headline-sm text-base font-bold text-text-charcoal">
              {t("tracker.sub")}
            </h1>
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs font-bold">
              {t("common.active")}
            </span>
          </div>

          <div className="flex flex-col gap-3 pt-1">
            <div className="flex justify-between items-center text-xs border-b border-border-warm-gray/20 py-2">
              <span className="text-text-slate">Aadhaar Seeding Status</span>
              <span className="text-emerald-700 font-bold">{t("common.verified")} ✓</span>
            </div>
            <div className="flex justify-between items-center text-xs border-b border-border-warm-gray/20 py-2">
              <span className="text-text-slate">NPCI Mapper Status</span>
              <span className="text-emerald-700 font-bold">Active</span>
            </div>
            <div className="flex justify-between items-center text-xs py-2">
              <span className="text-text-slate">Next Installment</span>
              <span className="text-text-charcoal font-bold">Nov 2026</span>
            </div>
          </div>
        </section>

        <section className="flex flex-col gap-3">
          <button
            onClick={() => navigate('/dbt-error-remediation')}
            className="w-full py-3.5 rounded-full bg-surface-sand text-text-charcoal font-label-md text-sm font-semibold border border-border-warm-gray/50 hover:bg-surface-dim transition-all min-h-[48px]"
            type="button"
          >
            {t("tracker.remediationTitle")}
          </button>
          
          <button
            onClick={() => navigate('/dbt-receipt')}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            <span>{t("tracker.receiptTitle")}</span>
            <span className="material-symbols-outlined text-[20px]">receipt</span>
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default PmKisanDbtTrackingInstallmentStatusPage;
