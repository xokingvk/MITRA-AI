// MITRA AI Turn-based Audio Voice Service using MediaRecorder & Backend STT/TTS

import { transcribeVoice, synthesizeVoice } from './api';

export class VoiceAssistantService {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.activeStream = null;
    this.isRecording = false;
    this.currentAudioPlayer = null;
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
  }

  isSupported() {
    return (
      typeof window !== 'undefined' &&
      typeof navigator !== 'undefined' &&
      Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder)
    );
  }

  isSecureContext() {
    if (typeof window === 'undefined') return true;
    return Boolean(
      window.isSecureContext ||
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1'
    );
  }

  async requestMicrophonePermission() {
    console.log("[VOICE] Requesting microphone access via getUserMedia...");
    
    if (!this.isSecureContext()) {
      throw new Error("Microphone recording requires HTTPS on mobile. Deploy the frontend using an HTTPS URL.");
    }

    if (!this.isSupported()) {
      throw new Error("Microphone recording is not supported in this browser.");
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      console.log("[VOICE] Microphone permission granted.");
      this.activeStream = stream;
      return stream;
    } catch (err) {
      console.error("[VOICE] Microphone permission denied or failed:", err);
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        throw new Error("Microphone access was denied. Please allow microphone access in your browser settings.");
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        throw new Error("No microphone device found on this device.");
      }
      throw new Error(`Microphone error: ${err.message || 'Unable to access audio hardware.'}`);
    }
  }

  async startRecording(onDataAvailable) {
    if (this.isRecording) {
      console.warn("[VOICE] Recording is already in progress.");
      return;
    }

    this.stopSpeaking();
    this.audioChunks = [];

    const stream = await this.requestMicrophonePermission();

    // Select supported audio mime type in priority order
    const candidateMimes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/ogg',
      'audio/mp4',
      'audio/wav'
    ];
    let selectedMimeType = '';
    if (typeof MediaRecorder !== 'undefined' && typeof MediaRecorder.isTypeSupported === 'function') {
      for (const candidate of candidateMimes) {
        if (MediaRecorder.isTypeSupported(candidate)) {
          selectedMimeType = candidate;
          break;
        }
      }
    }

    try {
      this.mediaRecorder = selectedMimeType
        ? new MediaRecorder(stream, { mimeType: selectedMimeType })
        : new MediaRecorder(stream);
    } catch (e) {
      console.warn("[VOICE] MediaRecorder initialization with explicit MIME failed, using browser default:", e);
      this.mediaRecorder = new MediaRecorder(stream);
    }

    this.selectedMimeType = this.mediaRecorder.mimeType || selectedMimeType || 'audio/webm';

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        this.audioChunks.push(event.data);
        if (onDataAvailable) onDataAvailable(event.data);
      }
    };

    this.mediaRecorder.onstart = () => {
      console.log(`[VOICE] MediaRecorder started. selectedMimeType="${this.selectedMimeType}", actualMimeType="${this.mediaRecorder.mimeType}".`);
      this.isRecording = true;
    };

    // Continuous recording delivers clean, unfragmented container headers upon stop
    this.mediaRecorder.start();
  }

  async stopRecording() {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        this.isRecording = false;
        this.cleanupStream();
        resolve(null);
        return;
      }

      this.mediaRecorder.onstop = () => {
        this.isRecording = false;
        const actualMime = this.mediaRecorder?.mimeType || this.selectedMimeType || 'audio/webm';
        const chunkCount = this.audioChunks.length;
        const audioBlob = new Blob(this.audioChunks, { type: actualMime });

        console.log(`[VOICE] Recording stopped. chunks=${chunkCount}, blob_size=${audioBlob.size} bytes, blob_type="${audioBlob.type}"`);

        this.cleanupStream();
        this.audioChunks = [];

        if (audioBlob.size === 0) {
          reject(new Error("No audio was recorded. Please speak clearly into your microphone."));
        } else {
          resolve(audioBlob);
        }
      };

      this.mediaRecorder.onerror = (err) => {
        console.error("[VOICE] MediaRecorder error:", err);
        this.isRecording = false;
        this.cleanupStream();
        reject(err);
      };

      try {
        if (this.mediaRecorder.state === 'recording') {
          try {
            this.mediaRecorder.requestData();
          } catch (e) {}
        }
        this.mediaRecorder.stop();
      } catch (err) {
        this.cleanupStream();
        reject(err);
      }
    });
  }

  cleanupStream() {
    if (this.activeStream) {
      try {
        this.activeStream.getTracks().forEach((track) => track.stop());
      } catch (e) {}
      this.activeStream = null;
    }
  }

  async transcribe(audioBlob, language = 'en') {
    if (!audioBlob || audioBlob.size === 0) {
      throw new Error("No speech recorded. Please speak clearly into your microphone.");
    }
    console.log(`[VOICE] Sending audio recording (${audioBlob.size} bytes) for transcription (language: ${language})...`);
    const response = await transcribeVoice(audioBlob, language);
    return response;
  }

  async speak(text, onEnd, language = 'en') {
    if (!text || !text.trim()) {
      if (onEnd) onEnd();
      return;
    }

    this.stopSpeaking();

    // 1. Try Gemini backend native TTS synthesis first
    try {
      const result = await synthesizeVoice(text, language);
      if (result && result.audio_base64) {
        console.log(`[VOICE] Playing Gemini native synthesized audio for language ${language}...`);
        const audioUrl = `data:audio/wav;base64,${result.audio_base64}`;
        const audio = new Audio(audioUrl);
        this.currentAudioPlayer = audio;
        audio.onended = () => {
          this.currentAudioPlayer = null;
          if (onEnd) onEnd();
        };
        audio.onerror = (e) => {
          console.warn("[VOICE] Gemini audio playback error, trying browser fallback:", e);
          this.currentAudioPlayer = null;
          this.speakWithBrowserSynth(text, onEnd, language);
        };
        await audio.play();
        return;
      }
    } catch (e) {
      console.warn("[VOICE] Backend Gemini TTS unavailable, using browser speech synthesis fallback:", e);
    }

    // 2. Fallback to browser Web Speech Synthesis
    this.speakWithBrowserSynth(text, onEnd, language);
  }

  speakWithBrowserSynth(text, onEnd, language = 'en') {
    if (!this.synth) {
      if (onEnd) setTimeout(onEnd, 500);
      return;
    }

    this.synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    const langLocales = {
      en: 'en-IN',
      hi: 'hi-IN',
      ta: 'ta-IN',
      te: 'te-IN',
      kn: 'kn-IN',
      ml: 'ml-IN',
      mr: 'mr-IN',
      bn: 'bn-IN',
      gu: 'gu-IN'
    };
    const cleanLang = String(language || 'en').toLowerCase().split('-')[0];
    utterance.lang = langLocales[cleanLang] || 'en-IN';

    utterance.onend = () => {
      console.log(`[VOICE] Browser speech synthesis completed (${utterance.lang}).`);
      if (onEnd) onEnd();
    };

    utterance.onerror = (err) => {
      console.warn("[VOICE] Browser speech synthesis notice:", err);
      if (onEnd) onEnd();
    };

    this.synth.speak(utterance);
  }

  stopSpeaking() {
    if (this.currentAudioPlayer) {
      try {
        this.currentAudioPlayer.pause();
        this.currentAudioPlayer.currentTime = 0;
      } catch (e) {}
      this.currentAudioPlayer = null;
    }

    if (this.synth) {
      try {
        this.synth.cancel();
      } catch (e) {}
    }
  }
}

export const voiceService = new VoiceAssistantService();
