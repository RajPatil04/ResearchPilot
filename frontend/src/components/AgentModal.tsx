import React, { useState } from 'react';
import { X, Bot, Sparkles, AlertCircle, Play, CheckCircle2, Shield } from 'lucide-react';
import { api } from '../services/api';
import type { AgentInvestigationResponse, DocumentMetadata } from '../types';

interface AgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  document: DocumentMetadata | null;
}

export const AgentModal: React.FC<AgentModalProps> = ({ isOpen, onClose, document }) => {
  const [query, setQuery] = useState(
    'Examine the dataset size, preprocessing steps, and data splits used in the experiments.'
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentInvestigationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleLaunch = async () => {
    if (!document) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.runAgentInvestigation(query, document.id, 5);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Agent run failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-[#111b30] border border-[#26344d] rounded-2xl w-full max-w-3xl max-h-[85vh] shadow-2xl flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-5 py-4 border-b border-[#26344d] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Autonomous Research Agent</h2>
              <p className="text-[11px] text-slate-400">
                Multi-step tool execution with verifiable trace logging
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
        <div className="flex-1 overflow-y-auto p-5 text-xs text-slate-200 space-y-4">
          {/* Target Query */}
          <div>
            <label className="text-[11px] font-semibold text-slate-300 block mb-1.5">
              Investigation Target
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter investigation goal..."
                className="flex-1 bg-[#0d1527] border border-[#26344d] focus:border-cyan-500 rounded-xl px-3 py-2 text-white outline-none text-xs"
              />
              <button
                onClick={handleLaunch}
                disabled={loading || !document}
                className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-xl shadow-md transition-all flex items-center gap-1.5 shrink-0 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5" />
                <span>{loading ? 'Running...' : 'Launch Agent'}</span>
              </button>
            </div>
          </div>

          {/* Safety Sandbox notice */}
          <div className="p-2.5 rounded-xl bg-[#0e1528] border border-[#26344d] flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5 text-cyan-400 font-medium">
              <Shield className="w-3.5 h-3.5" />
              Registered Safe Tools Sandbox
            </span>
            <span className="font-mono text-[10px] text-slate-400">
              get_metadata • get_page_text • search_text • render_page
            </span>
          </div>

          {error && (
            <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <p className="text-[11px]">{error}</p>
            </div>
          )}

          {loading && (
            <div className="py-12 flex flex-col items-center justify-center space-y-3">
              <Sparkles className="w-7 h-7 text-cyan-400 animate-spin" />
              <p className="font-semibold text-xs text-white">Agent is executing inquiry steps & retrieving evidence...</p>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Tool Execution Trace */}
              <div>
                <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-2">
                  Tool Execution Trace ({result.tool_calls_count} steps)
                </h3>
                <div className="space-y-1.5">
                  {result.execution_trace.map((step) => (
                    <div
                      key={step.step}
                      className="p-2.5 rounded-xl bg-[#0d1527] border-l-2 border-cyan-400 border-t border-r border-b border-[#26344d] flex items-start justify-between"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 font-mono">
                            Step {step.step}
                          </span>
                          <code className="text-xs font-semibold text-white">{step.tool}</code>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-1">{step.summary}</p>
                      </div>
                      <span className="text-[10px] text-emerald-400 flex items-center gap-1 shrink-0 font-medium">
                        <CheckCircle2 className="w-3 h-3" /> success
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Synthesized Findings */}
              <div className="p-4 rounded-xl bg-[#0d1527] border border-[#26344d] space-y-2">
                <div className="flex items-center justify-between pb-1.5 border-b border-[#26344d] text-cyan-400 font-semibold text-xs">
                  <span>Synthesized Research Findings</span>
                  <span>Pages Cited: {result.referenced_pages.join(', ')}</span>
                </div>
                <div className="prose-research whitespace-pre-wrap leading-relaxed text-slate-200 text-xs">
                  {result.synthesized_answer}
                </div>
              </div>
            </div>
          )}
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
