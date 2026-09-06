import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, Shield, FileCheck, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import type { FaceComparisonResult } from "@/types";

interface BiometricResultBannerProps {
  result: FaceComparisonResult | null;
  docNumber?: string | null;
  holderName?: string | null;
  onReset?: () => void;
}

export function BiometricResultBanner({
  result,
  docNumber,
  holderName,
  onReset,
}: BiometricResultBannerProps) {
  if (!result) return null;

  const isMatched = result.matched;
  const isReview = !result.matched && result.similarity_score >= 0.48;
  const isNoMatch = !result.matched && result.similarity_score < 0.48;

  let bannerClass = "";
  let iconClass = "";
  let title = "";
  let description = "";
  let badgeText = "";
  let badgeClass = "";

  if (isMatched) {
    bannerClass = "border-accent-emerald/60 bg-accent-emerald/10 shadow-[0_0_30px_rgba(16,185,129,0.25)]";
    iconClass = "text-accent-emerald bg-accent-emerald/20 border-accent-emerald/40";
    title = "BIOMETRIC VERIFICATION: MATCHED";
    description = "Live traveler facial geometry is consistent with the reference document portrait.";
    badgeText = "VERIFIED • PROCEED";
    badgeClass = "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/50";
  } else if (isReview) {
    bannerClass = "border-accent-amber/60 bg-accent-amber/10 shadow-[0_0_30px_rgba(245,158,11,0.25)]";
    iconClass = "text-accent-amber bg-accent-amber/20 border-accent-amber/40";
    title = "BIOMETRIC VERIFICATION: REVIEW REQUIRED";
    description = "Biometric similarity score is near threshold or quality warrants manual inspection.";
    badgeText = "OFFICER REVIEW";
    badgeClass = "bg-accent-amber/20 text-accent-amber border-accent-amber/50";
  } else {
    bannerClass = "border-accent-rose/60 bg-accent-rose/10 shadow-[0_0_30px_rgba(239,68,68,0.25)]";
    iconClass = "text-accent-rose bg-accent-rose/20 border-accent-rose/40";
    title = "BIOMETRIC VERIFICATION: NO MATCH";
    description = "Live traveler facial embedding does not match the official reference document.";
    badgeText = "MISMATCH DETECTED";
    badgeClass = "bg-accent-rose/20 text-accent-rose border-accent-rose/50";
  }

  return (
    <div className={`panel-3d p-5 rounded-2xl border transition-all duration-500 ${bannerClass}`}>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border ${iconClass}`}>
            {isMatched ? (
              <CheckCircle2 size={24} />
            ) : isReview ? (
              <AlertTriangle size={24} />
            ) : (
              <XCircle size={24} />
            )}
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-base font-mono font-black text-slateText-50 tracking-tight">
                {title}
              </h2>
              <span className={`px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border ${badgeClass}`}>
                {badgeText}
              </span>
            </div>
            <p className="text-xs text-slateText-200 mt-1 font-medium">
              {description}
            </p>
            {(docNumber || holderName) && (
              <div className="flex items-center gap-3 mt-1 text-[11px] font-mono text-slateText-400">
                {docNumber && <span>DOC: <strong className="text-slateText-200">{docNumber}</strong></span>}
                {holderName && <span>NAME: <strong className="text-slateText-200">{holderName}</strong></span>}
                <span>SIMILARITY: <strong className="text-accent-teal">{(result.similarity_score * 100).toFixed(1)}%</strong></span>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 self-end md:self-center">
          <Link
            to="/screening"
            className="btn-secondary text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-1.5"
          >
            <FileCheck size={14} />
            <span>Document Screening</span>
          </Link>
          <Link
            to="/evidence"
            className="btn-primary text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-1.5 shadow-glowTeal"
          >
            <span>Evidence Dossier</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  );
}
