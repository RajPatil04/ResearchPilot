import React from 'react';
import {
  Plus,
  MessageSquare,
  FileText,
  FolderKanban,
  Settings,
  Trash2,
  BookOpen,
  ChevronRight,
  Database,
} from 'lucide-react';
import type { DocumentMetadata, ConversationSession, HealthResponse } from '../types';

interface SidebarProps {
  conversations: ConversationSession[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
  documents: DocumentMetadata[];
  activeDocumentId: string | null;
  onSelectDocument: (id: string) => void;
  onDeleteDocument: (id: string) => void;
  onOpenSettings: () => void;
  health: HealthResponse | null;
  selectedWorkspace: string;
  onSelectWorkspace: (ws: string) => void;
  onUploadClick: () => void;
  onLoadSampleClick: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  documents,
  activeDocumentId,
  onSelectDocument,
  onDeleteDocument,
  onOpenSettings,
  health,
  selectedWorkspace,
  onSelectWorkspace,
  onUploadClick,
  onLoadSampleClick,
}) => {
  const workspaces = ['Machine Learning', 'Biology Research', 'NLP Papers', 'Default'];

  const totalPages = documents.reduce((sum, d) => sum + d.page_count, 0);
  const totalWords = documents.reduce((sum, d) => sum + d.total_words, 0);

  return (
    <aside className="w-72 bg-[#0e1528] border-r border-[#26344d] flex flex-col h-full shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-4 border-b border-[#26344d]/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-700 to-sky-500 flex items-center justify-center text-white shadow-md shadow-sky-500/20">
            <BookOpen className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-white tracking-tight leading-tight">ResearchPilot AI</h1>
            <p className="text-[10px] text-sky-400 font-medium">Gemma 4 Research Assistant</p>
          </div>
        </div>
      </div>

      {/* Primary Action: New Chat */}
      <div className="p-3">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-gradient-to-r from-blue-600 to-sky-600 hover:from-blue-500 hover:to-sky-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-blue-900/30 transition-all cursor-pointer"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>New Research Chat</span>
        </button>
      </div>

      {/* Scrollable Navigation Body */}
      <div className="flex-1 overflow-y-auto px-3 space-y-4 text-xs">
        {/* Workspace Selector */}
        <div>
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-1">
            <span className="flex items-center gap-1.5">
              <FolderKanban className="w-3.5 h-3.5 text-sky-400" />
              Workspace
            </span>
          </div>
          <select
            value={selectedWorkspace}
            onChange={(e) => onSelectWorkspace(e.target.value)}
            className="w-full bg-[#111b30] border border-[#26344d] text-slate-200 text-xs rounded-lg px-2.5 py-1.5 outline-none focus:border-sky-500 cursor-pointer"
          >
            {workspaces.map((ws) => (
              <option key={ws} value={ws}>
                {ws}
              </option>
            ))}
          </select>
        </div>

        {/* Uploaded Papers Library */}
        <div>
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-1">
            <span className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-sky-400" />
              Papers ({documents.length})
            </span>
            <div className="flex items-center gap-1">
              <button
                onClick={onUploadClick}
                title="Upload PDF"
                className="hover:text-sky-400 text-slate-400 transition-colors p-0.5"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div className="space-y-1">
            {documents.length === 0 ? (
              <div className="p-2.5 rounded-lg bg-[#111b30]/60 border border-dashed border-[#26344d] text-center text-slate-400 text-[11px]">
                <p>No papers attached.</p>
                <button
                  onClick={onLoadSampleClick}
                  className="mt-1 text-sky-400 hover:text-sky-300 font-medium underline text-[11px] block mx-auto"
                >
                  ⚡ Load Sample Paper
                </button>
              </div>
            ) : (
              documents.map((doc) => {
                const isActive = doc.id === activeDocumentId;
                return (
                  <div
                    key={doc.id}
                    onClick={() => onSelectDocument(doc.id)}
                    className={`group flex items-start justify-between p-2 rounded-lg cursor-pointer transition-all border ${
                      isActive
                        ? 'bg-[#17243a] border-sky-500/70 text-white shadow-sm'
                        : 'bg-[#111b30]/60 border-transparent hover:border-[#26344d] text-slate-300 hover:text-white'
                    }`}
                  >
                    <div className="flex items-start gap-2 min-w-0">
                      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${isActive ? 'bg-sky-400 shadow-sm shadow-sky-400' : 'bg-slate-600'}`} />
                      <div className="truncate">
                        <p className="font-medium text-xs truncate leading-snug">{doc.title}</p>
                        <p className="text-[10px] text-slate-500 mt-0.5">
                          {doc.page_count} pages • {doc.total_words.toLocaleString()} words
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteDocument(doc.id);
                      }}
                      title="Remove document"
                      className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-red-400 transition-opacity ml-1"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Recent Conversations */}
        <div>
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-1">
            <span className="flex items-center gap-1.5">
              <MessageSquare className="w-3.5 h-3.5 text-sky-400" />
              Recent Conversations
            </span>
          </div>

          <div className="space-y-1">
            {conversations.length === 0 ? (
              <p className="text-slate-500 text-[11px] px-1 italic">No recent chats.</p>
            ) : (
              conversations.map((conv) => {
                const isActive = conv.id === activeConversationId;
                return (
                  <div
                    key={conv.id}
                    onClick={() => onSelectConversation(conv.id)}
                    className={`group flex items-center justify-between px-2.5 py-1.5 rounded-lg cursor-pointer transition-all ${
                      isActive
                        ? 'bg-[#17243a] text-white border border-[#26344d]'
                        : 'hover:bg-[#111b30] text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <MessageSquare className="w-3 h-3 shrink-0 text-slate-500" />
                      <span className="truncate text-xs">{conv.title}</span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteConversation(conv.id);
                      }}
                      title="Delete conversation"
                      className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 p-0.5"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Workspace Metrics */}
        <div className="p-2.5 rounded-lg bg-[#111b30] border border-[#26344d]/70 space-y-1.5 text-[11px]">
          <div className="flex items-center justify-between text-slate-400 font-semibold mb-1">
            <span className="flex items-center gap-1">
              <Database className="w-3 h-3 text-sky-400" />
              Workspace Metrics
            </span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Indexed Papers:</span>
            <span className="text-white font-medium">{documents.length}</span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Total Pages:</span>
            <span className="text-white font-medium">{totalPages}</span>
          </div>
          <div className="flex justify-between text-slate-400">
            <span>Total Words:</span>
            <span className="text-sky-400 font-medium">{totalWords.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Footer / Settings Bar */}
      <div className="p-3 border-t border-[#26344d]/80 bg-[#0c1222]">
        <button
          onClick={onOpenSettings}
          className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-[#111b30] hover:bg-[#17243a] text-slate-300 hover:text-white transition-all text-xs border border-[#26344d] cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <Settings className="w-3.5 h-3.5 text-slate-400" />
            <span className="font-medium">Model Settings</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                health?.connected
                  ? 'bg-emerald-400 shadow-sm shadow-emerald-400'
                  : health?.has_api_key
                  ? 'bg-sky-400'
                  : 'bg-amber-400'
              }`}
            />
            <ChevronRight className="w-3.5 h-3.5 text-slate-500" />
          </div>
        </button>
      </div>
    </aside>
  );
};
