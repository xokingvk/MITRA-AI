// MITRA AI Centralized API Service

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://mitra-ai-6a4h.onrender.com";

/**
 * Sends a chat message to the MITRA AI backend RAG service.
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
 * Uploads a temporary user document (PDF/Image) to the backend for session context parsing.
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
 * Fetches available health schemes.
 * @param {string} [category] - Optional category filter
 * @param {string} [language] - Optional language code
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
