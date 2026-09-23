class MitraException(Exception):
    """Base exception class for MITRA AI backend."""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class DocumentProcessingError(MitraException):
    """Raised when PDF or document processing fails."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)

class VectorStoreError(MitraException):
    """Raised when vector store creation or retrieval fails."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=500, details=details)

class GeminiAPIError(MitraException):
    """Raised when Gemini API request fails or is unconfigured."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=502, details=details)

class UnsupportedLanguageError(MitraException):
    """Raised when an invalid or unsupported language is requested."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=422, details=details)
