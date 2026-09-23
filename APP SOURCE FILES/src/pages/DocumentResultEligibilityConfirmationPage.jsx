import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const DocumentResultEligibilityConfirmationPage = () => {
  const navigate = useNavigate();
  const { analysisResult, speakText, isPlayingAudio, stopAudio, t } = useApp();

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else {
      const summaryText = analysisResult 
        ? `Uploaded file ${analysisResult.filename} was successfully processed into session context.`
        : t("doc.speechVerified");
      speakText(summaryText);
    }
  };

  if (!analysisResult) {
    return (
      <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
        <Header title={t("doc.title")} showBack />
        <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5 items-center justify-center text-center">
          <div className="bg-surface-warm-white rounded-3xl p-6 shadow-sm border border-border-warm-gray/40 flex flex-col items-center gap-4 w-full">
            <span className="material-symbols-outlined text-[48px] text-text-slate">upload_file</span>
            <h2 className="font-headline-sm text-lg font-bold text-text-charcoal">No Document Uploaded Yet</h2>
            <p className="font-body-sm text-xs text-text-slate">Please select and upload a supporting document to view real analysis details.</p>
            <button
              onClick={() => navigate('/document-upload')}
              className="py-3 px-6 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary transition-all shadow-md"
              type="button"
            >
              Upload Document
            </button>
          </div>
        </main>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("doc.docReady")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Verification Success Header */}
        <section className="bg-emerald-50 border border-emerald-200 rounded-3xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
            <span className="material-symbols-outlined text-[28px]">check_circle</span>
          </div>
          <div className="min-w-0">
            <h2 className="font-headline-sm text-base font-bold text-emerald-950">
              {t("doc.docReady")} • {t("common.verified")}
            </h2>
            <p className="font-body-sm text-xs text-emerald-800 mt-0.5">
              {analysisResult.filename} • Session Context Active
            </p>
          </div>
        </section>

        {/* Audio Summary Card */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-secondary-container/30 text-secondary flex items-center justify-center flex-shrink-0">
              <span className="material-symbols-outlined text-[22px]">volume_up</span>
            </div>
            <div className="min-w-0">
              <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                {t("common.listen")}
              </span>
              <span className="font-body-sm text-xs text-text-slate block">
                Listen to document upload confirmation
              </span>
            </div>
          </div>
          <button
            onClick={toggleAudio}
            className="w-10 h-10 rounded-full bg-primary-container text-on-primary flex items-center justify-center flex-shrink-0 active:scale-95 transition-transform"
            type="button"
          >
            <span className="material-symbols-outlined text-[20px]">
              {isPlayingAudio ? 'stop' : 'play_arrow'}
            </span>
          </button>
        </section>

        {/* Real Extracted Document Details from Backend */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <h3 className="font-headline-sm text-sm font-bold text-text-charcoal uppercase tracking-wider">
            Server Document Analysis
          </h3>

          <div className="flex flex-col gap-2.5 pt-1">
            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20 text-xs">
              <span className="text-text-slate font-medium">Filename</span>
              <span className="text-text-charcoal font-semibold truncate max-w-[200px]">{analysisResult.filename}</span>
            </div>

            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20 text-xs">
              <span className="text-text-slate font-medium">Document ID</span>
              <span className="text-text-charcoal font-semibold font-mono text-[11px] truncate max-w-[180px]">{analysisResult.document_id}</span>
            </div>

            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20 text-xs">
              <span className="text-text-slate font-medium">Pages Extracted</span>
              <span className="text-text-charcoal font-semibold">{analysisResult.pages_extracted} Page(s)</span>
            </div>

            <div className="flex justify-between items-center py-1.5 border-b border-border-warm-gray/20 text-xs">
              <span className="text-text-slate font-medium">Text Chunks</span>
              <span className="text-text-charcoal font-semibold">{analysisResult.chunks_count} Chunk(s)</span>
            </div>

            <div className="flex flex-col gap-1 py-1.5 border-b border-border-warm-gray/20 text-xs">
              <span className="text-text-slate font-medium">Status</span>
              <span className="text-emerald-800 font-semibold bg-emerald-50 p-2 rounded-xl border border-emerald-200">{analysisResult.message}</span>
            </div>

            {analysisResult.extracted_preview && (
              <div className="flex flex-col gap-1 pt-1 text-xs">
                <span className="text-text-slate font-medium">Extracted Text Preview:</span>
                <p className="bg-surface-sand/70 p-3 rounded-xl font-mono text-[11px] text-text-charcoal leading-relaxed max-h-36 overflow-y-auto border border-border-warm-gray/30">
                  {analysisResult.extracted_preview}
                </p>
              </div>
            )}
          </div>
        </section>

        {/* Next Action Buttons */}
        <section className="flex flex-col gap-3">
          <button
            onClick={() => navigate('/active-voice')}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            <span>Ask AI About Scheme Eligibility</span>
            <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
          </button>

          <button
            onClick={() => navigate('/document-upload')}
            className="w-full py-3.5 rounded-full bg-surface-sand text-text-charcoal font-label-md text-sm font-semibold border border-border-warm-gray/50 hover:bg-surface-dim active:scale-[0.98] transition-all min-h-[48px]"
            type="button"
          >
            Upload Another Document
          </button>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default DocumentResultEligibilityConfirmationPage;
