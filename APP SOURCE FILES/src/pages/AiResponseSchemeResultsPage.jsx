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
  const [expandedSchemeIdx, setExpandedSchemeIdx] = useState(null);

  // Derive short spoken text for TTS
  const getShortVoiceText = (result) => {
    if (!result) return "";
    if (result.voice_answer && result.voice_answer.trim()) {
      return result.voice_answer.trim();
    }
    const count = result.matched_schemes?.length || 0;
    if (count > 0) {
      return `I found ${count} scheme${count > 1 ? 's' : ''} that may be relevant to you. You can see them on the screen.`;
    }
    const firstPart = (result.answer || "").split("\n\n")[0].split(". ")[0];
    return firstPart ? (firstPart.endsWith(".") ? firstPart : `${firstPart}.`) : "Here is the information you requested.";
  };

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
          // Play ONLY short voice response, NOT long scheme paragraphs
          const shortVoice = getShortVoiceText(result);
          if (shortVoice) {
            speakText(shortVoice);
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
      stopAudio();
    };
  }, [queryToSearch, language]);

  const toggleAudio = () => {
    if (isPlayingAudio) {
      stopAudio();
    } else if (responseResult) {
      const shortVoice = getShortVoiceText(responseResult);
      speakText(shortVoice);
    }
  };

  const toggleSchemeExpand = (idx) => {
    setExpandedSchemeIdx(prev => prev === idx ? null : idx);
  };

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("results.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-4">
        
        {/* Spoken Query Header Pill */}
        <div className="w-full bg-surface-warm-white rounded-3xl p-4 shadow-sm flex items-center justify-between gap-3 border border-border-warm-gray/40">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-full bg-secondary text-on-secondary flex items-center justify-center flex-shrink-0 shadow-sm">
              <span className="material-symbols-outlined text-[18px]">search</span>
            </div>
            <div className="min-w-0">
              <span className="font-label-sm text-[11px] text-text-slate block uppercase tracking-wider font-semibold">
                Your Question
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

        {/* Audio Player Card (Speaks Short Voice Summary Only) */}
        {responseResult && (
          <section className="bg-surface-warm-white rounded-3xl p-4 shadow-sm border border-border-warm-gray/40 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-secondary-container/30 text-secondary flex items-center justify-center flex-shrink-0">
                <span className="material-symbols-outlined text-[22px]">volume_up</span>
              </div>
              <div className="min-w-0">
                <span className="font-label-md text-sm font-semibold text-text-charcoal block">
                  Voice Summary
                </span>
                <span className="font-body-sm text-xs text-text-slate block">
                  {isPlayingAudio ? "Playing voice summary..." : "Listen to concise summary"}
                </span>
              </div>
            </div>
            <button
              onClick={toggleAudio}
              className="w-10 h-10 rounded-full bg-primary-container text-on-primary flex items-center justify-center flex-shrink-0 active:scale-95 transition-transform shadow-sm"
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
              Searching Health Scheme Knowledge Base...
            </p>
            <p className="font-body-sm text-xs text-text-slate">
              Gemini is evaluating relevant health welfare programs.
            </p>
          </div>
        )}

        {errorMsg && (
          <div className="p-4 bg-red-50 border border-red-200 text-red-900 rounded-2xl text-xs font-semibold">
            {errorMsg}
          </div>
        )}

        {/* Short, Simple Gemini Introductory Answer */}
        {responseResult && (
          <section className="flex flex-col gap-4">
            <div className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-2.5">
              <div className="flex items-center gap-2 border-b border-border-warm-gray/20 pb-2">
                <span className="material-symbols-outlined text-secondary text-[20px]">smart_toy</span>
                <h3 className="font-headline-sm text-sm font-bold text-text-charcoal">
                  MITRA AI Guidance
                </h3>
              </div>

              <div className="font-body-md text-sm text-text-charcoal leading-relaxed whitespace-pre-wrap">
                {responseResult.answer}
              </div>
            </div>

            {/* Information Needed for Complete Verification Callout */}
            {responseResult.needs_more_information && responseResult.needs_more_information.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-3xl p-4 flex flex-col gap-1.5 shadow-sm">
                <div className="flex items-center gap-2 text-amber-900 font-bold text-xs">
                  <span className="material-symbols-outlined text-[18px]">info</span>
                  <span>Additional Information for Exact Eligibility:</span>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {responseResult.needs_more_information.map((info, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded-full bg-white border border-amber-300 text-amber-900 text-[11px] font-semibold">
                      {info}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Structured Scheme Cards */}
            {responseResult.matched_schemes && responseResult.matched_schemes.length > 0 && (
              <section className="flex flex-col gap-3">
                <div className="flex items-center justify-between px-1">
                  <h3 className="font-headline-sm text-sm font-bold text-text-charcoal flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-emerald-600 text-[18px]">verified</span>
                    <span>Potentially Relevant Schemes ({responseResult.matched_schemes.length})</span>
                  </h3>
                </div>

                <div className="flex flex-col gap-3">
                  {responseResult.matched_schemes.map((scheme, idx) => {
                    const isExpanded = expandedSchemeIdx === idx;
                    return (
                      <div
                        key={idx}
                        className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3 transition-all"
                      >
                        {/* Card Header: Scheme Name & Relevance Reason */}
                        <div className="flex flex-col gap-1">
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="font-headline-sm text-sm font-bold text-text-charcoal">
                              {scheme.name}
                            </h4>
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 whitespace-nowrap flex-shrink-0">
                              May be relevant
                            </span>
                          </div>

                          <p className="font-body-sm text-xs text-text-charcoal leading-relaxed">
                            {scheme.short_description}
                          </p>

                          {scheme.reason && (
                            <div className="flex items-center gap-1 text-[11px] text-secondary font-medium mt-0.5">
                              <span className="material-symbols-outlined text-[14px]">lightbulb</span>
                              <span>{scheme.reason}</span>
                            </div>
                          )}
                        </div>

                        {/* View Details Toggle Button */}
                        <button
                          onClick={() => toggleSchemeExpand(idx)}
                          className="w-full py-2.5 px-4 rounded-xl bg-surface-sand/80 hover:bg-surface-sand active:bg-surface-dim text-text-charcoal text-xs font-semibold flex items-center justify-between transition-colors border border-border-warm-gray/30"
                          type="button"
                        >
                          <span className="flex items-center gap-1.5">
                            <span className="material-symbols-outlined text-[16px] text-primary-container">info</span>
                            <span>{isExpanded ? 'Hide Details' : 'View Details'}</span>
                          </span>
                          <span className="material-symbols-outlined text-[18px] text-text-slate transition-transform duration-200" style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}>
                            expand_more
                          </span>
                        </button>

                        {/* Expandable Scheme Details (Eligibility, Benefits, Documents) */}
                        {isExpanded && (
                          <div className="pt-2 border-t border-border-warm-gray/30 flex flex-col gap-3 animate-fadeIn text-xs">
                            {scheme.eligibility && (
                              <div className="bg-surface-sand/50 p-3 rounded-2xl">
                                <span className="font-bold text-text-charcoal block mb-0.5">Eligibility Criteria:</span>
                                <span className="text-text-slate leading-relaxed">{scheme.eligibility}</span>
                              </div>
                            )}

                            {scheme.benefits && (
                              <div className="bg-emerald-50/60 border border-emerald-100 p-3 rounded-2xl">
                                <span className="font-bold text-emerald-950 block mb-0.5">Key Benefits:</span>
                                <span className="text-emerald-900 leading-relaxed">{scheme.benefits}</span>
                              </div>
                            )}

                            {scheme.documents && scheme.documents.length > 0 && (
                              <div className="flex flex-col gap-1.5">
                                <span className="font-bold text-text-charcoal">Required Documents:</span>
                                <div className="flex flex-wrap gap-1.5">
                                  {scheme.documents.map((doc, dIdx) => (
                                    <span key={dIdx} className="px-2.5 py-1 rounded-lg bg-surface-sand text-text-slate text-[11px] font-medium border border-border-warm-gray/30">
                                      📄 {doc}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            <div className="p-2.5 bg-amber-50/70 border border-amber-200/60 rounded-xl text-[11px] text-amber-900 leading-relaxed">
                              ℹ️ Final eligibility is verified at official government health portals or your local primary health center (PHC/CHC).
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* Official Sources Card */}
            {responseResult.sources && responseResult.sources.length > 0 && (
              <div className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-2.5">
                <h4 className="font-headline-sm text-xs font-bold text-text-charcoal uppercase tracking-wider">
                  Official Scheme Sources ({responseResult.sources.length})
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

            {responseResult.disclaimer && (
              <p className="text-[11px] text-text-slate italic px-2">
                {responseResult.disclaimer}
              </p>
            )}
          </section>
        )}

      </main>

      <BottomNav />
    </div>
  );
};

export default AiResponseSchemeResultsPage;
