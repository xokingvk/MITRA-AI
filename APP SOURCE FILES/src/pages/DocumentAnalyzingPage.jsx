import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { uploadDocument } from '../services/api';

export const DocumentAnalyzingPage = () => {
  const navigate = useNavigate();
  const { uploadedDoc, setAnalysisResult, t } = useApp();
  const [progress, setProgress] = useState(20);
  const [statusText, setStatusText] = useState("Connecting to MITRA AI server...");
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    if (!uploadedDoc) {
      navigate('/document-upload');
      return;
    }

    let isMounted = true;

    const performUpload = async () => {
      try {
        if (isMounted) {
          setProgress(40);
          setStatusText(`Uploading ${uploadedDoc.name} to server...`);
        }

        const backendResponse = await uploadDocument(uploadedDoc);

        if (!isMounted) return;

        setProgress(85);
        setStatusText("Parsing document text & session context...");

        setTimeout(() => {
          if (!isMounted) return;
          setProgress(100);
          setStatusText("Document processed successfully!");
          
          setAnalysisResult(backendResponse);
          navigate('/document-result');
        }, 500);

      } catch (err) {
        if (!isMounted) return;
        console.error("Document upload processing error:", err);
        setErrorMsg(err.message || "Failed to upload and process document on server.");
      }
    };

    performUpload();

    return () => {
      isMounted = false;
    };
  }, [uploadedDoc, navigate, setAnalysisResult]);

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("doc.analyzing")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5 items-center justify-center text-center">
        
        <div className="w-full bg-surface-warm-white rounded-3xl p-8 shadow-sm border border-border-warm-gray/40 flex flex-col items-center gap-5">
          {errorMsg ? (
            <>
              <div className="w-20 h-20 rounded-full bg-red-100 text-red-600 flex items-center justify-center">
                <span className="material-symbols-outlined text-[40px]">error</span>
              </div>
              <div className="flex flex-col gap-1">
                <h2 className="font-headline-sm text-lg font-bold text-red-950">
                  Document Upload Failed
                </h2>
                <p className="font-body-sm text-xs text-red-700 leading-relaxed max-w-xs">
                  {errorMsg}
                </p>
              </div>
              <button
                onClick={() => navigate('/document-upload')}
                className="mt-2 py-3 px-6 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary transition-all"
                type="button"
              >
                Try Uploading Again
              </button>
            </>
          ) : (
            <>
              <div className="w-20 h-20 rounded-full bg-secondary-container/30 text-secondary flex items-center justify-center animate-pulse">
                <span className="material-symbols-outlined text-[40px] animate-spin">document_scanner</span>
              </div>

              <div className="flex flex-col gap-1">
                <h2 className="font-headline-sm text-xl font-bold text-text-charcoal">
                  {t("doc.analyzing")}
                </h2>
                <p className="font-body-sm text-xs text-text-slate">
                  {statusText}
                </p>
              </div>

              <div className="w-full bg-surface-sand rounded-full h-2 overflow-hidden border border-border-warm-gray/30">
                <div 
                  className="bg-primary-container h-full rounded-full transition-all duration-500 ease-out" 
                  style={{ width: `${progress}%` }}
                />
              </div>

              <span className="font-label-sm text-xs font-semibold text-primary-container">
                {progress}% Completed
              </span>
            </>
          )}
        </div>

      </main>

      <BottomNav />
    </div>
  );
};

export default DocumentAnalyzingPage;
