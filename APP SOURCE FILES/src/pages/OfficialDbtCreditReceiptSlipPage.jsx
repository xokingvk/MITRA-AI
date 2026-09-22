import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const OfficialDbtCreditReceiptSlipPage = () => {
  const navigate = useNavigate();
  const { userProfile, t } = useApp();

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("tracker.receiptTitle")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-border-warm-gray/30 pb-3">
            <h1 className="font-headline-sm text-base font-bold text-text-charcoal">
              {t("tracker.receiptTitle")}
            </h1>
            <span className="px-2.5 py-0.5 rounded bg-emerald-100 text-emerald-800 text-xs font-bold">
              {t("common.verified")}
            </span>
          </div>

          <div className="flex flex-col gap-2.5 text-xs">
            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20">
              <span className="text-text-slate">Beneficiary</span>
              <span className="font-bold text-text-charcoal">{userProfile.name}</span>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20">
              <span className="text-text-slate">Scheme</span>
              <span className="font-bold text-text-charcoal">{t("schemes.pmKisan.title")}</span>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20">
              <span className="text-text-slate">Amount Credited</span>
              <span className="font-bold text-emerald-700">₹2,000.00</span>
            </div>
            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20">
              <span className="text-text-slate">Bank Account</span>
              <span className="font-bold text-text-charcoal">{userProfile.linkedBank}</span>
            </div>
            <div className="flex justify-between items-center py-1.5">
              <span className="text-text-slate">Date</span>
              <span className="font-bold text-text-charcoal">15 Aug 2026</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <button
              onClick={() => alert(t("common.download"))}
              className="py-3 rounded-2xl bg-surface-sand text-text-charcoal font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors border border-border-warm-gray/40 flex items-center justify-center gap-1.5 min-h-[44px]"
              type="button"
            >
              <span className="material-symbols-outlined text-[18px]">download</span>
              <span>{t("common.download")}</span>
            </button>
            <button
              onClick={() => alert(t("common.print"))}
              className="py-3 rounded-2xl bg-surface-sand text-text-charcoal font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors border border-border-warm-gray/40 flex items-center justify-center gap-1.5 min-h-[44px]"
              type="button"
            >
              <span className="material-symbols-outlined text-[18px]">print</span>
              <span>{t("common.print")}</span>
            </button>
          </div>
        </section>

        <button
          onClick={() => navigate('/my-schemes')}
          className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
          type="button"
        >
          <span>{t("common.done")}</span>
          <span className="material-symbols-outlined text-[20px]">check</span>
        </button>

      </main>

      <BottomNav />
    </div>
  );
};

export default OfficialDbtCreditReceiptSlipPage;
