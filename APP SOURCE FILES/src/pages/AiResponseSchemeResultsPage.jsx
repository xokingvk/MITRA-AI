import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { sendChatMessage } from '../services/api';

export const AiResponseSchemeResultsPage = () => {
  const navigate = useNavigate();
  const { spokenQuery, searchQuery, language, speakText, stopAudio, isPlayingAudio, t } = useApp();

  const queryToSearch = spokenQuery || searchQuery || '';
  const [loading, setLoading] = useState(false);
  const [responseResult, setResponseResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!queryToSearch) return;

    let isMounted = true;
    const fetchResponse = async () => {
      setLoading(true);
      setErrorMsg('');

      try {
        const result = await sendChatMessage(queryToSearch, language);
        if (isMounted) {
          setResponseResult(result);
          if (result && result.answer) {
            speakText(result.answer);
          }
        }
      } catch (err) {
        if (isMounted) {
          setErrorMsg(err.message || "Failed to retrieve response from MITRA AI server.");
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchResponse();

    return () => {
      isMounted = false;
    };
  }, [queryToSearch, language]);

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else if (responseResult?.answer) {
      speakText(responseResult.answer);
    }
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("results.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Spoken Query Header Pill */}
        <div className="w-full bg-surface-warm-white rounded-3xl p-4 shadow-sm flex items-center justify-between gap-3 border border-border-warm-gray/40">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-full bg-secondary text-on-secondary flex items-center justify-center flex-shrink-0">
              <span className="material-symbols-outlined text-[18px]">search</span>
            </div>
            <div className="min-w-0">
              <span className="font-label-sm text-[11px] text-text-slate block uppercase tracking-wider font-semibold">
                User Question
              </span>
              <p className="font-label-md text-xs font-bold text-text-charcoal truncate">
                "{queryToSearch || 'No question provided'}"
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate('/')}
            aria-label="New Question"
            className="p-2 rounded-full hover:bg-surface-sand text-secondary flex-shrink-0"
            type="button"
          >
            <span className="material-symbols-outlined text-[20px]">edit</span>
          </button>
        </div>

        {/* Audio Player Card */}
        {responseResult?.answer && (
          <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary-container/30 text-secondary flex items-center justify-center flex-shrink-0">
                <span className="material-symbols-outlined text-[22px]">volume_up</span>
              </div>
              <div className="min-w-0">
                <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                  Listen to Guidance Response
                </span>
                <span className="font-body-sm text-xs text-text-slate block">
                  Gemini synthesized audio
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
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-surface-warm-white rounded-3xl p-8 shadow-sm border border-border-warm-gray/40 flex flex-col items-center text-center gap-3">
            <span className="material-symbols-outlined text-[36px] text-primary-container animate-spin">sync</span>
            <p className="font-headline-sm text-sm font-bold text-text-charcoal">
              Searching Permanent Health Scheme Knowledge Base...
            </p>
            <p className="font-body-sm text-xs text-text-slate">
              Gemini is analyzing official scheme documentation.
            </p>
          </div>
        )}

        {errorMsg && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-900 rounded-2xl text-xs font-semibold">
            {errorMsg}
          </div>
        )}

        {/* Real Gemini Answer Result Section */}
        {responseResult && (
          <section className="flex flex-col gap-4">
            <div className="bg-surface-warm-white rounded-3xl p-6 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
              <div className="flex items-center gap-2 border-b border-border-warm-gray/30 pb-2.5">
                <span className="material-symbols-outlined text-secondary text-[22px]">smart_toy</span>
                <h3 className="font-headline-sm text-base font-bold text-text-charcoal">
                  MITRA AI Response
                </h3>
              </div>

              <div className="font-body-md text-sm text-text-charcoal leading-relaxed whitespace-pre-wrap">
                {responseResult.answer}
              </div>

              {responseResult.disclaimer && (
                <p className="text-[11px] text-text-slate italic pt-2 border-t border-border-warm-gray/20">
                  {responseResult.disclaimer}
                </p>
              )}
            </div>

            {/* Official Sources Card */}
            {responseResult.sources && responseResult.sources.length > 0 && (
              <div className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
                <h4 className="font-headline-sm text-xs font-bold text-text-charcoal uppercase tracking-wider">
                  Official Scheme Sources Used ({responseResult.sources.length})
                </h4>

                <div className="flex flex-col gap-2">
                  {responseResult.sources.map((src, idx) => (
                    <div key={idx} className="bg-surface-sand/60 p-3 rounded-2xl text-xs flex flex-col gap-1 border border-border-warm-gray/30">
                      <div className="flex justify-between items-center font-semibold text-primary-container">
                        <span>📄 {src.document || 'Health Schemes Document'}</span>
                        <span>Page {src.page}</span>
                      </div>
                      {src.snippet && (
                        <p className="text-[11px] text-text-slate leading-relaxed">
                          "{src.snippet}"
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

      </main>

      <BottomNav />
    </div>
  );
};

export default AiResponseSchemeResultsPage;
