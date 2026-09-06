import React from "react";
import { ScanFace, CheckCircle2, XCircle } from "lucide-react";
import type { FaceComparisonResult } from "@/types";

interface BiometricComparisonProps {
  comparison: FaceComparisonResult | null;
  data?: FaceComparisonResult | null;
}

export function BiometricComparison({ comparison, data }: BiometricComparisonProps) {
  const result = comparison || data;

  if (!result) {
    return (
      <div className="panel-3d p-6 text-center text-xs font-semibold text-slateText-400">
        No companion live face was provided for 1:1 biometric comparison.
      </div>
    );
  }

  return (
    <div className="panel-3d p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-canvas-600 pb-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slateText-100 flex items-center gap-2">
          <ScanFace size={16} className="text-accent-sky" />
          <span>Biometric 1:1 Facial Verification</span>
        </h2>
        <span
          className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${
            result.matched
              ? "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40"
              : "bg-accent-rose/20 text-accent-rose border-accent-rose/40"
          }`}
        >
          {result.matched ? "MATCH CONFIRMED" : "MISMATCH"}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="p-3.5 rounded-xl bg-canvas-850 border border-canvas-600">
          <div className="text-[11px] font-bold text-slateText-400 uppercase">Similarity</div>
          <div className="text-xl font-mono font-bold text-accent-sky mt-1">
            {Math.round(result.similarity_score * 100)}%
          </div>
          <div className="text-[10px] text-slateText-400 mt-1">Cosine similarity</div>
        </div>

        <div className="p-3.5 rounded-xl bg-canvas-850 border border-canvas-600">
          <div className="text-[11px] font-bold text-slateText-400 uppercase">Liveness</div>
          <div
            className={`text-xl font-mono font-bold mt-1 ${
              result.liveness_detected ? "text-accent-emerald" : "text-accent-rose"
            }`}
          >
            {Math.round(result.liveness_score * 100)}%
          </div>
          <div className="text-[10px] text-slateText-400 mt-1">Anti-spoofing score</div>
        </div>

        <div className="p-3.5 rounded-xl bg-canvas-850 border border-canvas-600">
          <div className="text-[11px] font-bold text-slateText-400 uppercase">Threshold</div>
          <div className="text-xl font-mono font-bold text-slateText-100 mt-1">
            {Math.round(result.threshold * 100)}%
          </div>
          <div className="text-[10px] text-slateText-400 mt-1">FAR &lt; 0.001 Standard</div>
        </div>
      </div>
    </div>
  );
}
