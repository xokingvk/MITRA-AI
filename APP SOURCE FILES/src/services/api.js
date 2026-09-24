// MITRA AI Centralized API Service

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://mitra-ai-6a4h.onrender.com";

/**
 * FLOW A: Sends a text or voice chat query to the MITRA AI backend RAG service.
 * @param {string} message - User query message
 * @param {string} language - Target ISO language code (default 'en')
 * @param {string} [sessionId] - Optional conversation session ID
 */
export async function sendChatMessage(message, language = "en", sessionId = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        language,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || `Server error ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API sendChatMessage error:", error);
    throw error;
  }
}

/**
 * FLOW B: Uploads a temporary user supporting document (PDF/JPG/PNG) to Gemini for profile field extraction.
 * @param {File} file - File object from file input
 */
export async function uploadDocument(file) {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || `Upload failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API uploadDocument error:", error);
    throw error;
  }
}

/**
 * FLOW B: Matches user-confirmed profile information against the permanent health scheme corpus.
 * @param {Object} confirmedProfile - Object containing user-edited profile fields
 * @param {string} language - Target ISO language code
 */
export async function matchConfirmedProfile(confirmedProfile, language = "en") {
  try {
    const response = await fetch(`${API_BASE_URL}/api/documents/match`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        confirmed_profile: confirmedProfile,
        language: language,
      }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || `Scheme matching failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API matchConfirmedProfile error:", error);
    throw error;
  }
}

/**
 * Checks the backend health status.
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) return { status: "unhealthy", error: response.statusText };
    return await response.json();
  } catch (error) {
    console.error("API checkBackendHealth error:", error);
    return { status: "offline", error: error.message };
  }
}

/**
 * Transcribes recorded audio bytes using the backend STT service.
 * @param {Blob} audioBlob - Recorded audio Blob from MediaRecorder
 * @param {string} language - ISO language code
 */
export async function transcribeVoice(audioBlob, language = "en") {
  try {
    const formData = new FormData();
    const fileExt = audioBlob.type.includes("mp4") ? "mp4" : audioBlob.type.includes("wav") ? "wav" : "webm";
    formData.append("file", audioBlob, `voice_recording.${fileExt}`);
    formData.append("language_code", language === "ta" ? "ta-IN" : language === "hi" ? "hi-IN" : "en-IN");

    const response = await fetch(`${API_BASE_URL}/api/voice/transcribe`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || `Voice transcription failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API transcribeVoice error:", error);
    throw error;
  }
}

/**
 * Synthesizes text to speech audio using the backend TTS service.
 * @param {string} text - Text to speak
 * @param {string} language - ISO language code
 */
export async function synthesizeVoice(text, language = "en") {
  try {
    const response = await fetch(`${API_BASE_URL}/api/voice/synthesize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text,
        language_code: language === "ta" ? "ta-IN" : language === "hi" ? "hi-IN" : "en-IN",
      }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || errData.message || `Voice synthesis failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API synthesizeVoice error:", error);
    throw error;
  }
}

/**
 * Fetches available health schemes catalog.
 */
export async function fetchSchemes(category = null, language = "en") {
  try {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (language) params.append("language", language);

    const url = `${API_BASE_URL}/api/schemes${params.toString() ? `?${params.toString()}` : ""}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch schemes: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API fetchSchemes error:", error);
    throw error;
  }
}
