import React from "react";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Shield,
  FileCheck,
  Percent,
  Cpu,
} from "lucide-react";
import { formatDate } from "@/utils/formatters";
import type { UnifiedScreeningDossier } from "@/types";

interface EvidenceSummaryCardProps {
  dossier: UnifiedScreeningDossier;
}

export function EvidenceSummaryCard({ dossier }: EvidenceSummaryCardProps) {
  const status = dossier.status || "UNKNOWN";
  const isPass = status === "VALID" || status === "PASS";
  const isReview = status === "REVIEW_REQUIRED";
  const isFail =
    status === "INVALID" ||
    status === "EXPIRED" ||
    status === "TAMPERED" ||
    status === "FRAUD_DETECTED" ||
    status === "WATCHLIST_HIT";

  let borderClass = "border-canvas-600 bg-canvas-850";
  let iconClass = "text-accent-sky bg-accent-sky/20 border-accent-sky/40";
  let statusTitle = "DOCUMENT SCREENING COMPLETED";
  let statusDesc = "Multi-modal forensic analysis recorded in immutable audit dossier.";
  let badgeClass = "bg-accent-sky/20 text-accent-sky border-accent-sky/40";

  if (isPass) {
    borderClass = "border-accent-emerald/60 bg-accent-emerald/5 shadow-[0_0_25px_rgba(16,185,129,0.15)]";
    iconClass = "text-accent-emerald bg-accent-emerald/20 border-accent-emerald/40";
    statusTitle = "VALID DOCUMENT";
    statusDesc = "Verification checks completed with no critical tampering or syntactic issues.";
    badgeClass = "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/50";
  } else if (isReview) {
    borderClass = "border-accent-amber/60 bg-accent-amber/5 shadow-[0_0_25px_rgba(245,158,11,0.15)]";
    iconClass = "text-accent-amber bg-accent-amber/20 border-accent-amber/40";
    statusTitle = "REVIEW REQUIRED";
    statusDesc = "Verification identified potential anomalies or ambiguities requiring manual review.";
    badgeClass = "bg-accent-amber/20 text-accent-amber border-accent-amber/50";
  } else if (isFail) {
    borderClass = "border-accent-rose/60 bg-accent-rose/5 shadow-[0_0_25px_rgba(239,68,68,0.15)]";
    iconClass = "text-accent-rose bg-accent-rose/20 border-accent-rose/40";
    statusTitle = status.replace(/_/g, " ");
    statusDesc = "Critical security check failure, expiration, or physical tampering detected.";
    badgeClass = "bg-accent-rose/20 text-accent-rose border-accent-rose/50";
  }

  const confidenceScore =
    dossier.confidence_score !== undefined && dossier.confidence_score !== null
      ? Math.round(dossier.confidence_score * 100)
      : null;

  const tamperScore =
    dossier.tampering_analysis?.tampering_score !== undefined &&
    dossier.tampering_analysis?.tampering_score !== null
      ? Math.round(dossier.tampering_analysis.tampering_score * 100)
      : 0;

  return (
    <div className={`panel-3d p-6 rounded-2xl border transition-all duration-300 ${borderClass}`}>
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        {/* Left: Status Icon & Title */}
        <div className="flex items-start gap-4">
          <div className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border ${iconClass}`}>
            {isPass ? (
              <CheckCircle2 size={30} />
            ) : isReview ? (
              <AlertTriangle size={30} />
            ) : isFail ? (
              <XCircle size={30} />
            ) : (
              <Shield size={30} />
            )}
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <h2 className="text-xl font-mono font-black text-slateText-50 tracking-tight">
                {statusTitle}
              </h2>
              <span className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold border ${badgeClass}`}>
                {status}
              </span>
            </div>
            <p className="text-xs text-slateText-200 mt-1 font-medium max-w-xl">
              {statusDesc}
            </p>

            {/* Sub-details line */}
            <div className="flex flex-wrap items-center gap-4 mt-3 text-[11px] font-mono text-slateText-400">
              <span className="flex items-center gap-1.5">
                <FileCheck size={13} className="text-accent-teal" />
                <span>TYPE: <strong className="text-slateText-200">{dossier.document_type || "PASSPORT"}</strong></span>
              </span>
              <span className="flex items-center gap-1.5">
                <Cpu size={13} className="text-accent-sky" />
                <span>REF: <strong className="text-slateText-200">{dossier.screening_id || "—"}</strong></span>
              </span>
              <span className="flex items-center gap-1.5">
                <Clock size={13} className="text-slateText-400" />
                <span>SCREENED: <strong className="text-slateText-300">{formatDate(dossier.timestamp)}</strong></span>
              </span>
            </div>
          </div>
        </div>

        {/* Right: Key Metric Tiles */}
        <div className="flex items-center gap-3 self-end lg:self-center">
          <div className="px-4 py-3 rounded-xl bg-canvas-900 border border-canvas-600/80 text-right min-w-[110px]">
            <span className="text-[10px] font-mono font-bold text-slateText-400 uppercase tracking-wider">
              Confidence
            </span>
            <div className="text-2xl font-mono font-black text-accent-emerald mt-0.5">
              {confidenceScore !== null ? `${confidenceScore}%` : "—"}
            </div>
            <span className="text-[9px] font-mono text-slateText-400">OCR / FUSION</span>
          </div>

          <div className="px-4 py-3 rounded-xl bg-canvas-900 border border-canvas-600/80 text-right min-w-[110px]">
            <span className="text-[10px] font-mono font-bold text-slateText-400 uppercase tracking-wider">
              Tamper Risk
            </span>
            <div
              className={`text-2xl font-mono font-black mt-0.5 ${
                tamperScore > 35 ? "text-accent-rose" : "text-accent-emerald"
              }`}
            >
              {tamperScore}%
            </div>
            <span className="text-[9px] font-mono text-slateText-400">M3 FORENSICS</span>
          </div>
        </div>
      </div>
    </div>
  );
}
