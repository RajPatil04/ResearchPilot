import React, { useState, useEffect, useRef } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatArea } from './components/ChatArea';
import { Composer } from './components/Composer';
import { SourcePanel } from './components/SourcePanel';
import { SettingsModal } from './components/SettingsModal';
import { SummaryModal } from './components/SummaryModal';
import { InsightsModal } from './components/InsightsModal';
import { FiguresModal } from './components/FiguresModal';
import { AgentModal } from './components/AgentModal';
import { api } from './services/api';
import type {
  ChatMessage,
  Citation,
  ConversationSession,
  DocumentMetadata,
  HealthResponse,
} from './types';

export const App: React.FC = () => {
  // --- Global State ---
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);
  const [selectedWorkspace, setSelectedWorkspace] = useState('Machine Learning');

  // --- Conversations & Messages ---
  const [conversations, setConversations] = useState<ConversationSession[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  // --- Citations & Source Panel ---
  const [activeCitations, setActiveCitations] = useState<Citation[]>([]);
  const [isSourcePanelOpen, setIsSourcePanelOpen] = useState(false); // Closed by default per requirement

  // --- Modals State ---
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);
  const [isInsightsOpen, setIsInsightsOpen] = useState(false);
  const [isFiguresOpen, setIsFiguresOpen] = useState(false);
  const [isAgentOpen, setIsAgentOpen] = useState(false);

  // Hidden File Input
  const fileInputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Initial Data Fetch
  useEffect(() => {
    bootstrap();
  }, []);

  const bootstrap = async () => {
    try {
      const h = await api.getHealth();
      setHealth(h);
      if (h.active_document_id) {
        setActiveDocumentId(h.active_document_id);
      }
    } catch {
      // Backend starting or offline
    }

    try {
      const docs = await api.getDocuments();
      setDocuments(docs);
      if (!activeDocumentId && docs.length > 0) {
        setActiveDocumentId(docs[0].id);
      }
    } catch {}

    try {
      const convs = await api.getConversations();
      setConversations(convs);
      if (convs.length > 0) {
        setActiveConversationId(convs[0].id);
        setMessages(convs[0].messages || []);
      }
    } catch {}
  };

  const activeDocument = documents.find((d) => d.id === activeDocumentId) || null;

  // --- Message Sending ---
  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || isGenerating) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query.trim(),
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsGenerating(true);

    try {
      const historyPayload = messages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await api.sendChatMessage(query.trim(), activeDocumentId, historyPayload);

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.response,
        citations: res.citations,
        model: res.model,
        duration_seconds: res.duration_seconds,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      if (res.citations && res.citations.length > 0) {
        setActiveCitations(res.citations);
      }
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `⚠️ **Inference Error**: ${err.message || 'Failed to communicate with Gemma 4.'}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsGenerating(false);
  };

  // --- Document Ingestion ---
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const doc = await api.uploadDocument(file);
      setDocuments((prev) => [doc, ...prev.filter((d) => d.id !== doc.id)]);
      setActiveDocumentId(doc.id);
    } catch (err: any) {
      alert(`Upload error: ${err.message}`);
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleLoadSample = async () => {
    try {
      const doc = await api.loadSampleDocument();
      setDocuments((prev) => [doc, ...prev.filter((d) => d.id !== doc.id)]);
      setActiveDocumentId(doc.id);
    } catch (err: any) {
      alert(`Could not load sample paper: ${err.message}`);
    }
  };

  const handleSelectDocument = async (id: string) => {
    setActiveDocumentId(id);
    try {
      await api.selectDocument(id);
    } catch {}
  };

  const handleDeleteDocument = async (id: string) => {
    try {
      await api.deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      if (activeDocumentId === id) {
        const remaining = documents.filter((d) => d.id !== id);
        setActiveDocumentId(remaining.length > 0 ? remaining[0].id : null);
      }
    } catch {}
  };

  // --- Conversations ---
  const handleNewConversation = async () => {
    try {
      const newConv = await api.createConversation();
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversationId(newConv.id);
      setMessages([]);
      setActiveCitations([]);
    } catch {
      setActiveConversationId(Date.now().toString());
      setMessages([]);
      setActiveCitations([]);
    }
  };

  const handleSelectConversation = (cid: string) => {
    setActiveConversationId(cid);
    const target = conversations.find((c) => c.id === cid);
    if (target) {
      setMessages(target.messages || []);
    }
  };

  const handleDeleteConversation = async (cid: string) => {
    try {
      await api.deleteConversation(cid);
      setConversations((prev) => prev.filter((c) => c.id !== cid));
      if (activeConversationId === cid) {
        handleNewConversation();
      }
    } catch {}
  };

  // --- Model Connection ---
  const handleConnect = async (apiKey: string, model: string, enableThinking: boolean) => {
    const res = await api.connectModel(apiKey, model, enableThinking);
    const updatedHealth = await api.getHealth();
    setHealth(updatedHealth);
    return res.success;
  };

  // --- Export Markdown ---
  const handleDownloadMarkdown = async (content: string) => {
    const title = activeDocument?.title || 'ResearchPilot_Chat_Response';
    const blob = await api.exportArtifact(title, 'chat', content, activeDocumentId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.slice(0, 24).replace(/\s+/g, '_')}_Response.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportFullDossier = async () => {
    if (!activeDocument) return;
    const conversationTranscript = messages
      .map((m) => `**${m.role.toUpperCase()}:** ${m.content}`)
      .join('\n\n');
    const blob = await api.exportArtifact(activeDocument.title, 'dossier', conversationTranscript, activeDocumentId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ResearchPilot_Dossier_${activeDocument.title.slice(0, 20)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#080d1a] text-slate-100 font-sans">
      {/* Hidden File Input for Paper Uploads */}
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={handleFileUpload}
      />

      {/* 1. Left Sidebar */}
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        documents={documents}
        activeDocumentId={activeDocumentId}
        onSelectDocument={handleSelectDocument}
        onDeleteDocument={handleDeleteDocument}
        onOpenSettings={() => setIsSettingsOpen(true)}
        health={health}
        selectedWorkspace={selectedWorkspace}
        onSelectWorkspace={setSelectedWorkspace}
        onUploadClick={() => fileInputRef.current?.click()}
        onLoadSampleClick={handleLoadSample}
      />

      {/* 2. Central Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        {/* Top Header */}
        <Header
          activeDocument={activeDocument}
          health={health}
          onOpenSettings={() => setIsSettingsOpen(true)}
          isSourcePanelOpen={isSourcePanelOpen}
          onToggleSourcePanel={() => setIsSourcePanelOpen(!isSourcePanelOpen)}
          citationCount={activeCitations.length}
        />

        {/* Conversation Stream Area */}
        <ChatArea
          messages={messages}
          isGenerating={isGenerating}
          activeDocument={activeDocument}
          onSelectPrompt={(promptText) => {
            setInput(promptText);
            handleSendMessage(promptText);
          }}
          onOpenCitationPanel={(citations) => {
            if (citations) setActiveCitations(citations);
            setIsSourcePanelOpen(true);
          }}
          onDownloadMarkdown={handleDownloadMarkdown}
          onLoadSampleClick={handleLoadSample}
          onUploadClick={() => fileInputRef.current?.click()}
        />

        {/* Bottom-Anchored Composer */}
        <Composer
          input={input}
          setInput={setInput}
          onSend={() => handleSendMessage()}
          onStop={handleStopGeneration}
          isGenerating={isGenerating}
          activeDocument={activeDocument}
          onRemoveDocument={() => setActiveDocumentId(null)}
          onOpenUpload={() => fileInputRef.current?.click()}
          onOpenSummary={() => setIsSummaryOpen(true)}
          onOpenInsights={() => setIsInsightsOpen(true)}
          onOpenFigures={() => setIsFiguresOpen(true)}
          onOpenAgent={() => setIsAgentOpen(true)}
          onOpenExport={handleExportFullDossier}
          onLoadSample={handleLoadSample}
        />
      </div>

      {/* 3. Right Collapsible Source Panel (Closed by default) */}
      <SourcePanel
        isOpen={isSourcePanelOpen}
        onClose={() => setIsSourcePanelOpen(false)}
        activeDocument={activeDocument}
        citations={activeCitations}
      />

      {/* Modals & Dialogs */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onConnect={handleConnect}
        health={health}
      />

      <SummaryModal
        isOpen={isSummaryOpen}
        onClose={() => setIsSummaryOpen(false)}
        document={activeDocument}
      />

      <InsightsModal
        isOpen={isInsightsOpen}
        onClose={() => setIsInsightsOpen(false)}
        document={activeDocument}
      />

      <FiguresModal
        isOpen={isFiguresOpen}
        onClose={() => setIsFiguresOpen(false)}
        document={activeDocument}
      />

      <AgentModal
        isOpen={isAgentOpen}
        onClose={() => setIsAgentOpen(false)}
        document={activeDocument}
      />
    </div>
  );
};

export default App;
