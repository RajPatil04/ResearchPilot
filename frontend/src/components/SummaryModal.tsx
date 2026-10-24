import React, { useState, useEffect } from 'react';
import { X, FileSpreadsheet, Download, Sparkles, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import type { DocumentMetadata, SummaryResponse } from '../types';

interface SummaryModalProps {
  isOpen: boolean;
  onClose: () => void;
  document: DocumentMetadata | null;
}

export const SummaryModal: React.FC<SummaryModalProps> = ({ isOpen, onClose, document }) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<SummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && document && !data) {
      handleGenerate();
    }
  }, [isOpen, document]);

  const handleGenerate = async () => {
    if (!document) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.generateSummary(document.id);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate summary.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!data || !document) return;
    const blob = await api.exportArtifact(document.title, 'summary', data.summary, document.id);
    const url = URL.createObjectURL(blob);
    const a = window.document.createElement('a');
    a.href = url;
    a.download = `Summary_${document.title.slice(0, 24)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-[#111b30] border border-[#26344d] rounded-2xl w-full max-w-3xl max-h-[85vh] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-[#26344d] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">12-Point Structured Research Summary</h2>
              <p className="text-[11px] text-slate-400 truncate max-w-lg">
                {document?.title || 'Target Research Paper'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#17243a] transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 text-xs text-slate-200">
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 space-y-3">
              <Sparkles className="w-8 h-8 text-sky-400 animate-spin" />
              <p className="text-xs font-semibold text-white">Gemma 4 is reading and compiling the structured summary...</p>
              <p className="text-[11px] text-slate-400">Extracting objectives, methodology, exact quantitative findings, and limitations.</p>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 flex items-start gap-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-xs">Summary Generation Error</p>
                <p className="text-[11px] mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {data && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-[#0e1528] border border-[#26344d] text-[11px] text-slate-400">
                <span>Model: <strong className="text-sky-300">Gemma 4</strong></span>
                <span>⏱️ {data.duration_seconds}s</span>
                <span>{data.citations.length} Verified Evidence Points</span>
              </div>
              <div className="prose-research whitespace-pre-wrap leading-relaxed">
                {data.summary}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#26344d] bg-[#0c1222] flex items-center justify-between shrink-0">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="text-xs text-sky-400 hover:text-sky-300 font-medium"
          >
            Regenerate Summary
          </button>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-lg bg-[#17243a] hover:bg-[#20304c] text-slate-300 text-xs font-semibold transition-all"
            >
              Close
            </button>
            {data && (
              <button
                onClick={handleDownload}
                className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition-all flex items-center gap-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download (.md)</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
