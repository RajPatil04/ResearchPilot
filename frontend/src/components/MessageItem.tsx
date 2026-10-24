import React, { useState } from 'react';
import {
  User,
  Bot,
  Copy,
  Check,
  Download,
  BookmarkCheck,
} from 'lucide-react';
import type { ChatMessage, Citation } from '../types';

interface MessageItemProps {
  message: ChatMessage;
  onOpenCitationPanel: (citations?: Citation[]) => void;
  onDownloadMarkdown: (content: string) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  onOpenCitationPanel,
  onDownloadMarkdown,
}) => {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === 'assistant';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Basic markdown-like parser for paragraphs, bold, lists, headings
  const renderFormattedContent = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      // Markdown Headings
      if (line.startsWith('### ')) {
        return (
          <h3 key={idx} className="text-sm font-bold text-sky-300 mt-3 mb-1">
            {line.replace('### ', '')}
          </h3>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h2 key={idx} className="text-base font-bold text-white mt-4 mb-1.5 border-b border-[#26344d]/70 pb-1">
            {line.replace('## ', '')}
          </h2>
        );
      }
      if (line.startsWith('# ')) {
        return (
          <h1 key={idx} className="text-lg font-extrabold text-white mt-4 mb-2">
            {line.replace('# ', '')}
          </h1>
        );
      }
      // Bullet list items
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        const itemText = line.trim().replace(/^[-*]\s+/, '');
        return (
          <li key={idx} className="ml-4 list-disc text-slate-300 my-0.5 leading-relaxed">
            {formatInlineText(itemText)}
          </li>
        );
      }
      // Numbered list items
      if (/^\d+\.\s+/.test(line.trim())) {
        const itemText = line.trim().replace(/^\d+\.\s+/, '');
        return (
          <li key={idx} className="ml-4 list-decimal text-slate-300 my-0.5 leading-relaxed">
            {formatInlineText(itemText)}
          </li>
        );
      }
      // Empty line / paragraph break
      if (!line.trim()) {
        return <div key={idx} className="h-2" />;
      }
      // Standard paragraph
      return (
        <p key={idx} className="text-slate-200 leading-relaxed my-1">
          {formatInlineText(line)}
        </p>
      );
    });
  };

  // Formats inline bold (**text**), inline code (`code`), and [PAGE N] badges
  const formatInlineText = (text: string) => {
    // Replace [PAGE N] with clickable pill styling
    const parts = text.split(/(\[PAGE\s+\d+\]|\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('[PAGE') && part.endsWith(']')) {
        return (
          <span
            key={i}
            className="inline-flex items-center px-1.5 py-0.2 rounded bg-sky-950/80 border border-sky-500/50 text-sky-300 text-[11px] font-mono font-semibold mx-0.5"
          >
            {part}
          </span>
        );
      }
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-white">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={i} className="px-1 py-0.5 rounded bg-[#0d1527] border border-[#26344d] text-sky-400 font-mono text-[11px]">
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  return (
    <div className={`flex gap-3 px-4 py-4 w-full ${isAssistant ? 'bg-[#0f172a]/40' : 'bg-transparent'}`}>
      {/* Role Avatar */}
      <div className="shrink-0 mt-0.5">
        {isAssistant ? (
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-700 to-sky-500 flex items-center justify-center text-white shadow-sm shadow-sky-500/30">
            <Bot className="w-4 h-4" />
          </div>
        ) : (
          <div className="w-7 h-7 rounded-lg bg-[#1e293b] border border-[#334155] flex items-center justify-center text-slate-300">
            <User className="w-4 h-4" />
          </div>
        )}
      </div>

      {/* Message Content & Actions */}
      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-white">
              {isAssistant ? 'ResearchPilot Gemma 4' : 'Researcher'}
            </span>
            {isAssistant && message.model && (
              <span className="text-[10px] text-slate-400 bg-[#17243a] px-1.5 py-0.2 rounded font-mono">
                {message.model}
              </span>
            )}
            {isAssistant && message.duration_seconds && (
              <span className="text-[10px] text-sky-400/80">
                • {message.duration_seconds}s
              </span>
            )}
          </div>
        </div>

        {/* Formatted Text Body */}
        <div className="text-xs text-slate-200 font-normal leading-relaxed overflow-x-auto">
          {renderFormattedContent(message.content)}
        </div>

        {/* Citations Snippets / Summary Pills if available */}
        {isAssistant && message.citations && message.citations.length > 0 && (
          <div className="pt-2 flex flex-wrap items-center gap-1.5 border-t border-[#26344d]/50">
            <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
              <BookmarkCheck className="w-3 h-3 text-sky-400" />
              Verified Citations:
            </span>
            {message.citations.map((c) => (
              <button
                key={c.id}
                onClick={() => onOpenCitationPanel(message.citations)}
                className="text-[10px] font-medium bg-[#111b30] hover:bg-[#17243a] border border-sky-500/40 hover:border-sky-400 text-sky-300 px-2 py-0.5 rounded-full transition-all cursor-pointer"
              >
                {c.id} • Page {c.page_number}
              </button>
            ))}
          </div>
        )}

        {/* Assistant Actions Bar */}
        {isAssistant && (
          <div className="flex items-center gap-2 pt-1 text-slate-400">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-[11px] hover:text-white transition-colors px-1.5 py-0.5 rounded hover:bg-[#17243a]"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
            <button
              onClick={() => onDownloadMarkdown(message.content)}
              className="flex items-center gap-1 text-[11px] hover:text-white transition-colors px-1.5 py-0.5 rounded hover:bg-[#17243a]"
            >
              <Download className="w-3 h-3" />
              <span>Download (.md)</span>
            </button>
            {message.citations && message.citations.length > 0 && (
              <button
                onClick={() => onOpenCitationPanel(message.citations)}
                className="flex items-center gap-1 text-[11px] text-sky-400 hover:text-sky-300 transition-colors px-1.5 py-0.5 rounded hover:bg-[#17243a]"
              >
                <BookmarkCheck className="w-3 h-3" />
                <span>Inspect Citations</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
