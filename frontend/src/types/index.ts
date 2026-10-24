export interface DocumentMetadata {
  id: string;
  title: string;
  filename: string;
  page_count: number;
  total_words: number;
  total_characters: number;
  estimated_reading_minutes: number;
  sections_detected: string[];
  is_scanned: boolean;
  is_active?: boolean;
}

export interface Citation {
  id: string;
  title: string;
  page_number: number;
  snippet: string;
  score: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  model?: string;
  duration_seconds?: number;
  timestamp?: string;
}

export interface ConversationSession {
  id: string;
  title: string;
  created_at: string;
  document_id?: string | null;
  messages: ChatMessage[];
}

export interface ConnectResponse {
  success: boolean;
  message: string;
  model: string;
  has_api_key: boolean;
}

export interface ModelInfo {
  id: string;
  name: string;
  is_default: boolean;
  description: string;
}

export interface AgentTraceStep {
  step: number;
  tool: string;
  args: Record<string, any>;
  status: string;
  summary: string;
}

export interface AgentInvestigationResponse {
  query: string;
  execution_trace: AgentTraceStep[];
  tool_calls_count: number;
  referenced_pages: number[];
  synthesized_answer: string;
}

export interface SummaryResponse {
  summary: string;
  metadata: DocumentMetadata;
  citations: Citation[];
  duration_seconds: number;
}

export interface InsightsResponse {
  insights: string;
  metadata: DocumentMetadata;
  duration_seconds: number;
}

export interface FigureAnalysisResponse {
  analysis: string;
  page_number: number;
  question: string;
  document_id: string;
}

export interface HealthResponse {
  status: string;
  model: string;
  has_api_key: boolean;
  connected: boolean;
  documents_count: number;
  active_document_id?: string | null;
}
