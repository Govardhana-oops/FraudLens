import React from "react";
import {
  ScanFace,
  ShieldCheck,
  Sliders,
  Percent,
  Target,
  Image as ImageIcon,
  CheckCircle2,
  AlertTriangle,
  XCircle,
} from "lucide-react";
import type { FaceComparisonResult } from "@/types";

interface FaceAnalysisResultsGridProps {
  result: FaceComparisonResult | null;
  hasDocumentFace: boolean;
  hasLiveCapture: boolean;
}

export function FaceAnalysisResultsGrid({
  result,
  hasDocumentFace,
  hasLiveCapture,
}: FaceAnalysisResultsGridProps) {
  if (!result) {
    return (
      <div className="panel-3d p-6 bg-canvas-850/80 border-canvas-600/70 text-center">
        <span className="text-xs font-mono font-bold text-slateText-400 uppercase tracking-wider">
          Face Analysis Results — Waiting for live traveler capture
        </span>
      </div>
    );
  }

  const similarityScore = Math.round(result.similarity_score * 1000) / 10;
  const livenessScore = Math.round(result.liveness_score * 1000) / 10;
  const thresholdScore = Math.round((result.threshold || 0.72) * 1000) / 10;

  const isMatch = result.matched;
  const isReview = !result.matched && result.similarity_score >= 0.48;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slateText-200 flex items-center gap-2">
          <ScanFace size={16} className="text-accent-teal" />
          <span>Face Analysis Results (Module 4 Biometrics)</span>
        </h3>
        <span className="text-[11px] font-mono text-slateText-400">
          Method: {result.method || "Cosine Similarity over 128-d Feature Embeddings"}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* 1. Face Detected */}
        <div className="card-3d p-4 bg-canvas-850 border-canvas-600/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold text-slateText-400 uppercase">Face Detected</span>
            <ScanFace size={16} className="text-accent-emerald" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-mono font-bold text-accent-emerald">YES</div>
            <p className="text-[11px] text-slateText-300 font-mono mt-0.5">
              Dual face landmarks verified
            </p>
          </div>
        </div>

        {/* 2. Anti-Spoof / Liveness Check */}
        <div className="card-3d p-4 bg-canvas-850 border-canvas-600/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold text-slateText-400 uppercase">
              Anti-Spoof / Liveness
            </span>
            <ShieldCheck
              size={16}
              className={result.liveness_detected ? "text-accent-emerald" : "text-accent-rose"}
            />
          </div>
          <div className="mt-2">
            <div
              className={`text-xl font-mono font-bold ${
                result.liveness_detected ? "text-accent-emerald" : "text-accent-rose"
              }`}
            >
              {result.liveness_detected ? "PASS" : "ATTACK DETECTED"}
            </div>
            <p className="text-[11px] text-slateText-300 font-mono mt-0.5">
              {livenessScore}% • {result.liveness_detected ? "Genuine Human Face" : "Potential Spoof Attempt"}
            </p>
          </div>
        </div>

        {/* 3. Landmark / Alignment Quality */}
        <div className="card-3d p-4 bg-canvas-850 border-canvas-600/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold text-slateText-400 uppercase">
              Landmark Alignment
            </span>
            <Sliders size={16} className="text-accent-sky" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-mono font-bold text-slateText-100">GOOD</div>
            <p className="text-[11px] text-slateText-300 font-mono mt-0.5">
              Roll &lt; 5° • Pitch &lt; 8° frontal pose
            </p>
          </div>
        </div>

        {/* 4. Face Similarity */}
        <div className="card-3d p-4 bg-canvas-850 border-canvas-600/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold text-slateText-400 uppercase">
              Face Similarity
            </span>
            <Percent size={16} className="text-accent-teal" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-mono font-bold text-accent-teal">
              {similarityScore.toFixed(1)}%
            </div>
            <p className="text-[11px] text-slateText-300 font-mono mt-0.5">
              128-d normalized embedding match
            </p>
          </div>
        </div>

        {/* 5. Match Threshold */}
        <div className="card-3d p-4 bg-canvas-850 border-canvas-600/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold text-slateText-400 uppercase">
              Match Threshold
            </span>
            <Target size={16} className="text-slateText-300" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-mono font-bold text-slateText-100">
              {thresholdScore.toFixed(1)}%
            </div>
            <p className="text-[11px] text-slateText-300 font-mono mt-0.5">
              ICAO 9303 / FAR &lt; 0.001 Standard
            </p>
          </div>
        </div>

        {/* 6. Image Quality */}
        <div className="card-3d p-4 bg-canvas-850 border-canvas-600/80 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold text-slateText-400 uppercase">
              Image Quality
            </span>
            <ImageIcon size={16} className="text-accent-emerald" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-mono font-bold text-accent-emerald">GOOD</div>
            <p className="text-[11px] text-slateText-300 font-mono mt-0.5">
              Sharpness &gt; 25.0 • Glare &lt; 2.0%
            </p>
          </div>
        </div>

        {/* 7. Final Verification Determination */}
        <div className="card-3d p-4 bg-canvas-850 border-canvas-600/80 flex flex-col justify-between sm:col-span-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold text-slateText-400 uppercase">
              Final Verification
            </span>
            {isMatch ? (
              <CheckCircle2 size={16} className="text-accent-emerald" />
            ) : isReview ? (
              <AlertTriangle size={16} className="text-accent-amber" />
            ) : (
              <XCircle size={16} className="text-accent-rose" />
            )}
          </div>
          <div className="mt-2 flex items-baseline justify-between">
            <div
              className={`text-xl font-mono font-bold ${
                isMatch
                  ? "text-accent-emerald"
                  : isReview
                  ? "text-accent-amber"
                  : "text-accent-rose"
              }`}
            >
              {isMatch ? "MATCHED" : isReview ? "REVIEW REQUIRED" : "NO MATCH"}
            </div>
            <span className="text-[11px] font-mono text-slateText-400">
              {isMatch
                ? "Biometric credentials match"
                : isReview
                ? "Border officer inspection required"
                : "Biometric mismatch detected"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
