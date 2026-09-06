import React from "react";
import { ShieldCheck, ShieldAlert, Layers } from "lucide-react";
import type { TamperingAnalysis } from "@/types";

interface ForensicAnalysisCardProps {
  analysis: TamperingAnalysis | null;
}

export function ForensicAnalysisCard({ analysis }: ForensicAnalysisCardProps) {
  if (!analysis) {
    return (
      <div className="panel-3d p-6 text-center text-xs font-semibold text-slateText-400">
        No forensic tampering analysis available.
      </div>
    );
  }

  const isClean = !analysis.tampering_detected && (analysis.tampering_score || 0) < 0.35;

  return (
    <div className="panel-3d p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-canvas-600 pb-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slateText-100 flex items-center gap-2">
          <Layers size={16} className="text-brand-teal" />
          <span>Forensic Tamper Detection (Module 3)</span>
        </h2>
        <span
          className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${
            isClean
              ? "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40"
              : "bg-accent-rose/20 text-accent-rose border-accent-rose/40"
          }`}
        >
          {isClean ? "INTEGRITY INTACT" : "TAMPERING FLAGGED"}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3.5 rounded-xl bg-canvas-850 border border-canvas-600">
          <div className="text-[11px] font-bold text-slateText-400 uppercase">Tampering Risk</div>
          <div
            className={`text-xl font-mono font-bold mt-1 ${
              (analysis.tampering_score || 0) > 0.35 ? "text-accent-rose" : "text-accent-emerald"
            }`}
          >
            {Math.round((analysis.tampering_score || 0) * 100)}%
          </div>
          <div className="text-[10px] text-slateText-400 mt-1">Multi-signal neural score</div>
        </div>

        <div className="p-3.5 rounded-xl bg-canvas-850 border border-canvas-600">
          <div className="text-[11px] font-bold text-slateText-400 uppercase">ELA Disparity</div>
          <div className="text-xl font-mono font-bold text-slateText-100 mt-1">
            {analysis.ela_disparity_score !== undefined
              ? (analysis.ela_disparity_score * 100).toFixed(1) + "%"
              : "0.03"}
          </div>
          <div className="text-[10px] text-slateText-400 mt-1">Compression gradient</div>
        </div>

        <div className="p-3.5 rounded-xl bg-canvas-850 border border-canvas-600">
          <div className="text-[11px] font-bold text-slateText-400 uppercase">Copy-Move Match</div>
          <div
            className={`text-xl font-mono font-bold mt-1 ${
              analysis.copy_move_detected ? "text-accent-rose" : "text-accent-emerald"
            }`}
          >
            {analysis.copy_move_detected ? "DETECTED" : "CLEAR"}
          </div>
          <div className="text-[10px] text-slateText-400 mt-1">SIFT/ORB Keypoints</div>
        </div>
      </div>

      {analysis.anomalies_found && analysis.anomalies_found.length > 0 && (
        <div className="p-3 rounded-lg bg-accent-rose/10 border border-accent-rose/30 space-y-1">
          <div className="text-xs font-bold text-accent-rose">Detected Forensic Anomalies:</div>
          <ul className="list-disc list-inside text-xs text-slateText-200">
            {analysis.anomalies_found.map((a, i) => (
              <li key={i}>{a}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
