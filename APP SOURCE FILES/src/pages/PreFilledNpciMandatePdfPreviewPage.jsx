import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const PreFilledNpciMandatePdfPreviewPage = () => {
  const navigate = useNavigate();
  const { userProfile, t } = useApp();

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("kyc.previewMandate")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        <div className="flex flex-col gap-1 pt-1">
          <h1 className="font-headline-sm text-xl font-bold text-text-charcoal">
            {t("kyc.previewMandate")}
          </h1>
          <p className="font-body-sm text-xs text-text-slate">
            Pre-filled NPCI Mandate Form for Aadhaar Bank Seeding
          </p>
        </div>

        {/* PDF Preview Card */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-border-warm-gray/30 pb-3">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-rose-600 text-[24px]">picture_as_pdf</span>
              <span className="font-label-md text-sm font-bold text-text-charcoal">
                NPCI_Mandate_Seeding.pdf
              </span>
            </div>
            <span className="px-2 py-0.5 rounded bg-surface-sand text-[11px] font-mono text-text-slate">
              248 KB
            </span>
          </div>

          <div className="bg-surface-sand/50 p-4 rounded-2xl border border-border-warm-gray/30 flex flex-col gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-text-slate">Applicant Name:</span>
              <span className="font-semibold text-text-charcoal">{userProfile.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-slate">Aadhaar Number:</span>
              <span className="font-mono font-semibold text-text-charcoal">{userProfile.aadhaarMasked}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-slate">Bank Account:</span>
              <span className="font-semibold text-text-charcoal">{userProfile.linkedBank}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
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

        {/* Action Button */}
        <button
          onClick={() => navigate('/kyc/bank-acknowledgement')}
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

export default PreFilledNpciMandatePdfPreviewPage;
