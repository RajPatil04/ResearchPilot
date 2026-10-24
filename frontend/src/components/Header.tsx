import React from 'react';
import {
  BookOpen,
  FileText,
  SlidersHorizontal,
  BookmarkCheck,
  Sparkles,
} from 'lucide-react';
import type { DocumentMetadata, HealthResponse } from '../types';

interface HeaderProps {
  activeDocument: DocumentMetadata | null;
  health: HealthResponse | null;
  onOpenSettings: () => void;
  isSourcePanelOpen: boolean;
  onToggleSourcePanel: () => void;
  citationCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  activeDocument,
  health,
  onOpenSettings,
  isSourcePanelOpen,
  onToggleSourcePanel,
  citationCount,
}) => {
  return (
    <header className="h-14 border-b border-[#26344d] bg-[#0c1222]/90 backdrop-blur-md px-4 flex items-center justify-between shrink-0 z-10">
      {/* Left: Active Paper Scope Chip */}
      <div className="flex items-center gap-3 min-w-0">
        {activeDocument ? (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#111b30] border border-sky-500/40 text-xs text-slate-200 truncate">
            <FileText className="w-3.5 h-3.5 text-sky-400 shrink-0" />
            <span className="font-semibold text-white truncate max-w-[240px] md:max-w-[360px]">
              {activeDocument.title}
            </span>
            <span className="text-[10px] text-sky-400/80 bg-sky-950/60 px-1.5 py-0.5 rounded-full shrink-0 font-medium">
              {activeDocument.page_count} pages • ~{activeDocument.estimated_reading_minutes}m
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <BookOpen className="w-4 h-4 text-slate-500" />
            <span className="font-medium text-slate-400">No document attached</span>
            <span className="text-[11px] text-slate-500 hidden sm:inline">(Upload or select a paper)</span>
          </div>
        )}
      </div>

      {/* Right: Model status, Citation panel toggle, Settings */}
      <div className="flex items-center gap-2.5">
        {/* Model Badge */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#111b30] border border-[#26344d] text-[11px] text-slate-300">
          <Sparkles className="w-3 h-3 text-sky-400" />
          <span className="font-mono text-sky-300 font-medium">
            {health?.model || 'gemma-4-26b-a4b-it'}
          </span>
        </div>

        {/* Connection State Badge */}
        <button
          onClick={onOpenSettings}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border transition-all cursor-pointer ${
            health?.connected
              ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/20'
              : health?.has_api_key
              ? 'bg-sky-500/10 border-sky-500/40 text-sky-400 hover:bg-sky-500/20'
              : 'bg-amber-500/10 border-amber-500/40 text-amber-400 hover:bg-amber-500/20'
          }`}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              health?.connected ? 'bg-emerald-400 shadow-sm shadow-emerald-400' : health?.has_api_key ? 'bg-sky-400' : 'bg-amber-400'
            }`}
          />
          <span className="hidden sm:inline">
            {health?.connected ? 'Connected' : health?.has_api_key ? 'Ready to Test' : 'Key Required'}
          </span>
        </button>

        {/* Source Citations Toggle */}
        <button
          onClick={onToggleSourcePanel}
          title={isSourcePanelOpen ? 'Close citations panel' : 'Inspect citations panel'}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium border transition-all cursor-pointer ${
            isSourcePanelOpen
              ? 'bg-sky-600 border-sky-400 text-white shadow-sm shadow-sky-600/30'
              : 'bg-[#111b30] border-[#26344d] text-slate-300 hover:text-white hover:border-slate-500'
          }`}
        >
          <BookmarkCheck className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Citations</span>
          {citationCount > 0 && (
            <span className="bg-sky-400 text-slate-950 font-bold text-[10px] px-1.5 py-0.2 rounded-full">
              {citationCount}
            </span>
          )}
        </button>

        {/* Settings button */}
        <button
          onClick={onOpenSettings}
          title="Open Model Settings"
          className="p-1.5 rounded-lg bg-[#111b30] border border-[#26344d] text-slate-400 hover:text-white hover:border-slate-500 transition-all cursor-pointer"
        >
          <SlidersHorizontal className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
