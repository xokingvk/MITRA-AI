import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const DocumentUploadVerificationPage = () => {
  const navigate = useNavigate();
  const { setUploadedDoc, t } = useApp();
  const [analyzing, setAnalyzing] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setUploadedDoc(e.target.files[0]);
    }
  };

  const handleAnalyze = () => {
    setAnalyzing(true);
    setTimeout(() => {
      navigate('/document-analyzing');
    }, 800);
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("doc.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Step Indicator Header */}
        <div className="flex items-center justify-between pt-1">
          <span className="font-label-sm text-xs font-semibold text-secondary flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-container/30">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
            Step 2 of 3 • Document Upload
          </span>
        </div>

        <div className="flex flex-col gap-1">
          <h1 className="font-headline-sm text-xl font-bold text-text-charcoal">
            {t("doc.uploadDoc")}
          </h1>
          <p className="font-body-sm text-xs text-text-slate leading-relaxed">
            Upload Land Patta, Aadhaar, or Income Certificate. MITRA AI will analyze eligibility instantly.
          </p>
        </div>

        {/* Action Options: Camera, Gallery, Files */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-4">
          
          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-4 rounded-2xl bg-surface-sand/80 hover:bg-surface-sand active:bg-surface-dim border border-border-warm-gray/40 flex flex-col items-center justify-center gap-2 text-center transition-all min-h-[96px]"
              type="button"
            >
              <span className="material-symbols-outlined text-[32px] text-primary-container">photo_camera</span>
              <span className="font-label-sm text-xs font-semibold text-text-charcoal">{t("doc.camera")}</span>
            </button>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-4 rounded-2xl bg-surface-sand/80 hover:bg-surface-sand active:bg-surface-dim border border-border-warm-gray/40 flex flex-col items-center justify-center gap-2 text-center transition-all min-h-[96px]"
              type="button"
            >
              <span className="material-symbols-outlined text-[32px] text-secondary">image</span>
              <span className="font-label-sm text-xs font-semibold text-text-charcoal">{t("doc.gallery")}</span>
            </button>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-4 rounded-2xl bg-surface-sand/80 hover:bg-surface-sand active:bg-surface-dim border border-border-warm-gray/40 flex flex-col items-center justify-center gap-2 text-center transition-all min-h-[96px]"
              type="button"
            >
              <span className="material-symbols-outlined text-[32px] text-tertiary">folder</span>
              <span className="font-label-sm text-xs font-semibold text-text-charcoal">{t("doc.files")}</span>
            </button>
          </div>

          <div
            onClick={() => fileInputRef.current?.click()}
            className="w-full border-2 border-dashed border-border-warm-gray rounded-2xl p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:border-primary-container transition-colors bg-surface-sand/30"
          >
            <span className="material-symbols-outlined text-[36px] text-text-slate mb-2">cloud_upload</span>
            <span className="font-label-md text-sm font-semibold text-text-charcoal">
              {t("doc.chooseFile")}
            </span>
            <span className="font-body-sm text-xs text-text-slate mt-1">
              Supports PDF, PNG, JPG (Max 10MB)
            </span>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,image/*"
            onChange={handleFileChange}
            className="hidden"
          />

          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            {analyzing ? (
              <>
                <span className="material-symbols-outlined text-[20px] animate-spin">sync</span>
                <span>{t("doc.analyzing")}</span>
              </>
            ) : (
              <>
                <span>{t("doc.analyzing")}</span>
                <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
              </>
            )}
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default DocumentUploadVerificationPage;
