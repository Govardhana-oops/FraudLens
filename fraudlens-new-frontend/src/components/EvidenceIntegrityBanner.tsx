import React from "react";
import { Link } from "react-router-dom";
import {
  ShieldCheck,
  AlertTriangle,
  XCircle,
  FileCheck,
  ArrowRight,
  Download,
  Printer,
  Lock,
} from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface EvidenceIntegrityBannerProps {
  dossier: UnifiedScreeningDossier;
  onExportJSON: () => void;
  onPrint: () => void;
}

export function EvidenceIntegrityBanner({
  dossier,
  onExportJSON,
  onPrint,
}: EvidenceIntegrityBannerProps) {
  const status = dossier.status || "UNKNOWN";
  const isPass = status === "VALID" || status === "PASS";
  const isReview = status === "REVIEW_REQUIRED";
  const isFail =
    status === "INVALID" ||
    status === "EXPIRED" ||
    status === "TAMPERED" ||
    status === "FRAUD_DETECTED" ||
    status === "WATCHLIST_HIT";

  let title = "EVIDENCE INTEGRITY: VERIFIED";
  let desc = "All multi-layer verification checks completed with no critical tampering or syntactic anomalies detected.";
  let borderClass = "border-accent-emerald/60 bg-accent-emerald/5 shadow-[0_0_30px_rgba(16,185,129,0.12)]";
  let iconClass = "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40";
  let Icon = ShieldCheck;

  if (isReview) {
    title = "EVIDENCE INTEGRITY: REVIEW REQUIRED";
    desc = "Verification pipeline identified ambiguous data or borderline checksums. Secondary officer inspection recommended.";
    borderClass = "border-accent-amber/60 bg-accent-amber/5 shadow-[0_0_30px_rgba(245,158,11,0.12)]";
    iconClass = "bg-accent-amber/20 text-accent-amber border-accent-amber/40";
    Icon = AlertTriangle;
  } else if (isFail) {
    title = `EVIDENCE INTEGRITY: ${status.replace(/_/g, " ")}`;
    desc = "High-risk tampering, expired validity, or critical check failure recorded in immutable forensic dossier.";
    borderClass = "border-accent-rose/60 bg-accent-rose/5 shadow-[0_0_30px_rgba(239,68,68,0.12)]";
    iconClass = "bg-accent-rose/20 text-accent-rose border-accent-rose/40";
    Icon = XCircle;
  } else if (!isPass) {
    title = "EVIDENCE INTEGRITY: INSUFFICIENT EVIDENCE";
    desc = "Dossier data is incomplete or requires additional document screening passes.";
    borderClass = "border-accent-sky/60 bg-accent-sky/5 shadow-[0_0_30px_rgba(6,182,212,0.12)]";
    iconClass = "bg-accent-sky/20 text-accent-sky border-accent-sky/40";
    Icon = FileCheck;
  }

  return (
    <div className={`panel-3d p-6 rounded-2xl border transition-all duration-300 ${borderClass}`}>
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        {/* Left: Status and message */}
        <div className="flex items-start gap-4">
          <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border ${iconClass}`}>
            <Icon size={26} />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-mono font-black text-slateText-50 tracking-tight">
                {title}
              </h2>
              <span className="flex items-center gap-1 text-[10px] font-mono text-accent-cyan font-bold px-2 py-0.5 rounded bg-accent-cyan/10 border border-accent-cyan/30">
                <Lock size={10} />
                <span>SHA-256 SIGNED</span>
              </span>
            </div>
            <p className="text-xs font-mono text-slateText-300 mt-1 max-w-2xl">
              {desc}
            </p>
          </div>
        </div>

        {/* Right: Functional Action buttons */}
        <div className="flex flex-wrap items-center gap-2.5 self-end lg:self-center">
          <button
            onClick={onExportJSON}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-canvas-900 hover:bg-canvas-800 border border-canvas-600 hover:border-accent-sky text-xs font-mono font-bold text-slateText-200 hover:text-accent-sky transition-all shadow-md"
          >
            <Download size={13} />
            <span>EXPORT DOSSIER</span>
          </button>

          <button
            onClick={onPrint}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-canvas-900 hover:bg-canvas-800 border border-canvas-600 hover:border-accent-sky text-xs font-mono font-bold text-slateText-200 hover:text-accent-sky transition-all shadow-md"
          >
            <Printer size={13} />
            <span>PRINT DOSSIER</span>
          </button>

          <Link
            to="/audit"
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-accent-sky to-accent-teal hover:opacity-90 text-canvas-950 text-xs font-mono font-black uppercase tracking-wider transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            <span>VIEW AUDIT LEDGER</span>
            <ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </div>
  );
}
