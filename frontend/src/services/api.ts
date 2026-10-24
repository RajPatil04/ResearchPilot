/**
 * API service for communicating with ResearchPilot AI FastAPI backend.
 */

import type {
  AgentInvestigationResponse,
  Citation,
  ConnectResponse,
  ConversationSession,
  DocumentMetadata,
  FigureAnalysisResponse,
  HealthResponse,
  InsightsResponse,
  ModelInfo,
  SummaryResponse,
} from '../types';

const API_BASE = '/api';

export const api = {
  // --- Health & Connection ---
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return res.json();
  },

  async getModels(): Promise<{ models: ModelInfo[]; active_model: string; enable_thinking: boolean }> {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error('Failed to fetch model catalog');
    return res.json();
  },

  async connectModel(apiKey: string, model: string = 'gemma-4-26b-a4b-it', enableThinking: boolean = false): Promise<ConnectResponse> {
    const res = await fetch(`${API_BASE}/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey, model, enable_thinking: enableThinking }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Connection verification failed' }));
      throw new Error(err.detail || 'Connection verification failed');
    }
    return res.json();
  },

  // --- Document Ingestion ---
  async uploadDocument(file: File): Promise<DocumentMetadata> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async loadSampleDocument(): Promise<DocumentMetadata> {
    const res = await fetch(`${API_BASE}/documents/sample`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to load sample document' }));
      throw new Error(err.detail || 'Failed to load sample document');
    }
    return res.json();
  },

  async getDocuments(): Promise<DocumentMetadata[]> {
    const res = await fetch(`${API_BASE}/documents`);
    if (!res.ok) throw new Error('Failed to retrieve documents list');
    return res.json();
  },

  async selectDocument(docId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${docId}/select`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to select document');
  },

  async deleteDocument(docId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${docId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete document');
  },

  // --- Research Chat & Retrieval ---
  async sendChatMessage(
    message: string,
    docId?: string | null,
    history: Array<{ role: string; content: string }> = []
  ): Promise<{ response: string; citations: Citation[]; model: string; duration_seconds: number }> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        document_id: docId || null,
        history,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Inference failed' }));
      throw new Error(err.detail || 'Inference failed');
    }
    return res.json();
  },

  // --- Research Tools ---
  async generateSummary(docId: string): Promise<SummaryResponse> {
    const res = await fetch(`${API_BASE}/documents/${docId}/summary`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Summary generation failed' }));
      throw new Error(err.detail || 'Summary generation failed');
    }
    return res.json();
  },

  async generateInsights(docId: string): Promise<InsightsResponse> {
    const res = await fetch(`${API_BASE}/documents/${docId}/insights`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Insights generation failed' }));
      throw new Error(err.detail || 'Insights generation failed');
    }
    return res.json();
  },

  async analyzeFigure(docId: string, pageNumber: number, question: string, zoom: number = 1.5): Promise<FigureAnalysisResponse> {
    const res = await fetch(`${API_BASE}/documents/${docId}/figures/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_number: pageNumber, question, zoom }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Figure inspection failed' }));
      throw new Error(err.detail || 'Figure inspection failed');
    }
    return res.json();
  },

  getPageImageUrl(docId: string, pageNumber: number, zoom: number = 1.5): string {
    return `${API_BASE}/documents/${docId}/pages/${pageNumber}/image?zoom=${zoom}`;
  },

  async getCitations(docId: string, query: string): Promise<Citation[]> {
    const res = await fetch(`${API_BASE}/documents/${docId}/citations?q=${encodeURIComponent(query)}`);
    if (!res.ok) return [];
    return res.json();
  },

  // --- Agent & Export ---
  async runAgentInvestigation(query: string, docId?: string | null, maxSteps: number = 5): Promise<AgentInvestigationResponse> {
    const res = await fetch(`${API_BASE}/agent/investigate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, document_id: docId || null, max_steps: maxSteps }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Agent investigation failed' }));
      throw new Error(err.detail || 'Agent investigation failed');
    }
    return res.json();
  },

  async exportArtifact(title: string, exportType: string, content: string, docId?: string | null): Promise<Blob> {
    const res = await fetch(`${API_BASE}/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, export_type: exportType, content, document_id: docId || null }),
    });
    if (!res.ok) throw new Error('Export download failed');
    return res.blob();
  },

  // --- Conversations ---
  async getConversations(): Promise<ConversationSession[]> {
    const res = await fetch(`${API_BASE}/conversations`);
    if (!res.ok) return [];
    return res.json();
  },

  async createConversation(): Promise<ConversationSession> {
    const res = await fetch(`${API_BASE}/conversations`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to create new conversation');
    return res.json();
  },

  async deleteConversation(cid: string): Promise<void> {
    await fetch(`${API_BASE}/conversations/${cid}`, { method: 'DELETE' });
  },
};
