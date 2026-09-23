// Voice Speech Recognition and Text-to-Speech service wrapper

export class VoiceAssistantService {
  constructor() {
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
    this.recognition = null;
    this.isListening = false;
    this.isManuallyStopped = false;
    this.lastTranscript = '';
    
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
    if (typeof navigator !== 'undefined' && navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        console.log("[Voice] Requesting microphone permission...");
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Stop temporary track right after permission granted so speech recognition can use audio device
        stream.getTracks().forEach(track => track.stop());
        console.log("[Voice] Microphone permission granted.");
        return true;
      } catch (err) {
        console.warn("[Voice] Microphone permission request failed:", err);
        return false;
      }
    }
    return true; // Fallback if getUserMedia not available directly
  }

  async startListening(onResult, onError, onEnd, lang = 'en-US') {
    console.log("[Voice] Microphone button clicked / startListening requested");

    if (!this.isSupported()) {
      const msg = "Unsupported browser. Please use Google Chrome for voice input.";
      console.error(`[Voice] ${msg}`);
      if (onError) onError(msg);
      return;
    }

    // Request microphone permission first
    const hasPermission = await this.requestMicrophonePermission();
    if (!hasPermission) {
      const msg = "Microphone permission denied. Please allow microphone access in your browser settings.";
      console.error(`[Voice] ${msg}`);
      if (onError) onError(msg);
      return;
    }

    // Reset state flags
    this.isManuallyStopped = false;
    this.lastTranscript = '';

    // If already listening, stop current session cleanly before restarting
    if (this.isListening) {
      console.log("[Voice] Stopping existing listening session before starting new one...");
      try { this.recognition.stop(); } catch(e) {}
    }

    this.isListening = true;
    this.recognition.lang = lang;

    // MANDATORY REQUIREMENT: Register event handlers BEFORE calling recognition.start()
    this.recognition.onstart = () => {
      console.log("[Voice] Recognition started");
      this.isListening = true;
    };

    this.recognition.onresult = (event) => {
      console.log("[Voice] Speech recognition result received");
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;
        if (result.isFinal) {
          finalTranscript += text + ' ';
          console.log(`[Voice] Final transcript received: "${text}"`);
        } else {
          interimTranscript += text;
          console.log(`[Voice] Interim transcript received: "${text}"`);
        }
      }

      const fullTranscript = (finalTranscript + interimTranscript).trim();
      if (fullTranscript) {
        this.lastTranscript = fullTranscript;
        if (onResult) onResult(fullTranscript, finalTranscript.trim());
      }
    };

    this.recognition.onerror = (event) => {
      console.error(`[Voice] Recognition error: ${event.error}`, event);
      const errType = event.error;

      let userMsg = `Speech recognition error: ${errType}`;
      if (errType === 'not-allowed' || errType === 'service-not-allowed') {
        userMsg = "Microphone permission denied. Please enable microphone access.";
        this.isManuallyStopped = true;
      } else if (errType === 'audio-capture') {
        userMsg = "No microphone hardware detected on your device.";
        this.isManuallyStopped = true;
      } else if (errType === 'no-speech') {
        userMsg = "No speech detected. Please speak clearly into your microphone.";
      } else if (errType === 'network') {
        userMsg = "Network error occurred during speech recognition.";
      } else if (errType === 'aborted') {
        userMsg = "Speech recognition cancelled.";
      }

      if (errType === 'not-allowed' || errType === 'audio-capture') {
        this.isListening = false;
      }

      if (onError) onError(userMsg, errType);
    };

    this.recognition.onend = () => {
      console.log("[Voice] Recognition ended");
      this.isListening = false;

      // Do NOT automatically restart if user manually stopped
      if (this.isManuallyStopped) {
        console.log("[Voice] Recognition stopped manually by user.");
        if (onEnd) onEnd(this.lastTranscript, true);
        return;
      }

      if (onEnd) onEnd(this.lastTranscript, false);
    };

    try {
      this.recognition.start();
    } catch (err) {
      console.error("[Voice] Exception starting recognition:", err);
      this.isListening = false;
      if (onError) onError("Failed to start speech recognition.");
    }
  }

  stopListening() {
    console.log("[Voice] stopListening called by user/component.");
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
