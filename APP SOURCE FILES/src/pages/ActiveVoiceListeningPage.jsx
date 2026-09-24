import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Header } from '../components/layout/Header';
import { BottomNav } from '../components/layout/BottomNav';
import { voiceService } from '../services/voiceService';
import { sendChatMessage } from '../services/api';

export const ActiveVoiceListeningPage = () => {
  const navigate = useNavigate();
  const { 
    spokenQuery, 
    setSpokenQuery, 
    setSearchQuery, 
    speakText,
    language,
    t 
  } = useApp();

  // Turn-based states: 'idle' | 'recording' | 'transcribing' | 'thinking' | 'speaking' | 'error'
  const [voiceState, setVoiceState] = useState('idle');
  const [uiNotice, setUiNotice] = useState('');
  const [waveHeights, setWaveHeights] = useState([20, 36, 56, 44, 64, 40, 56, 28, 48, 60, 32, 16]);
  const isMountedRef = useRef(true);

  const startVoiceRecording = async () => {
    try {
      setUiNotice('');
      setVoiceState('recording');
      await voiceService.startRecording();
    } catch (err) {
      console.error("[VOICE UI] Failed to start recording:", err);
      setVoiceState('error');
      setUiNotice(err.message || "Failed to start microphone recording.");
    }
  };

  useEffect(() => {
    isMountedRef.current = true;
    startVoiceRecording();

    const interval = setInterval(() => {
      setWaveHeights(prev => prev.map(() => Math.floor(Math.random() * 45) + 12));
    }, 200);

    return () => {
      isMountedRef.current = false;
      clearInterval(interval);
      voiceService.stopRecording().catch(() => {});
      voiceService.stopSpeaking();
    };
  }, []);

  const handleDoneSpeaking = async () => {
    // If already typed text into box, allow direct submission
    if (voiceState === 'transcribing' || voiceState === 'thinking') return;

    let finalQuery = (spokenQuery || "").trim();

    // 1. If currently recording, stop MediaRecorder and transcribe
    if (voiceState === 'recording') {
      try {
        setVoiceState('transcribing');
        const audioBlob = await voiceService.stopRecording();
        
        if (audioBlob && audioBlob.size > 0) {
          const res = await voiceService.transcribe(audioBlob, language);
          const transcriptText = (res && typeof res === 'object' ? res.transcript : res) || "";
          
          if (transcriptText && transcriptText.trim()) {
            finalQuery = transcriptText.trim();
            setSpokenQuery(finalQuery);
          }
        }
      } catch (err) {
        console.warn("[VOICE UI] Transcription notice:", err);
        if (!finalQuery) {
          setVoiceState('error');
          setUiNotice(err.message || "Voice transcription was unable to recognize speech. Please speak clearly or type your question below.");
          return;
        }
      }
    }

    if (!finalQuery) {
      setVoiceState('error');
      setUiNotice("No speech detected in recording. Please speak into your microphone or type your question in the text box below.");
      return;
    }

    // 2. Put transcript into search query and navigate to results page
    setSearchQuery(finalQuery);
    if (isMountedRef.current) {
      navigate('/search-results');
    }
  };

  const handleRestart = async () => {
    voiceService.stopSpeaking();
    await voiceService.stopRecording().catch(() => {});
    setSpokenQuery('');
    setUiNotice('');
    await startVoiceRecording();
  };

  const isRecording = voiceState === 'recording';
  const isBusy = voiceState === 'transcribing' || voiceState === 'thinking' || voiceState === 'speaking';

  return (
    <div className="bg-surface-sand text-text-charcoal font-body-md min-h-screen flex flex-col">
      <Header title={t("activeVoice.title")} showBack />

      <main className="flex-1 w-full max-w-md mx-auto px-4 pt-20 pb-28 flex flex-col gap-5">
        
        {/* Top Status Bar */}
        <div className="flex items-center justify-between gap-2 pt-1">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-warm-white shadow-sm border border-border-warm-gray/30">
            <span className="relative flex h-2.5 w-2.5">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isRecording ? 'bg-secondary' : isBusy ? 'bg-amber-500' : 'bg-slate-400'} opacity-75`}></span>
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${isRecording ? 'bg-secondary' : isBusy ? 'bg-amber-500' : 'bg-slate-400'}`}></span>
            </span>
            <span className={`font-label-sm text-xs font-semibold ${isRecording ? 'text-secondary' : isBusy ? 'text-amber-600' : 'text-slate-600'}`}>
              {voiceState === 'recording' ? t("activeVoice.listening") :
               voiceState === 'transcribing' ? 'Transcribing Speech...' :
               voiceState === 'thinking' ? 'Consulting Health Schemes...' :
               voiceState === 'speaking' ? 'Playing Response...' :
               voiceState === 'error' ? 'Voice Notice' : 'Ready'}
            </span>
          </div>

          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-warm-white shadow-sm border border-border-warm-gray/30">
            <span className="material-symbols-outlined text-[16px] text-emerald-600 font-bold">mic</span>
            <span className="font-label-sm text-xs text-text-charcoal font-medium">
              Audio Recording
            </span>
          </div>
        </div>

        {/* Error / Notice Banner */}
        {uiNotice && (
          <div className="p-3.5 bg-amber-50 border border-amber-200 text-amber-900 rounded-2xl text-xs font-medium leading-relaxed shadow-sm">
            {uiNotice}
          </div>
        )}

        {/* Dynamic Waveform Centerpiece */}
        <div className="relative flex flex-col items-center justify-center p-6 rounded-3xl bg-surface-warm-white shadow-sm overflow-hidden min-h-[180px] border border-border-warm-gray/40">
          <div className="flex flex-col items-center text-center z-10 mb-4">
            <p className="font-headline-sm text-base font-bold text-text-charcoal">
              {isRecording ? "Recording your question..." :
               voiceState === 'transcribing' ? "Converting audio to text..." :
               voiceState === 'thinking' ? "Finding matching schemes..." :
               "Tap Done to Submit"}
            </p>
            <p className="font-body-sm text-xs text-text-slate mt-0.5">
              {isRecording ? "Speak clearly into your microphone, then tap Done." : "Review or edit your question below."}
            </p>
          </div>

          <div className="flex items-center justify-center gap-1.5 h-16 w-full px-4 z-10">
            {waveHeights.map((h, i) => (
              <span
                key={i}
                className={`w-1.5 rounded-full transition-all duration-200 ${isRecording ? 'bg-primary-container' : 'bg-slate-300'}`}
                style={{ height: isRecording ? `${h}px` : '12px' }}
              />
            ))}
          </div>
        </div>

        {/* Editable Transcript Section */}
        <section className="bg-surface-warm-white rounded-3xl p-5 shadow-sm border border-border-warm-gray/40 flex flex-col gap-3">
          <div className="flex items-center justify-between border-b border-border-warm-gray/30 pb-2.5">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[20px] text-primary-container">notes</span>
              <h3 className="font-headline-sm text-sm font-bold text-text-charcoal">
                {t("activeVoice.realtimeTranscript")}
              </h3>
            </div>
            {isRecording && (
              <span className="text-[11px] font-semibold text-secondary flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse"></span>
                Recording audio...
              </span>
            )}
          </div>

          <div className="bg-surface-sand/60 p-4 rounded-2xl border border-border-warm-gray/30 flex flex-col gap-2">
            <textarea
              id="voiceTranscriptInput"
              value={spokenQuery}
              onChange={(e) => setSpokenQuery(e.target.value)}
              placeholder="Speak into microphone or edit your question here..."
              rows={3}
              className="w-full bg-transparent font-body-md text-sm text-text-charcoal leading-relaxed focus:outline-none resize-none"
            />
          </div>
        </section>

        {/* Action Buttons */}
        <section className="flex flex-col gap-3">
          <button
            onClick={handleDoneSpeaking}
            disabled={isBusy}
            className="w-full py-4 rounded-full bg-primary-container text-on-primary font-label-md text-sm font-semibold hover:bg-primary active:scale-[0.98] transition-all shadow-md flex items-center justify-center gap-2 min-h-[52px]"
            type="button"
          >
            {isBusy ? (
              <>
                <span className="material-symbols-outlined text-[20px] animate-spin">sync</span>
                <span>{voiceState === 'transcribing' ? 'Transcribing...' : t("activeVoice.analyzingSchemes")}</span>
              </>
            ) : (
              <>
                <span>{t("activeVoice.doneSpeaking")}</span>
                <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
              </>
            )}
          </button>

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={handleRestart}
              disabled={isBusy}
              className="py-3 rounded-2xl bg-surface-sand text-text-charcoal font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors border border-border-warm-gray/40 min-h-[44px]"
              type="button"
            >
              {t("activeVoice.clearRestart")}
            </button>
            <button
              onClick={() => {
                voiceService.stopRecording().catch(() => {});
                voiceService.stopSpeaking();
                navigate('/');
              }}
              className="py-3 rounded-2xl bg-surface-sand text-text-charcoal font-label-sm text-xs font-semibold hover:bg-surface-dim transition-colors border border-border-warm-gray/40 min-h-[44px]"
              type="button"
            >
              {t("activeVoice.typeInstead")}
            </button>
          </div>
        </section>

      </main>

      <BottomNav />
    </div>
  );
};

export default ActiveVoiceListeningPage;
