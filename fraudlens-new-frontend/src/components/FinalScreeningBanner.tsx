import React from "react";
import { Link } from "react-router-dom";
import { CheckCircle2, AlertTriangle, XCircle, ArrowRight, Shield } from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface FinalScreeningBannerProps {
  currentResult: UnifiedScreeningDossier | null;
}

export function FinalScreeningBanner({ currentResult }: FinalScreeningBannerProps) {
  if (!currentResult) {
    return (
      <div className="p-4 rounded-2xl bg-[#040C16] border border-cyan-950/80 flex items-center justify-between text-xs text-[#5A7A9C]">
        <div className="flex items-center gap-2">
          <Shield size={16} className="text-cyan-700" />
          <span>Upload an identity credential to view final automated screening determination.</span>
        </div>
        <span className="font-mono text-[11px] text-cyan-800">AWAITING INPUT</span>
      </div>
    );
  }

  const status = (currentResult.status || "VALID").toUpperCase();
  const isClear = status === "VALID" || status === "PASS" || status === "CLEAR";
  const isExpired = status.includes("EXPIRED");
  const isTampered = status.includes("TAMPER");
  const isReview = status.includes("REVIEW") || status.includes("UNCERTAINTY") || status.includes("FLAG");

  let badgeLabel = "SCREENING RESULT: CLEAR";
  let badgeClass = "bg-emerald-950/90 border-[#00F5A0] text-[#00F5A0] shadow-[0_0_15px_rgba(0,245,160,0.3)]";
  let statusIcon = <CheckCircle2 size={16} className="text-[#00F5A0]" />;
  let explanation = "Document appears to be valid with no critical issues.";

  if (isExpired) {
    badgeLabel = "SCREENING RESULT: EXPIRED";
    badgeClass = "bg-amber-950/90 border-amber-500 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.3)]";
    statusIcon = <AlertTriangle size={16} className="text-amber-400" />;
    explanation = "Document expiration date prior to screening timestamp. Secondary review required.";
  } else if (isTampered) {
    badgeLabel = "SCREENING RESULT: TAMPERED";
    badgeClass = "bg-rose-950/90 border-rose-500 text-rose-400 shadow-[0_0_15px_rgba(239,68,68,0.3)]";
    statusIcon = <XCircle size={16} className="text-rose-400" />;
    explanation = "Forensic analysis detected structural or font anomalies. Document inspection flagged.";
  } else if (isReview) {
    badgeLabel = "SCREENING RESULT: REVIEW REQUIRED";
    badgeClass = "bg-amber-950/90 border-amber-500 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.3)]";
    statusIcon = <AlertTriangle size={16} className="text-amber-400" />;
    explanation = "Manual verification recommended by automated decision support engine.";
  }

  return (
    <div className="p-3.5 sm:p-4 rounded-2xl bg-gradient-to-r from-[#061828] via-[#041220] to-[#061828] border border-cyan-800/80 shadow-[0_0_25px_rgba(0,217,245,0.12)] flex flex-col sm:flex-row items-center justify-between gap-4 backdrop-blur-md">
      {/* Left: Glowing Badge */}
      <div className={`px-4 py-2 rounded-xl border flex items-center gap-2 text-xs font-mono font-black shrink-0 ${badgeClass}`}>
        {statusIcon}
        <span>{badgeLabel}</span>
      </div>

      {/* Center: Context Description */}
      <div className="text-xs text-slate-200 text-center sm:text-left flex-1 truncate font-medium">
        {explanation}
      </div>

      {/* Right: CTA Button */}
      <Link
        to={`/evidence?id=${currentResult.screening_id}`}
        className="px-4 py-2 rounded-xl bg-[#071F32] hover:bg-cyan-950 border border-cyan-700 hover:border-cyan-400 text-cyan-300 hover:text-white text-xs font-mono font-bold flex items-center gap-2 shadow-md transition-all shrink-0 group"
      >
        <span>View Full Report</span>
        <ArrowRight size={13} className="text-cyan-400 group-hover:translate-x-1 transition-transform" />
      </Link>
    </div>
  );
}
