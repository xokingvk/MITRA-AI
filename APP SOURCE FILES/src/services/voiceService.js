// Voice Speech Recognition and Text-to-Speech service wrapper

export class VoiceAssistantService {
  constructor() {
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
    this.recognition = null;
    this.isListening = false;
    this.isManuallyStopped = false;
    this.lastTranscript = '';
    
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
    }
  }

  isSupported() {
    return Boolean(this.recognition);
  }

  speak(text, onEnd) {
    if (!this.synth) {
      if (onEnd) setTimeout(onEnd, 1000);
      return;
    }

    this.synth.cancel(); // Stop any ongoing speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    
    if (onEnd) {
      utterance.onend = onEnd;
      utterance.onerror = onEnd;
    }

    this.synth.speak(utterance);
  }

  stopSpeaking() {
    if (this.synth) {
      this.synth.cancel();
    }
  }

  startListening(onResult, onError, onEnd, lang = 'en-US') {
    if (!this.recognition) {
      if (onError) onError("Speech recognition is not supported in this browser.");
      return;
    }

    // Stop any active recognition session first
    this.stopListening();

    this.isManuallyStopped = false;
    this.isListening = true;
    this.lastTranscript = '';
    this.recognition.lang = lang;

    this.recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      if (transcript.trim()) {
        this.lastTranscript = transcript.trim();
        if (onResult) onResult(this.lastTranscript);
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      const errType = event.error;
      
      if (errType === 'not-allowed' || errType === 'service-not-allowed') {
        this.isListening = false;
        this.isManuallyStopped = true;
        if (onError) onError("Microphone access denied. Please allow microphone permissions.");
      } else if (errType === 'no-speech') {
        // Ignore silent timeouts during speech active listening
      } else {
        if (onError) onError(`Speech recognition error: ${errType}`);
      }
    };

    this.recognition.onend = () => {
      this.isListening = false;

      // Do NOT automatically restart if manually stopped
      if (this.isManuallyStopped) {
        if (onEnd) onEnd(this.lastTranscript, true);
        return;
      }

      if (onEnd) onEnd(this.lastTranscript, false);
    };

    try {
      this.recognition.start();
    } catch (err) {
      console.warn("Failed to start speech recognition:", err);
      if (onError) onError("Failed to start microphone listening.");
      this.isListening = false;
    }
  }

  stopListening() {
    this.isManuallyStopped = true;
    this.isListening = false;
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        try {
          this.recognition.abort();
        } catch (e2) {
          // ignore
        }
      }
    }
  }
}

export const voiceService = new VoiceAssistantService();
