import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const MyEnrolledSchemesBenefitsTrackerPage = () => {
  const navigate = useNavigate();
  const { t } = useApp();

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("tracker.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Total Credited Summary */}
        <section className="bg-primary-container text-on-primary rounded-3xl p-6 shadow-md flex flex-col gap-2">
          <span className="font-label-sm text-xs font-semibold opacity-90">
            {t("tracker.totalCredited")}
          </span>
          <h1 className="font-headline-lg text-3xl font-bold tracking-tight">
            {t("tracker.totalAmount")}
          </h1>
          <span className="font-body-sm text-xs opacity-80 mt-1">
            {t("tracker.sub")}
          </span>
        </section>

        {/* Installment Items */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-border-warm-gray/30 pb-3">
            <h2 className="font-headline-sm text-base font-bold text-text-charcoal">
              Installment History
            </h2>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold">
              {t("kyc.npciSeeded")}
            </span>
          </div>

          <div className="flex flex-col gap-3">
            <div 
              onClick={() => navigate('/my-schemes/credited')}
              className="p-4 rounded-2xl bg-surface-sand/60 hover:bg-surface-sand border border-border-warm-gray/30 flex items-center justify-between cursor-pointer transition-all"
            >
              <div>
                <span className="font-label-md text-sm font-bold text-text-charcoal block">
                  {t("tracker.installment16")}
                </span>
                <span className="font-body-sm text-xs text-text-slate block mt-0.5">
                  {t("tracker.installment16Sub")}
                </span>
              </div>
              <span className="material-symbols-outlined text-emerald-600 text-[22px]">check_circle</span>
            </div>

            <div 
              onClick={() => navigate('/dbt-tracker')}
              className="p-4 rounded-2xl bg-surface-sand/60 hover:bg-surface-sand border border-border-warm-gray/30 flex items-center justify-between cursor-pointer transition-all"
            >
              <div>
                <span className="font-label-md text-sm font-bold text-text-charcoal block">
                  {t("tracker.installment17")}
                </span>
                <span className="font-body-sm text-xs text-text-slate block mt-0.5">
                  {t("tracker.installment17Sub")}
                </span>
              </div>
              <span className="material-symbols-outlined text-amber-600 text-[22px]">schedule</span>
            </div>
          </div>
        </section>

        {/* Actions */}
        <section className="flex flex-col gap-3">
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

export default MyEnrolledSchemesBenefitsTrackerPage;
