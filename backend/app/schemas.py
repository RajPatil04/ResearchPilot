"""Pydantic schemas for ResearchPilot AI FastAPI backend."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConnectRequest(BaseModel):
    api_key: str = Field(..., description="Google AI Studio API key")
    model: Optional[str] = Field("gemma-4-26b-a4b-it", description="Configured Gemma 4 model ID")
    enable_thinking: Optional[bool] = Field(False, description="Enable thinking_level='high'")


class ConnectResponse(BaseModel):
    success: bool
    message: str
    model: str
    has_api_key: bool


class ModelInfo(BaseModel):
    id: str
    name: str
    is_default: bool
    description: str


class DocumentMetadata(BaseModel):
    id: str
    title: str
    filename: str
    page_count: int
    total_words: int
    total_characters: int
    estimated_reading_minutes: float
    sections_detected: List[str]
    is_scanned: bool
    is_active: bool = False


class Citation(BaseModel):
    id: str
    title: str
    page_number: int
    snippet: str
    score: int


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    document_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    response: str
    citations: List[Citation]
    model: str
    duration_seconds: float
    document_id: Optional[str] = None


class SummaryResponse(BaseModel):
    summary: str
    metadata: DocumentMetadata
    citations: List[Citation]
    duration_seconds: float


class InsightsResponse(BaseModel):
    insights: str
    metadata: DocumentMetadata
    duration_seconds: float


class FigureAnalysisRequest(BaseModel):
    page_number: int
    question: str
    zoom: Optional[float] = 1.5


class FigureAnalysisResponse(BaseModel):
    analysis: str
    page_number: int
    question: str
    document_id: str


class AgentInvestigationRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    max_steps: Optional[int] = 5


class AgentInvestigationResponse(BaseModel):
    query: str
    execution_trace: List[Dict[str, Any]]
    tool_calls_count: int
    referenced_pages: List[int]
    synthesized_answer: str


class ConversationSession(BaseModel):
    id: str
    title: str
    created_at: str
    document_id: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)


class ExportRequest(BaseModel):
    title: str
    export_type: str  # summary, chat, insights, dossier
    content: Optional[str] = None
    document_id: Optional[str] = None
