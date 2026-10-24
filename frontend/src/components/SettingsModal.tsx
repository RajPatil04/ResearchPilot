import React, { useState } from 'react';
import {
  X,
  Key,
  CheckCircle2,
  AlertTriangle,
  Eye,
  EyeOff,
  ExternalLink,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';
import type { HealthResponse } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConnect: (apiKey: string, model: string, enableThinking: boolean) => Promise<boolean>;
  health: HealthResponse | null;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  onConnect,
  health,
}) => {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [model, setModel] = useState(health?.model || 'gemma-4-26b-a4b-it');
  const [customModel, setCustomModel] = useState('');
  const [enableThinking, setEnableThinking] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ success: boolean; msg: string } | null>(null);

  if (!isOpen) return null;

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      setStatusMessage({ success: false, msg: 'Please provide a valid Google AI Studio API key.' });
      return;
    }

    setIsVerifying(true);
    setStatusMessage(null);
    const targetModel = model === 'custom' ? customModel.trim() : model;

    try {
      const ok = await onConnect(apiKey.trim(), targetModel, enableThinking);
      if (ok) {
        setStatusMessage({ success: true, msg: `Verified & connected to ${targetModel} via Google Gen AI API.` });
      } else {
        setStatusMessage({ success: false, msg: 'Connection validation failed. Check API key permissions.' });
      }
    } catch (err: any) {
      setStatusMessage({ success: false, msg: err.message || 'Connection failed.' });
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-[#111b30] border border-[#26344d] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="px-5 py-4 border-b border-[#26344d] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
              <Key className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">Gemma 4 Configuration</h2>
              <p className="text-[11px] text-slate-400">Manage credentials & model parameters</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#17243a] transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleConnect} className="p-5 space-y-4 text-xs">
          {/* Status Alert if available */}
          {statusMessage && (
            <div
              className={`p-3 rounded-xl border flex items-start gap-2.5 ${
                statusMessage.success
                  ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'
                  : 'bg-red-950/40 border-red-500/50 text-red-300'
              }`}
            >
              {statusMessage.success ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              )}
              <div className="text-[11px] leading-relaxed">{statusMessage.msg}</div>
            </div>
          )}

          {/* API Key Field */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="font-semibold text-slate-200">Google AI Studio API Key</label>
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noreferrer"
                className="text-[10px] text-sky-400 hover:text-sky-300 flex items-center gap-0.5 font-medium"
              >
                Get API Key <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>
            <div className="relative">
              <input
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="AIzaSy..."
                className="w-full bg-[#0d1527] border border-[#26344d] focus:border-sky-500 rounded-xl px-3 py-2 text-white pr-9 outline-none text-xs"
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-2.5 top-2.5 text-slate-400 hover:text-white"
              >
                {showKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
              </button>
            </div>
            <p className="text-[10px] text-slate-500 mt-1">
              Transmitted securely to backend session memory. Never saved in localStorage or exposed to client code.
            </p>
          </div>

          {/* Model Selection */}
          <div>
            <label className="font-semibold text-slate-200 block mb-1.5">Gemma 4 Model Target</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-[#0d1527] border border-[#26344d] focus:border-sky-500 rounded-xl px-3 py-2 text-white outline-none text-xs"
            >
              <option value="gemma-4-26b-a4b-it">gemma-4-26b-a4b-it (Recommended Default)</option>
              <option value="gemma-4-31b-it">gemma-4-31b-it</option>
              <option value="custom">Custom Model Identifier...</option>
            </select>
            {model === 'custom' && (
              <input
                type="text"
                value={customModel}
                onChange={(e) => setCustomModel(e.target.value)}
                placeholder="Enter custom model string"
                className="mt-2 w-full bg-[#0d1527] border border-[#26344d] focus:border-sky-500 rounded-xl px-3 py-2 text-white outline-none text-xs"
              />
            )}
          </div>

          {/* Thinking Mode Toggle */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-[#0d1527] border border-[#26344d]">
            <div>
              <div className="flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                <span className="font-semibold text-white">Enable Gemma Thinking</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">
                Requests thinking_level='high' for deep methodological reasoning.
              </p>
            </div>
            <input
              type="checkbox"
              checked={enableThinking}
              onChange={(e) => setEnableThinking(e.target.checked)}
              className="w-4 h-4 rounded text-sky-600 focus:ring-0 bg-[#17243a] border-[#26344d] cursor-pointer"
            />
          </div>

          {/* Security & Anti-Substitution Note */}
          <div className="p-3 rounded-xl bg-[#0e1528] border border-sky-500/20 text-slate-400 space-y-1 text-[11px]">
            <div className="flex items-center gap-1.5 text-sky-400 font-semibold">
              <ShieldCheck className="w-3.5 h-3.5" />
              Strict Model Grounding Guarantee
            </div>
            <p>
              ResearchPilot AI strictly invokes Gemma 4. If an endpoint is unavailable or quota is exceeded, the actual API error is surfaced. No models are substituted silently.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-[#26344d]/60">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 rounded-xl bg-[#17243a] hover:bg-[#20304c] text-slate-300 font-semibold transition-all"
            >
              Close
            </button>
            <button
              type="submit"
              disabled={isVerifying}
              className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-sky-600 hover:from-blue-500 hover:to-sky-500 text-white font-semibold shadow-md shadow-blue-900/30 transition-all flex items-center gap-1.5"
            >
              {isVerifying ? 'Verifying...' : 'Test & Save Connection'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
