import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const MyEnrolledSchemes2000CreditedPage = () => {
  const navigate = useNavigate();
  const { t } = useApp();

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("tracker.installment16")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        <section className="bg-emerald-50 border border-emerald-200 rounded-3xl p-6 shadow-sm flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
            <span className="material-symbols-outlined text-[32px]">check_circle</span>
          </div>
          <div className="min-w-0">
            <span className="font-label-sm text-xs font-bold text-emerald-800 uppercase tracking-wider block">
              {t("common.credited")}
            </span>
            <h1 className="font-headline-lg text-2xl font-bold text-emerald-950 mt-0.5">
              ₹2,000 Credited
            </h1>
            <p className="font-body-sm text-xs text-emerald-800 mt-0.5">
              {t("tracker.installment16Sub")}
            </p>
          </div>
        </section>

        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3 text-xs">
          <div className="flex justify-between items-center py-2 border-b border-border-warm-gray/20">
            <span className="text-text-slate">Scheme Name</span>
            <span className="font-bold text-text-charcoal">{t("schemes.pmKisan.title")}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-border-warm-gray/20">
            <span className="text-text-slate">Amount</span>
            <span className="font-bold text-emerald-700">₹2,000.00</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-border-warm-gray/20">
            <span className="text-text-slate">Transaction Ref</span>
            <span className="font-mono font-bold text-text-charcoal">UTR-940284019</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-text-slate">Bank Account</span>
            <span className="font-bold text-text-charcoal">SBI A/C ****4091</span>
          </div>
        </section>

        <button
          onClick={() => navigate('/dbt-receipt')}
          className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
          type="button"
        >
          <span>{t("tracker.receiptTitle")}</span>
          <span className="material-symbols-outlined text-[20px]">receipt</span>
        </button>

      </main>

      <BottomNav />
    </div>
  );
};

export default MyEnrolledSchemes2000CreditedPage;
