import uuid
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationService, cls).__new__(cls)
            cls._instance.store: Dict[str, List[Dict[str, str]]] = {}
        return cls._instance

    def create_session(self) -> str:
        """Generates a new conversation session ID."""
        session_id = str(uuid.uuid4())
        self.store[session_id] = []
        return session_id

    def get_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Returns turn history for a conversation ID."""
        if not conversation_id:
            return []
        return self.store.setdefault(conversation_id, [])

    def add_turn(self, conversation_id: str, role: str, content: str, max_turns: int = 12):
        """Appends a user/assistant turn and enforces maximum turn limit."""
        if not conversation_id:
            return
        
        history = self.get_history(conversation_id)
        history.append({"role": role, "content": content})
        
        # Trim history to maintain reasonable token limits
        if len(history) > max_turns:
            self.store[conversation_id] = history[-max_turns:]
        else:
            self.store[conversation_id] = history

    def format_history_text(self, conversation_id: str, max_recent: int = 6) -> str:
        """Formats recent history as a readable prompt string."""
        history = self.get_history(conversation_id)[-max_recent:]
        if not history:
            return ""
        
        formatted = []
        for turn in history:
            role_label = "User" if turn["role"] == "user" else "Assistant"
            formatted.append(f"{role_label}: {turn['content']}")
        return "\n".join(formatted)
