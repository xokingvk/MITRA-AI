import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';

export const DocumentAnalyzingPage = () => {
  const navigate = useNavigate();
  const { t } = useApp();
  const [progress, setProgress] = useState(30);

  useEffect(() => {
    const timer1 = setTimeout(() => setProgress(65), 700);
    const timer2 = setTimeout(() => setProgress(95), 1400);

    const navTimer = setTimeout(() => {
      navigate('/document-result');
    }, 2000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(navTimer);
    };
  }, [navigate]);

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("doc.analyzing")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5 items-center justify-center text-center">
        
        <div className="w-full bg-surface-warm-white rounded-3xl p-8 shadow-sm border border-border-warm-gray/40 flex flex-col items-center gap-5">
          <div className="w-20 h-20 rounded-full bg-secondary-container/30 text-secondary flex items-center justify-center animate-pulse">
            <span className="material-symbols-outlined text-[40px] animate-spin">document_scanner</span>
          </div>

          <div className="flex flex-col gap-1">
            <h2 className="font-headline-sm text-xl font-bold text-text-charcoal">
              {t("doc.analyzing")}
            </h2>
            <p className="font-body-sm text-xs text-text-slate">
              Extracting Patta land size, survey number, and owner details...
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
        </div>

      </main>

      <BottomNav />
    </div>
  );
};

export default DocumentAnalyzingPage;
