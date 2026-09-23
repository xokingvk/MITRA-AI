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
        this.recognition.maxAlternatives = 1;
      }
    }
  }

  isSecureContext() {
    if (typeof window === 'undefined') return true;
    const isSecure = Boolean(
      window.isSecureContext ||
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1'
    );
    return isSecure;
  }

  isSupported() {
    const supported = Boolean(this.recognition);
    console.log(`[VOICE] SpeechRecognition supported: ${supported}`);
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
        console.log("[VOICE] Speech synthesis completed.");
        onEnd();
      };
      utterance.onerror = (err) => {
        console.warn("[VOICE] Speech synthesis error:", err);
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
    console.log("[VOICE] Requesting microphone permission");

    const isSecure = this.isSecureContext();
    console.log(`[VOICE] Secure context: ${isSecure}`);

    if (!isSecure) {
      console.warn(`[VOICE] Insecure context detected (http://${window.location.hostname}). Browser may block getUserMedia.`);
    }

    if (typeof navigator !== 'undefined' && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("[VOICE] Microphone permission: granted");
        // Keep active stream reference so mic hardware stays active for SpeechRecognition
        this.activeStream = stream;
        return true;
      } catch (err) {
        console.error("[VOICE] Microphone permission: denied", err);
        return false;
      }
    }
    return true;
  }

  async startListening(onResult, onError, onEnd, lang = 'en-US') {
    console.log("[VOICE] Microphone button clicked");

    const isSecure = this.isSecureContext();
    console.log(`[VOICE] Secure context: ${isSecure}`);

    if (!isSecure) {
      const secureErrorMsg = `Microphone permission is required. Android Chrome blocks microphone access on unencrypted http:// IP addresses (http://${window.location.hostname}:3000). Please use localhost, HTTPS, or add chrome://flags/#unsafely-treat-insecure-origin-as-secure.`;
      console.error(`[VOICE] Insecure Context Error: ${secureErrorMsg}`);
      if (onError) onError(secureErrorMsg, "insecure-context");
      return;
    }

    const supported = this.isSupported();
    if (!supported) {
      const msg = "SpeechRecognition is not supported in this browser. Please use Google Chrome.";
      console.error(`[VOICE] Unsupported Browser: ${msg}`);
      if (onError) onError(msg, "unsupported-browser");
      return;
    }

    // Prevent duplicate active instances
    if (this.isListening) {
      console.log("[VOICE] Cleaning up existing active instance before starting...");
      this.stopListening();
    }

    const hasPermission = await this.requestMicrophonePermission();
    if (!hasPermission) {
      const msg = "Microphone permission is required. Please allow microphone access in your browser settings and try again.";
      console.error("[VOICE] Microphone permission: denied");
      if (onError) onError(msg, "not-allowed");
      return;
    }

    this.isManuallyStopped = false;
    this.shouldAutoRestart = true;
    this.lastTranscript = '';
    this.recognition.lang = lang || 'en-US';
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.maxAlternatives = 1;

    console.log("[VOICE] Recognition starting");

    // MANDATORY HANDLERS REGISTERED BEFORE recognition.start()
    this.recognition.onstart = () => {
      console.log("[VOICE] Recognition started");
      this.isListening = true;
    };

    this.recognition.onaudiostart = () => {
      console.log("[VOICE] Audio started");
    };

    this.recognition.onspeechstart = () => {
      console.log("[VOICE] Speech started");
    };

    this.recognition.onspeechend = () => {
      console.log("[VOICE] Speech ended");
    };

    this.recognition.onaudioend = () => {
      console.log("[VOICE] Audio ended");
    };

    this.recognition.onnomatch = () => {
      console.log("[VOICE] Recognition no match");
    };

    this.recognition.onresult = (event) => {
      console.log("[VOICE] Result received:");
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
        console.log(`[VOICE] Final transcript: "${finalTranscript.trim()}"`);
      }

      if (combined) {
        this.lastTranscript = combined;
        if (onResult) onResult(combined, finalTranscript.trim(), interimTranscript.trim());
      }
    };

    this.recognition.onerror = (event) => {
      console.log(`[VOICE] Recognition error: ${event.error}`, event);
      const errType = event.error;

      if (errType === 'no-speech') {
        // 'no-speech' is non-fatal: do not crash or force stop if user has not pressed Stop
        console.log("[VOICE] 'no-speech' event received. Recognition remaining active.");
        return;
      }

      let userMsg = `Speech recognition error: ${errType}`;
      if (errType === 'not-allowed' || errType === 'service-not-allowed') {
        userMsg = "Microphone permission is required. Please allow microphone access in your browser settings and try again.";
        this.isManuallyStopped = true;
        this.shouldAutoRestart = false;
      } else if (errType === 'audio-capture') {
        userMsg = "Your browser cannot access the microphone device. Please check audio input hardware.";
        this.isManuallyStopped = true;
        this.shouldAutoRestart = false;
      } else if (errType === 'network') {
        userMsg = "Network error occurred during speech recognition. Please check your internet connection.";
      } else if (errType === 'aborted') {
        userMsg = "Speech recognition cancelled.";
      }

      this.isListening = false;
      if (onError) onError(userMsg, errType);
    };

    this.recognition.onend = () => {
      console.log("[VOICE] Recognition ended");
      this.isListening = false;

      // MUST NOT restart recognition after a manual Stop
      if (this.isManuallyStopped) {
        console.log("[VOICE] Manual stop flag set. Recognition staying stopped.");
        if (onEnd) onEnd(this.lastTranscript, true);
        return;
      }

      // Auto-restart if ended naturally without manual stop
      if (this.shouldAutoRestart) {
        console.log("[VOICE] Restarting recognition session for continuous listening...");
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
      console.error("[VOICE] Exception starting recognition:", err);
      this.isListening = false;
      if (onError) onError("Failed to start speech recognition.");
    }
  }

  stopListening() {
    console.log("[VOICE] Manual stop requested. Setting manuallyStopped flag BEFORE recognition.stop()");
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
