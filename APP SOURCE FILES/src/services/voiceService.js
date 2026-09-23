// Voice Speech Recognition and Text-to-Speech service wrapper

export class VoiceAssistantService {
  constructor() {
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
    this.recognition = null;
    this.isListening = false;
    this.isManuallyStopped = false;
    this.shouldAutoRestart = true;
    this.lastTranscript = '';
    this.activeStream = null;

    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
      }
    }
  }

  isSupported() {
    const supported = Boolean(this.recognition);
    if (!supported) {
      console.warn("[Voice] Unsupported browser. Neither SpeechRecognition nor webkitSpeechRecognition is available.");
    }
    return supported;
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
      utterance.onend = () => {
        console.log("[Voice] Speech synthesis completed.");
        onEnd();
      };
      utterance.onerror = (err) => {
        console.warn("[Voice] Speech synthesis error:", err);
        onEnd();
      };
    }

    this.synth.speak(utterance);
  }

  stopSpeaking() {
    if (this.synth) {
      this.synth.cancel();
    }
  }

  async requestMicrophonePermission() {
    console.log("Microphone permission requested");
    if (typeof navigator !== 'undefined' && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("Microphone permission granted");
        // Keep stream active while recognition runs so mic hardware remains enabled
        this.activeStream = stream;
        return true;
      } catch (err) {
        console.error("Microphone permission error / denied:", err);
        return false;
      }
    }
    return true;
  }

  async startListening(onResult, onError, onEnd, lang = 'en-US') {
    if (!this.isSupported()) {
      const msg = "Speech recognition is not supported in this browser. Please use Google Chrome.";
      console.error("Recognition error:", msg);
      if (onError) onError(msg, "unsupported-browser");
      return;
    }

    // Prevent multiple SpeechRecognition instances from running simultaneously
    if (this.isListening) {
      console.log("[Voice] Speech recognition already running. Resetting session...");
      this.stopListening();
    }

    // Request microphone permission from browser
    const hasPermission = await this.requestMicrophonePermission();
    if (!hasPermission) {
      const msg = "Microphone permission was denied. Please allow microphone access in your browser address bar.";
      console.error("Recognition error: not-allowed");
      if (onError) onError(msg, "not-allowed");
      return;
    }

    this.isManuallyStopped = false;
    this.shouldAutoRestart = true;
    this.lastTranscript = '';
    this.recognition.lang = lang || 'en-US';

    // REGISTER EVENT HANDLERS BEFORE CALLING recognition.start()
    this.recognition.onstart = () => {
      console.log("Recognition started");
      this.isListening = true;
    };

    this.recognition.onresult = (event) => {
      console.log("Speech result received");
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;
        if (result.isFinal) {
          finalTranscript += text + ' ';
        } else {
          interimTranscript += text;
        }
      }

      const combined = (finalTranscript + interimTranscript).trim();
      if (finalTranscript.trim()) {
        console.log("Final transcript:", finalTranscript.trim());
      }

      if (combined) {
        this.lastTranscript = combined;
        if (onResult) onResult(combined, finalTranscript.trim(), interimTranscript.trim());
      }
    };

    this.recognition.onerror = (event) => {
      console.log("Recognition error:", event.error);
      const errType = event.error;

      if (errType === 'no-speech') {
        // 'no-speech' is non-fatal: allow recognition to continue/restart if user hasn't pressed Stop
        console.log("[Voice] 'no-speech' detected. Speech recognition will remain active.");
        return;
      }

      let userMsg = `Speech recognition error: ${errType}`;
      if (errType === 'not-allowed' || errType === 'service-not-allowed') {
        userMsg = "Microphone permission was denied. Please allow microphone access in your browser.";
        this.isManuallyStopped = true;
        this.shouldAutoRestart = false;
      } else if (errType === 'audio-capture') {
        userMsg = "Your browser cannot access the microphone device. Please check audio input hardware.";
        this.isManuallyStopped = true;
        this.shouldAutoRestart = false;
      } else if (errType === 'network') {
        userMsg = "Network error occurred during speech recognition.";
      }

      this.isListening = false;
      if (onError) onError(userMsg, errType);
    };

    this.recognition.onnomatch = () => {
      console.log("[Voice] Speech onnomatch triggered.");
    };

    this.recognition.onend = () => {
      console.log("Recognition ended");
      this.isListening = false;

      // MUST NOT restart recognition after a manual Stop
      if (this.isManuallyStopped) {
        console.log("[Voice] Manual stop active. Recognition staying stopped.");
        if (onEnd) onEnd(this.lastTranscript, true);
        return;
      }

      // If ended naturally or due to no-speech without manual stop, auto-restart
      if (this.shouldAutoRestart) {
        console.log("[Voice] Continuous listening active. Auto-restarting recognition instance...");
        try {
          this.recognition.start();
          return;
        } catch (e) {
          // ignore
        }
      }

      if (onEnd) onEnd(this.lastTranscript, false);
    };

    try {
      this.recognition.start();
    } catch (err) {
      console.error("Recognition error:", err);
      this.isListening = false;
      if (onError) onError("Failed to start speech recognition.");
    }
  }

  stopListening() {
    console.log("[Voice] Setting manual stop flag BEFORE calling recognition.stop()");
    this.isManuallyStopped = true;
    this.shouldAutoRestart = false;
    this.isListening = false;

    if (this.activeStream) {
      try {
        this.activeStream.getTracks().forEach(track => track.stop());
        this.activeStream = null;
      } catch (e) {}
    }

    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        try {
          this.recognition.abort();
        } catch (e2) {}
      }
    }
  }
}

export const voiceService = new VoiceAssistantService();
