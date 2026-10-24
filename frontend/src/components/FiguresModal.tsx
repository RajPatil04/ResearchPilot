import React, { useState } from 'react';
import { X, BarChart, Sparkles, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import type { DocumentMetadata, FigureAnalysisResponse } from '../types';

interface FiguresModalProps {
  isOpen: boolean;
  onClose: () => void;
  document: DocumentMetadata | null;
}

export const FiguresModal: React.FC<FiguresModalProps> = ({ isOpen, onClose, document }) => {
  const [pageNumber, setPageNumber] = useState(1);
  const [zoom, setZoom] = useState(1.5);
  const [question, setQuestion] = useState(
    'Explain the visible architecture or system flow diagram in detail. Identify axes and trends if a chart is shown.'
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FigureAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAnalyze = async () => {
    if (!document) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.analyzeFigure(document.id, pageNumber, question, zoom);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Figure analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const imageUrl = document ? api.getPageImageUrl(document.id, pageNumber, zoom) : '';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-[#111b30] border border-[#26344d] rounded-2xl w-full max-w-4xl max-h-[90vh] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-[#26344d] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <BarChart className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Multimodal Figure & Diagram Analysis</h2>
              <p className="text-[11px] text-slate-400">
                Render page image and inspect visually with Gemma 4
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

        {/* Content Body: Two Columns */}
        <div className="flex-1 overflow-y-auto p-5 text-xs grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Left: Rendered Page Image & Controls */}
          <div className="space-y-3 flex flex-col">
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <label className="text-[11px] font-semibold text-slate-300 block mb-1">
                  Select Page (1 - {document?.page_count || 1})
                </label>
                <input
                  type="number"
                  min={1}
                  max={document?.page_count || 1}
                  value={pageNumber}
                  onChange={(e) => setPageNumber(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full bg-[#0d1527] border border-[#26344d] rounded-xl px-3 py-1.5 text-white outline-none text-xs"
                />
              </div>
              <div className="w-32">
                <label className="text-[11px] font-semibold text-slate-300 block mb-1">
                  Zoom Level
                </label>
                <select
                  value={zoom}
                  onChange={(e) => setZoom(parseFloat(e.target.value))}
                  className="w-full bg-[#0d1527] border border-[#26344d] rounded-xl px-2.5 py-1.5 text-white outline-none text-xs"
                >
                  <option value={1.0}>1.0x (Fast)</option>
                  <option value={1.5}>1.5x (Crisp)</option>
                  <option value={2.0}>2.0x (Ultra)</option>
                </select>
              </div>
            </div>

            {/* Rendered Preview Box */}
            <div className="flex-1 min-h-[300px] max-h-[420px] bg-[#0d1527] border border-[#26344d] rounded-xl overflow-auto p-2 flex items-center justify-center">
              {document ? (
                <img
                  src={imageUrl}
                  alt={`Page ${pageNumber}`}
                  className="max-w-full h-auto rounded shadow-md object-contain"
                />
              ) : (
                <p className="text-slate-500">No document attached.</p>
              )}
            </div>
          </div>

          {/* Right: Inspection Question & Output */}
          <div className="space-y-3 flex flex-col">
            <div>
              <label className="text-[11px] font-semibold text-slate-300 block mb-1">
                Visual Inspection Inquiry
              </label>
              <textarea
                rows={3}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full bg-[#0d1527] border border-[#26344d] focus:border-amber-500 rounded-xl p-2.5 text-white text-xs outline-none resize-none leading-relaxed"
              />
            </div>

            <button
              onClick={handleAnalyze}
              disabled={loading || !document}
              className="w-full py-2 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-semibold rounded-xl shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{loading ? 'Gemma 4 is inspecting page...' : 'Analyze Page with Gemma 4'}</span>
            </button>

            {error && (
              <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <p className="text-[11px]">{error}</p>
              </div>
            )}

            {/* Analysis Output Box */}
            <div className="flex-1 min-h-[220px] bg-[#0d1527] border border-[#26344d] rounded-xl p-3.5 overflow-y-auto">
              {result ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between pb-1.5 border-b border-[#26344d] text-[10px] text-amber-400 font-semibold">
                    <span>Page {result.page_number} Findings</span>
                    <span>Multimodal Analysis</span>
                  </div>
                  <div className="prose-research whitespace-pre-wrap text-slate-200 text-xs leading-relaxed">
                    {result.analysis}
                  </div>
                </div>
              ) : (
                <p className="text-slate-500 text-center py-12 italic text-xs">
                  {loading
                    ? 'Examining visual elements, diagrams, flowcharts, and labels...'
                    : 'Click "Analyze Page with Gemma 4" to inspect visible charts and architectures.'}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#26344d] bg-[#0c1222] flex items-center justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-[#17243a] hover:bg-[#20304c] text-slate-300 text-xs font-semibold transition-all"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
