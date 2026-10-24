"""In-memory application state manager for ResearchPilot AI backend."""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.pdf_processor import PDFProcessor
from src.gemma_client import GemmaClient, DEFAULT_GEMMA_MODEL, GemmaClientError


def _load_dotenv():
    """Load key-value pairs from .env into os.environ if not already present."""
    # Check current directory and up to project root
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key:
                                os.environ[key] = val
                break
            except Exception:
                pass


_load_dotenv()


class BackendState:
    """Singleton state manager holding active session documents, client, and chat history."""

    def __init__(self):
        _load_dotenv()
        # Environment fallback
        self.api_key: Optional[str] = os.getenv("GEMINI_API_KEY", "").strip() or None
        self.model: str = os.getenv("GEMMA_MODEL", DEFAULT_GEMMA_MODEL).strip()
        self.enable_thinking: bool = False
        self.connection_status: Optional[Tuple[bool, str]] = None

        # Auto-verify connection if API key is preconfigured in environment/.env
        if self.api_key:
            self.verify_connection()

        # Document storage: id -> PDFProcessor
        self.documents: Dict[str, PDFProcessor] = {}
        self.active_document_id: Optional[str] = None

        # Conversations: id -> dict
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.active_conversation_id: Optional[str] = None

        # Initialize default conversation
        self._create_default_conversation()

    def _create_default_conversation(self) -> str:
        cid = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.conversations[cid] = {
            "id": cid,
            "title": "New Research Inquiry",
            "created_at": now,
            "document_id": None,
            "messages": [],
        }
        self.active_conversation_id = cid
        return cid

    def get_client(self) -> Optional[GemmaClient]:
        if not self.api_key:
            return None
        return GemmaClient(
            api_key=self.api_key,
            model=self.model,
            enable_thinking=self.enable_thinking,
        )

    def verify_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            self.connection_status = (False, "API key not configured.")
            return False, "API key not configured."
        try:
            client = self.get_client()
            if not client:
                self.connection_status = (False, "Could not initialize client.")
                return False, "Could not initialize client."
            succ, msg = client.test_connection()
            self.connection_status = (succ, msg)
            return succ, msg
        except Exception as exc:
            self.connection_status = (False, str(exc))
            return False, str(exc)

    def add_document(self, file_bytes: bytes, filename: str) -> Tuple[str, PDFProcessor]:
        doc_id = str(uuid.uuid4())[:8]
        proc = PDFProcessor(file_bytes=file_bytes, filename=filename)
        self.documents[doc_id] = proc
        self.active_document_id = doc_id

        # Update active conversation with this doc
        if self.active_conversation_id and self.active_conversation_id in self.conversations:
            self.conversations[self.active_conversation_id]["document_id"] = doc_id

        return doc_id, proc

    def get_active_document(self) -> Optional[PDFProcessor]:
        if self.active_document_id and self.active_document_id in self.documents:
            return self.documents[self.active_document_id]
        if self.documents:
            first_id = list(self.documents.keys())[0]
            self.active_document_id = first_id
            return self.documents[first_id]
        return None

    def get_document_by_id(self, doc_id: str) -> Optional[PDFProcessor]:
        return self.documents.get(doc_id)

    def remove_document(self, doc_id: str) -> bool:
        if doc_id in self.documents:
            del self.documents[doc_id]
            if self.active_document_id == doc_id:
                self.active_document_id = list(self.documents.keys())[0] if self.documents else None
            return True
        return False

    def load_sample_paper(self) -> Optional[Tuple[str, PDFProcessor]]:
        sample_path = os.path.join("assets", "sample_paper_researchpilot.pdf")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                content = f.read()
            return self.add_document(content, "sample_paper_researchpilot.pdf")
        return None


# Global singleton instance
backend_state = BackendState()
