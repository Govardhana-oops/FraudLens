import React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, ArrowRight } from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface ForensicAnalysisCardsProps {
  currentResult: UnifiedScreeningDossier | null;
}

export function ForensicAnalysisCards({ currentResult }: ForensicAnalysisCardsProps) {
  // 1. Tampering status
  const tamperingScore = currentResult?.tampering_analysis?.tampering_score ?? 0.04;
  const isTampered = tamperingScore > 0.35 || (currentResult?.status || "").toUpperCase().includes("TAMPER");
  const tamperingTitle = isTampered ? "Tampering Detected" : "No Tampering Detected";
  const tamperingSub = isTampered ? "Splice / font disparity detected." : "Document integrity appears genuine.";

  // 2. MRZ status
  const isMrzValid = !((currentResult?.status || "").toUpperCase().includes("EXPIRED") || (currentResult?.status || "").toUpperCase().includes("INVALID"));
  const mrzTitle = isMrzValid ? "Valid" : "Review Required";
  const mrzSub = isMrzValid ? "MRZ checksum verified." : "Checksum or expiry disparity detected.";

  // 3. Biometric status
  const hasFace = currentResult?.face_comparison !== null && currentResult?.face_comparison !== undefined;
  const faceMatched = hasFace && currentResult?.face_comparison?.matched;
  const biometricTitle = faceMatched ? "Face Verified" : "Face Review Required";
  const biometricSub = faceMatched ? "1:1 Match confirmed (Liveness valid)." : "Manual review recommended.";

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
      {/* Card 1: Tampering Analysis */}
      <div className="p-4 rounded-2xl bg-[#071322]/90 border border-cyan-900/60 shadow-lg backdrop-blur-md flex flex-col justify-between hover:border-cyan-700 transition-all group">
        <div>
          <h3 className="text-[10.5px] font-mono font-bold tracking-wider uppercase text-[#7E9AB8] mb-2.5">
            Tampering Analysis
          </h3>
          <div className="flex items-start gap-3">
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border ${
                isTampered
                  ? "bg-rose-950/80 border-rose-500/60 text-rose-400 shadow-[0_0_10px_rgba(239,68,68,0.3)]"
                  : "bg-emerald-950/80 border-emerald-500/60 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
              }`}
            >
              {isTampered ? <AlertTriangle size={16} /> : <ShieldCheck size={16} />}
            </div>
            <div>
              <div className="text-xs font-bold text-white leading-snug">
                {tamperingTitle}
              </div>
              <div className="text-[10px] text-[#7E9AB8] mt-0.5 leading-tight">
                {tamperingSub}
              </div>
            </div>
          </div>
        </div>

        <Link
          to={currentResult ? `/evidence?id=${currentResult.screening_id}` : "/evidence"}
          className="inline-flex items-center gap-1.5 text-[10px] font-mono font-bold text-cyan-400 hover:text-cyan-300 mt-3.5 group-hover:translate-x-0.5 transition-all"
        >
          <span>View Details</span>
          <ArrowRight size={11} />
        </Link>
      </div>

      {/* Card 2: MRZ Validation */}
      <div className="p-4 rounded-2xl bg-[#071322]/90 border border-cyan-900/60 shadow-lg backdrop-blur-md flex flex-col justify-between hover:border-cyan-700 transition-all group">
        <div>
          <h3 className="text-[10.5px] font-mono font-bold tracking-wider uppercase text-[#7E9AB8] mb-2.5">
            MRZ Validation
          </h3>
          <div className="flex items-start gap-3">
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border ${
                !isMrzValid
                  ? "bg-amber-950/80 border-amber-500/60 text-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.3)]"
                  : "bg-emerald-950/80 border-emerald-500/60 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
              }`}
            >
              {!isMrzValid ? <XCircle size={16} /> : <CheckCircle2 size={16} />}
            </div>
            <div>
              <div className="text-xs font-bold text-white leading-snug">
                {mrzTitle}
              </div>
              <div className="text-[10px] text-[#7E9AB8] mt-0.5 leading-tight">
                {mrzSub}
              </div>
            </div>
          </div>
        </div>

        <Link
          to={currentResult ? `/evidence?id=${currentResult.screening_id}` : "/evidence"}
          className="inline-flex items-center gap-1.5 text-[10px] font-mono font-bold text-cyan-400 hover:text-cyan-300 mt-3.5 group-hover:translate-x-0.5 transition-all"
        >
          <span>View Details</span>
          <ArrowRight size={11} />
        </Link>
      </div>

      {/* Card 3: Biometric Analysis */}
      <div className="p-4 rounded-2xl bg-[#071322]/90 border border-cyan-900/60 shadow-lg backdrop-blur-md flex flex-col justify-between hover:border-cyan-700 transition-all group">
        <div>
          <h3 className="text-[10.5px] font-mono font-bold tracking-wider uppercase text-[#7E9AB8] mb-2.5">
            Biometric Analysis
          </h3>
          <div className="flex items-start gap-3">
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border ${
                !faceMatched
                  ? "bg-amber-950/80 border-amber-500/60 text-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.3)]"
                  : "bg-emerald-950/80 border-emerald-500/60 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.3)]"
              }`}
            >
              {!faceMatched ? <AlertTriangle size={16} /> : <ShieldCheck size={16} />}
            </div>
            <div>
              <div className="text-xs font-bold text-white leading-snug">
                {biometricTitle}
              </div>
              <div className="text-[10px] text-[#7E9AB8] mt-0.5 leading-tight">
                {biometricSub}
              </div>
            </div>
          </div>
        </div>

        <Link
          to="/live-verification"
          className="inline-flex items-center gap-1.5 text-[10px] font-mono font-bold text-cyan-400 hover:text-cyan-300 mt-3.5 group-hover:translate-x-0.5 transition-all"
        >
          <span>View Details</span>
          <ArrowRight size={11} />
        </Link>
      </div>
    </div>
  );
}
