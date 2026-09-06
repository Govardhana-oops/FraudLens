import React, { useState } from "react";
import {
  Settings,
  Save,
  Trash2,
  Shield,
  Sliders,
  Server,
  CheckCircle2,
} from "lucide-react";
import { useApp } from "@/context/AppContext";

export function SettingsPage() {
  const { settings, updateSettings, clearAllData } = useApp();

  const [form, setForm] = useState(settings);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    updateSettings(form);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  const handleClear = () => {
    if (window.confirm("Are you sure you want to clear all local screening and audit records? This cannot be undone.")) {
      clearAllData();
      alert("Local data cleared successfully.");
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slateText-50 tracking-tight">Console Configuration & Settings</h1>
        <p className="text-sm font-semibold text-slateText-300">
          Configure officer credentials, checkpoint identifiers, and inspection threshold tolerances
        </p>
      </div>

      {saveSuccess && (
        <div className="rounded-xl border border-accent-emerald/50 bg-accent-emerald/10 p-4 text-xs font-bold text-accent-emerald flex items-center gap-2 shadow-glow-emerald">
          <CheckCircle2 size={16} />
          <span>Settings saved successfully.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Officer & Terminal Info */}
        <div className="panel-3d p-6 space-y-4">
          <h2 className="text-base font-bold text-slateText-50 flex items-center gap-2">
            <Shield size={18} className="text-brand-teal" />
            <span>Officer & Checkpoint Station</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase text-slateText-300 mb-1">Officer Badge / ID</label>
              <input
                type="text"
                value={form.officerId}
                onChange={(e) => setForm({ ...form, officerId: e.target.value })}
                className="input-custom text-xs w-full"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase text-slateText-300 mb-1">Checkpoint Station ID</label>
              <input
                type="text"
                value={form.checkpointId}
                onChange={(e) => setForm({ ...form, checkpointId: e.target.value })}
                className="input-custom text-xs w-full"
                required
              />
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-bold uppercase text-slateText-300 mb-1">Terminal Location Name</label>
              <input
                type="text"
                value={form.checkpointName}
                onChange={(e) => setForm({ ...form, checkpointName: e.target.value })}
                className="input-custom text-xs w-full"
                required
              />
            </div>
          </div>
        </div>

        {/* Forensic Threshold Tolerances */}
        <div className="panel-3d p-6 space-y-4">
          <h2 className="text-base font-bold text-slateText-50 flex items-center gap-2">
            <Sliders size={18} className="text-brand-cyan" />
            <span>Forensic Sensitivity Thresholds</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase text-slateText-300 mb-1">
                OCR Confidence Threshold ({Math.round(form.ocrConfidenceThreshold * 100)}%)
              </label>
              <input
                type="range"
                min="0.5"
                max="0.95"
                step="0.05"
                value={form.ocrConfidenceThreshold}
                onChange={(e) => setForm({ ...form, ocrConfidenceThreshold: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase text-slateText-300 mb-1">
                Tamper Sensitivity ({Math.round(form.tamperingSensitivity * 100)}%)
              </label>
              <input
                type="range"
                min="0.2"
                max="0.8"
                step="0.05"
                value={form.tamperingSensitivity}
                onChange={(e) => setForm({ ...form, tamperingSensitivity: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase text-slateText-300 mb-1">
                Biometric Match Cutoff ({Math.round(form.faceMatchThreshold * 100)}%)
              </label>
              <input
                type="range"
                min="0.6"
                max="0.95"
                step="0.05"
                value={form.faceMatchThreshold}
                onChange={(e) => setForm({ ...form, faceMatchThreshold: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
          </div>
        </div>

        {/* Backend Endpoint */}
        <div className="panel-3d p-6 space-y-4">
          <h2 className="text-base font-bold text-slateText-50 flex items-center gap-2">
            <Server size={18} className="text-accent-amber" />
            <span>API Gateway Connection</span>
          </h2>

          <div>
            <label className="block text-xs font-bold uppercase text-slateText-300 mb-1">API Base URL</label>
            <input
              type="text"
              value={form.apiBaseUrl}
              onChange={(e) => setForm({ ...form, apiBaseUrl: e.target.value })}
              className="input-custom text-xs w-full font-mono"
              required
            />
            <p className="text-[11px] text-slateText-400 mt-1 font-medium">
              Default: http://localhost:8000 (Local) or Render Cloud URL
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <button
            type="submit"
            className="btn-primary w-full sm:w-auto px-8 py-3 text-xs uppercase tracking-wider font-bold flex items-center justify-center gap-2 shadow-glow-teal"
          >
            <Save size={16} />
            <span>Save Configuration</span>
          </button>

          <button
            type="button"
            onClick={handleClear}
            className="btn-danger w-full sm:w-auto text-xs uppercase tracking-wider flex items-center justify-center gap-2"
          >
            <Trash2 size={14} />
            <span>Clear Local Database</span>
          </button>
        </div>
      </form>
    </div>
  );
}
