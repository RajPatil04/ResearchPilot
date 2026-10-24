import React, { useEffect, useRef } from 'react';
import {
  Sparkles,
  Layers,
  Cpu,
  BarChart3,
  FileQuestion,
  BookOpen,
  ArrowRight,
} from 'lucide-react';
import type { ChatMessage, Citation, DocumentMetadata } from '../types';
import { MessageItem } from './MessageItem';

interface ChatAreaProps {
  messages: ChatMessage[];
  isGenerating: boolean;
  activeDocument: DocumentMetadata | null;
  onSelectPrompt: (promptText: string) => void;
  onOpenCitationPanel: (citations?: Citation[]) => void;
  onDownloadMarkdown: (content: string) => void;
  onLoadSampleClick: () => void;
  onUploadClick: () => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isGenerating,
  activeDocument,
  onSelectPrompt,
  onOpenCitationPanel,
  onDownloadMarkdown,
  onLoadSampleClick,
  onUploadClick,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isGenerating]);

  const suggestionPrompts = [
    {
      icon: Cpu,
      title: 'Methodology & Architecture',
      desc: 'Explain the proposed model design, formulas, and algorithms in plain terms.',
      prompt: 'Explain the proposed methodology, architecture, and core algorithms in plain language.',
    },
    {
      icon: BarChart3,
      title: 'Results & Baselines',
      desc: 'Extract reported quantitative benchmark metrics and baseline comparisons.',
      prompt: 'What exact quantitative results, metrics, and baseline comparisons did the authors report?',
    },
    {
      icon: Layers,
      title: 'Datasets & Preprocessing',
      desc: 'Identify datasets, splits, modalities, and data preparation steps.',
      prompt: 'What datasets, data sources, modalities, splits, and preprocessing steps were utilized?',
    },
    {
      icon: FileQuestion,
      title: 'Limitations & Gaps',
      desc: 'Separate stated author constraints from open future research directions.',
      prompt: 'What specific limitations, assumptions, and constraints did the authors state?',
    },
  ];

  return (
    <div className="flex-1 overflow-y-auto flex flex-col">
      {messages.length === 0 ? (
        /* Empty Welcome Screen (ChatGPT-style) */
        <div className="flex-1 flex flex-col items-center justify-center p-6 max-w-2xl mx-auto w-full text-center">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-700 to-sky-400 flex items-center justify-center text-white shadow-lg shadow-sky-500/25 mb-4">
            <Sparkles className="w-6 h-6" />
          </div>

          <h2 className="text-xl font-bold text-white tracking-tight mb-1.5">
            ResearchPilot AI
          </h2>
          <p className="text-xs text-slate-400 max-w-md mx-auto mb-6 leading-relaxed">
            Understand research beyond the abstract — powered by <strong className="text-sky-400">Gemma 4</strong> with strictly grounded <code className="text-[11px] text-sky-300 bg-sky-950/60 px-1 py-0.5 rounded border border-sky-500/30">[PAGE N]</code> citations.
          </p>

          {!activeDocument && (
            <div className="mb-6 p-3 rounded-xl bg-[#111b30] border border-[#26344d] max-w-md w-full flex items-center justify-between text-left">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
                  <BookOpen className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-white">No document attached</p>
                  <p className="text-[11px] text-slate-400">Upload a PDF or test with our sample paper</p>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={onLoadSampleClick}
                  className="text-xs bg-sky-600 hover:bg-sky-500 text-white font-semibold px-2.5 py-1.5 rounded-lg shadow-sm transition-all cursor-pointer"
                >
                  ⚡ Sample Paper
                </button>
                <button
                  onClick={onUploadClick}
                  className="text-xs bg-[#17243a] hover:bg-[#20304c] text-slate-300 font-semibold px-2.5 py-1.5 rounded-lg border border-[#26344d] transition-all cursor-pointer"
                >
                  Upload PDF
                </button>
              </div>
            </div>
          )}

          {/* Suggestion Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full text-left">
            {suggestionPrompts.map((item, idx) => {
              const Icon = item.icon;
              return (
                <button
                  key={idx}
                  onClick={() => onSelectPrompt(item.prompt)}
                  className="group p-3 rounded-xl bg-[#111b30]/80 hover:bg-[#17243a] border border-[#26344d] hover:border-sky-500/60 transition-all text-left flex flex-col justify-between cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="p-1.5 rounded-lg bg-[#0e1528] text-sky-400 group-hover:bg-sky-500/10 transition-colors">
                      <Icon className="w-4 h-4" />
                    </div>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-sky-400 transition-colors" />
                  </div>
                  <h3 className="text-xs font-bold text-white mb-0.5 group-hover:text-sky-300 transition-colors">
                    {item.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    {item.desc}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      ) : (
        /* Conversation Messages Stream */
        <div className="flex-1 max-w-3xl w-full mx-auto divide-y divide-[#26344d]/40 pb-6">
          {messages.map((msg) => (
            <MessageItem
              key={msg.id}
              message={msg}
              onOpenCitationPanel={onOpenCitationPanel}
              onDownloadMarkdown={onDownloadMarkdown}
            />
          ))}

          {/* Loading / Generating State */}
          {isGenerating && (
            <div className="flex gap-3 px-4 py-4 w-full bg-[#0f172a]/40">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-700 to-sky-500 flex items-center justify-center text-white shrink-0">
                <Sparkles className="w-4 h-4 animate-spin" />
              </div>
              <div className="space-y-1.5 flex-1 pt-1">
                <span className="text-xs font-semibold text-sky-400 flex items-center gap-2">
                  <span>Gemma 4 is inspecting document evidence...</span>
                </span>
                <div className="flex gap-1.5 items-center pt-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-bounce" />
                  <div className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-bounce [animation-delay:0.2s]" />
                  <div className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
};
