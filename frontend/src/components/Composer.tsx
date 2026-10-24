import React, { useState, useRef, useEffect } from 'react';
import {
  ArrowUp,
  Square,
  Plus,
  FileText,
  X,
  Sparkles,
  BarChart,
  Compass,
  FileSpreadsheet,
  Download,
  Bot,
} from 'lucide-react';
import type { DocumentMetadata } from '../types';

interface ComposerProps {
  input: string;
  setInput: (val: string) => void;
  onSend: () => void;
  onStop: () => void;
  isGenerating: boolean;
  activeDocument: DocumentMetadata | null;
  onRemoveDocument: () => void;
  onOpenUpload: () => void;
  onOpenSummary: () => void;
  onOpenInsights: () => void;
  onOpenFigures: () => void;
  onOpenAgent: () => void;
  onOpenExport: () => void;
  onLoadSample: () => void;
}

export const Composer: React.FC<ComposerProps> = ({
  input,
  setInput,
  onSend,
  onStop,
  isGenerating,
  activeDocument,
  onRemoveDocument,
  onOpenUpload,
  onOpenSummary,
  onOpenInsights,
  onOpenFigures,
  onOpenAgent,
  onOpenExport,
  onLoadSample,
}) => {
  const [isToolsOpen, setIsToolsOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const toolsMenuRef = useRef<HTMLDivElement>(null);

  // Close tools menu on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (toolsMenuRef.current && !toolsMenuRef.current.contains(e.target as Node)) {
        setIsToolsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!isGenerating && input.trim()) {
        onSend();
      }
    }
  };

  return (
    <div className="shrink-0 p-4 max-w-3xl w-full mx-auto relative">
      {/* Plus Menu Popup */}
      {isToolsOpen && (
        <div
          ref={toolsMenuRef}
          className="absolute bottom-20 left-4 w-72 bg-[#111b30] border border-[#26344d] rounded-xl shadow-2xl p-1.5 z-30 divide-y divide-[#26344d]/60 text-xs animate-in fade-in slide-in-from-bottom-2 duration-150"
        >
          <div className="py-1">
            <button
              onClick={() => {
                setIsToolsOpen(false);
                onOpenUpload();
              }}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-[#17243a] text-slate-200 hover:text-white transition-colors cursor-pointer text-left"
            >
              <FileText className="w-4 h-4 text-sky-400" />
              <div>
                <p className="font-semibold text-xs">Attach Research Paper</p>
                <p className="text-[10px] text-slate-400">Upload PDF to index locally</p>
              </div>
            </button>

            <button
              onClick={() => {
                setIsToolsOpen(false);
                onLoadSample();
              }}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-[#17243a] text-slate-200 hover:text-white transition-colors cursor-pointer text-left"
            >
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <div>
                <p className="font-semibold text-xs">Load Sample Paper</p>
                <p className="text-[10px] text-slate-400">Gemma 4 Literature Agent paper</p>
              </div>
            </button>
          </div>

          <div className="py-1">
            <button
              disabled={!activeDocument}
              onClick={() => {
                setIsToolsOpen(false);
                onOpenSummary();
              }}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors cursor-pointer ${
                activeDocument ? 'hover:bg-[#17243a] text-slate-200 hover:text-white' : 'opacity-40 cursor-not-allowed'
              }`}
            >
              <FileSpreadsheet className="w-4 h-4 text-blue-400" />
              <div>
                <p className="font-semibold text-xs">Summarize Paper</p>
                <p className="text-[10px] text-slate-400">12-section scientific breakdown</p>
              </div>
            </button>

            <button
              disabled={!activeDocument}
              onClick={() => {
                setIsToolsOpen(false);
                onOpenInsights();
              }}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors cursor-pointer ${
                activeDocument ? 'hover:bg-[#17243a] text-slate-200 hover:text-white' : 'opacity-40 cursor-not-allowed'
              }`}
            >
              <Compass className="w-4 h-4 text-purple-400" />
              <div>
                <p className="font-semibold text-xs">Research Limitations & Gaps</p>
                <p className="text-[10px] text-slate-400">Author limitations & 3-5 hypotheses</p>
              </div>
            </button>

            <button
              disabled={!activeDocument}
              onClick={() => {
                setIsToolsOpen(false);
                onOpenFigures();
              }}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors cursor-pointer ${
                activeDocument ? 'hover:bg-[#17243a] text-slate-200 hover:text-white' : 'opacity-40 cursor-not-allowed'
              }`}
            >
              <BarChart className="w-4 h-4 text-amber-400" />
              <div>
                <p className="font-semibold text-xs">Inspect Page Figure</p>
                <p className="text-[10px] text-slate-400">Multimodal diagram understanding</p>
              </div>
            </button>

            <button
              disabled={!activeDocument}
              onClick={() => {
                setIsToolsOpen(false);
                onOpenAgent();
              }}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors cursor-pointer ${
                activeDocument ? 'hover:bg-[#17243a] text-slate-200 hover:text-white' : 'opacity-40 cursor-not-allowed'
              }`}
            >
              <Bot className="w-4 h-4 text-cyan-400" />
              <div>
                <p className="font-semibold text-xs">Autonomous Agent Investigation</p>
                <p className="text-[10px] text-slate-400">Multi-step tool execution trace</p>
              </div>
            </button>
          </div>

          <div className="py-1">
            <button
              disabled={!activeDocument}
              onClick={() => {
                setIsToolsOpen(false);
                onOpenExport();
              }}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors cursor-pointer ${
                activeDocument ? 'hover:bg-[#17243a] text-slate-200 hover:text-white' : 'opacity-40 cursor-not-allowed'
              }`}
            >
              <Download className="w-4 h-4 text-slate-400" />
              <div>
                <p className="font-semibold text-xs">Export Research Notes</p>
                <p className="text-[10px] text-slate-400">Download Complete Dossier (.md)</p>
              </div>
            </button>
          </div>
        </div>
      )}

      {/* Main Composer Box */}
      <div className="bg-[#111b30] border border-[#26344d] focus-within:border-sky-500 rounded-2xl shadow-xl transition-all p-2.5">
        {/* Attached Document Scope Chip */}
        {activeDocument && (
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#26344d]/60 px-1">
            <div className="flex items-center gap-2 truncate">
              <span className="p-1 rounded bg-sky-500/10 text-sky-400">
                <FileText className="w-3.5 h-3.5" />
              </span>
              <span className="text-xs font-semibold text-white truncate max-w-[400px]">
                {activeDocument.title}
              </span>
              <span className="text-[10px] text-slate-400">
                ({activeDocument.page_count} pages)
              </span>
            </div>
            <button
              onClick={onRemoveDocument}
              title="Detach paper context"
              className="text-slate-500 hover:text-slate-300 p-1 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        <div className="flex items-end gap-2">
          {/* Plus / Attach Button */}
          <button
            onClick={() => setIsToolsOpen(!isToolsOpen)}
            title="Attach paper or invoke research tools"
            className="p-2 rounded-xl bg-[#0e1528] hover:bg-[#17243a] text-slate-300 hover:text-white border border-[#26344d] transition-all cursor-pointer shrink-0"
          >
            <Plus className={`w-4 h-4 transition-transform ${isToolsOpen ? 'rotate-45 text-sky-400' : ''}`} />
          </button>

          {/* Text Area */}
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              activeDocument
                ? `Ask about '${activeDocument.title.slice(0, 32)}...'`
                : 'Ask research question or attach a paper...'
            }
            className="flex-1 bg-transparent border-0 text-slate-100 placeholder-slate-500 text-xs focus:ring-0 focus:outline-none resize-none py-1.5 px-1 max-h-40 leading-relaxed"
          />

          {/* Send / Stop Button */}
          {isGenerating ? (
            <button
              onClick={onStop}
              title="Stop generation"
              className="p-2 rounded-xl bg-red-600 hover:bg-red-500 text-white transition-all cursor-pointer shrink-0 shadow-sm shadow-red-900/40"
            >
              <Square className="w-4 h-4" />
            </button>
          ) : (
            <button
              disabled={!input.trim()}
              onClick={onSend}
              title="Send inquiry"
              className={`p-2 rounded-xl transition-all shrink-0 cursor-pointer ${
                input.trim()
                  ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-900/30'
                  : 'bg-[#17243a] text-slate-500 cursor-not-allowed border border-[#26344d]'
              }`}
            >
              <ArrowUp className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      <p className="text-[10px] text-slate-500 text-center mt-2">
        ResearchPilot AI grounds statements in document text with explicit citations. Always verify critical metrics.
      </p>
    </div>
  );
};
