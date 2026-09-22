// Voice Speech Recognition and Text-to-Speech service wrapper

export class VoiceAssistantService {
  constructor() {
    this.synth = typeof window !== 'undefined' ? window.speechSynthesis : null;
    this.recognition = null;
    
    if (typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
    }
  }

  speak(text, onEnd) {
    if (!this.synth) {
      if (onEnd) setTimeout(onEnd, 2000);
      return;
    }

    this.synth.cancel(); // Stop any ongoing speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95; // Clear, relaxed cadence for civic assistant
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

  startListening(onResult, onError, onEnd) {
    if (!this.recognition) {
      console.warn("Speech recognition not supported in this browser, using simulated voice input.");
      // Fallback simulation
      setTimeout(() => {
        onResult("I have 2 acres land in Thanjavur and need seeds and PM-Kisan financial aid.");
        if (onEnd) onEnd();
      }, 3000);
      return;
    }

    this.recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      onResult(transcript);
    };

    this.recognition.onerror = (err) => {
      if (onError) onError(err);
    };

    this.recognition.onend = () => {
      if (onEnd) onEnd();
    };

    this.recognition.start();
  }

  stopListening() {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        // ignore
      }
    }
  }
}

export const voiceService = new VoiceAssistantService();
