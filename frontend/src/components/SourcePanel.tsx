import React from 'react';
import {
  X,
  BookmarkCheck,
  FileText,
  ExternalLink,
} from 'lucide-react';
import type { Citation, DocumentMetadata } from '../types';

interface SourcePanelProps {
  isOpen: boolean;
  onClose: () => void;
  activeDocument: DocumentMetadata | null;
  citations: Citation[];
  onCitationClick?: (pageNumber: number) => void;
}

export const SourcePanel: React.FC<SourcePanelProps> = ({
  isOpen,
  onClose,
  activeDocument,
  citations,
  onCitationClick,
}) => {
  if (!isOpen) return null;

  return (
    <aside className="w-80 bg-[#0e1528] border-l border-[#26344d] flex flex-col h-full shrink-0 z-20 shadow-2xl animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="h-14 px-4 border-b border-[#26344d] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <BookmarkCheck className="w-4 h-4 text-sky-400" />
          <h2 className="text-xs font-bold text-white uppercase tracking-wider">
            Source Citations & Scope
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#17243a] transition-all"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body Content */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-4 text-xs">
        {/* Active Paper Scope Card */}
        <div>
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-0.5">
            <span className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-sky-400" />
              Paper Scope
            </span>
          </div>

          {activeDocument ? (
            <div className="p-3 rounded-xl bg-[#111b30] border border-sky-500/30 space-y-2">
              <h3 className="font-bold text-white text-xs leading-snug">
                {activeDocument.title}
              </h3>
              <p className="text-[11px] text-slate-400 font-mono">
                {activeDocument.filename}
              </p>
              <div className="grid grid-cols-2 gap-2 pt-1 border-t border-[#26344d]/60 text-[11px]">
                <div>
                  <span className="text-slate-500 block">Total Pages</span>
                  <span className="text-sky-300 font-bold">{activeDocument.page_count}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Extracted Words</span>
                  <span className="text-sky-300 font-bold">{activeDocument.total_words.toLocaleString()}</span>
                </div>
              </div>
              {activeDocument.sections_detected && activeDocument.sections_detected.length > 0 && (
                <div className="pt-1.5">
                  <span className="text-[10px] text-slate-500 block mb-1">Detected Sections:</span>
                  <div className="flex flex-wrap gap-1">
                    {activeDocument.sections_detected.slice(0, 6).map((sec, i) => (
                      <span
                        key={i}
                        className="text-[10px] px-1.5 py-0.2 rounded bg-[#0d1527] border border-[#26344d] text-slate-300 font-mono"
                      >
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-3 rounded-xl bg-[#111b30]/60 border border-dashed border-[#26344d] text-center text-slate-500 text-xs">
              No active research paper selected.
            </div>
          )}
        </div>

        {/* Source Citations List */}
        <div>
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 px-0.5">
            <span className="flex items-center gap-1.5">
              <BookmarkCheck className="w-3.5 h-3.5 text-sky-400" />
              Verified Excerpts ({citations.length})
            </span>
          </div>

          {citations.length === 0 ? (
            <div className="p-3.5 rounded-xl bg-[#111b30]/60 border border-[#26344d] text-slate-400 text-center italic text-xs leading-relaxed">
              No supporting passages available for this response.
            </div>
          ) : (
            <div className="space-y-2.5">
              {citations.map((c) => (
                <div
                  key={c.id}
                  onClick={() => onCitationClick && onCitationClick(c.page_number)}
                  className="p-3 rounded-xl bg-[#111b30] border border-[#26344d] hover:border-sky-500/70 transition-all space-y-1.5 group cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-sky-950/80 border border-sky-500/50 text-sky-300 font-mono">
                      {c.id}
                    </span>
                    <span className="text-[11px] text-slate-400 font-medium">
                      Page {c.page_number}
                    </span>
                  </div>
                  <blockquote className="text-[11px] text-slate-300 italic bg-[#0d1527] p-2 rounded-lg border-l-2 border-sky-400 leading-relaxed">
                    "{c.snippet}"
                  </blockquote>
                  <div className="flex items-center justify-between text-[10px] text-slate-500 pt-0.5">
                    <span>Relevance: {c.score} matches</span>
                    <span className="text-sky-400 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5 font-medium">
                      Inspect Page <ExternalLink className="w-2.5 h-2.5" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};
