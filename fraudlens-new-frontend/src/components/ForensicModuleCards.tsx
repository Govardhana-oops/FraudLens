import React, { useState } from "react";
import {
  Eye,
  CheckCircle2,
  ShieldCheck,
  ShieldAlert,
  UserCheck,
  Lock,
  Copy,
  Check,
  ExternalLink,
} from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface ForensicModuleCardsProps {
  dossier: UnifiedScreeningDossier;
  onSelectTab?: (tab: string) => void;
}

export function ForensicModuleCards({ dossier, onSelectTab }: ForensicModuleCardsProps) {
  const [copiedHash, setCopiedHash] = useState(false);

  const fieldsCount = dossier.extracted_fields?.length || 0;
  const ocrConfidence =
    dossier.confidence_score !== undefined && dossier.confidence_score !== null
      ? Math.round(dossier.confidence_score * 100)
      : 0;

  const totalChecks = dossier.validation_checks?.length || 0;
  const passedChecks = dossier.validation_checks?.filter((c) => c.result === "PASS").length || 0;
  const validationPassed = totalChecks === 0 || passedChecks === totalChecks;

  const tamperRisk =
    dossier.tampering_analysis?.tampering_score !== undefined &&
    dossier.tampering_analysis?.tampering_score !== null
      ? Math.round(dossier.tampering_analysis.tampering_score * 100)
      : 0;
  const isTamperClean = tamperRisk < 35 && !dossier.tampering_analysis?.tampering_detected;

  const faceComp = dossier.face_comparison;
  const faceMatched = faceComp?.matched;
  const faceSimilarity = faceComp ? Math.round(faceComp.similarity_score * 100) : null;

  const hashShort = dossier.record_hash
    ? `${dossier.record_hash.substring(0, 8)}...${dossier.record_hash.substring(dossier.record_hash.length - 6)}`
    : "—";

  const handleCopyHash = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (dossier.record_hash) {
      navigator.clipboard.writeText(dossier.record_hash);
      setCopiedHash(true);
      setTimeout(() => setCopiedHash(false), 2000);
    }
  };

  const cards = [
    {
      id: "ocr",
      title: "OCR EXTRACTION",
      metric: `${fieldsCount} fields extracted`,
      subMetric: `Confidence: ${ocrConfidence}%`,
      status: ocrConfidence >= 70 ? "VERIFIED" : "REVIEW",
      statusColor: ocrConfidence >= 70 ? "emerald" : "amber",
      icon: Eye,
      tab: "fields",
    },
    {
      id: "validation",
      title: "VALIDATION",
      metric: `${passedChecks}/${totalChecks || 3} checksums valid`,
      subMetric: "ICAO 9303 Syntax",
      status: validationPassed ? "VALID" : "REVIEW",
      statusColor: validationPassed ? "emerald" : "amber",
      icon: CheckCircle2,
      tab: "forensics",
    },
    {
      id: "tamper",
      title: "TAMPER ANALYSIS",
      metric: `Risk: ${tamperRisk}%`,
      subMetric: isTamperClean ? "ELA / SIFT Clean" : "Anomaly Flagged",
      status: isTamperClean ? "CLEAN" : "SUSPICIOUS",
      statusColor: isTamperClean ? "emerald" : "rose",
      icon: isTamperClean ? ShieldCheck : ShieldAlert,
      tab: "forensics",
    },
    {
      id: "face",
      title: "FACE BIOMETRICS",
      metric: faceComp ? `Similarity: ${faceSimilarity}%` : "Specimen Linked",
      subMetric: faceComp ? "Live 1:1 Compared" : "Module 4 Ready",
      status: faceComp ? (faceMatched ? "MATCH" : "REVIEW") : "STANDBY",
      statusColor: faceComp ? (faceMatched ? "emerald" : "amber") : "sky",
      icon: UserCheck,
      tab: "forensics",
    },
    {
      id: "provenance",
      title: "SHA-256 PROVENANCE",
      metric: hashShort,
      subMetric: "Merkle Signed Ledger",
      status: "VERIFIED",
      statusColor: "cyan",
      icon: Lock,
      tab: "crypto",
      isHash: true,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
      {cards.map((card) => {
        const Icon = card.icon;
        const isEmerald = card.statusColor === "emerald";
        const isAmber = card.statusColor === "amber";
        const isRose = card.statusColor === "rose";

        let borderClasses = "border-canvas-600/90 hover:border-accent-sky/60";
        let badgeClasses = "bg-accent-sky/15 text-accent-sky border-accent-sky/30";
        let iconClasses = "bg-accent-sky/15 text-accent-sky border-accent-sky/30";

        if (isEmerald) {
          borderClasses = "border-accent-emerald/30 hover:border-accent-emerald/60 shadow-[0_0_12px_rgba(16,185,129,0.08)]";
          badgeClasses = "bg-accent-emerald/15 text-accent-emerald border-accent-emerald/40";
          iconClasses = "bg-accent-emerald/15 text-accent-emerald border-accent-emerald/30";
        } else if (isAmber) {
          borderClasses = "border-accent-amber/30 hover:border-accent-amber/60 shadow-[0_0_12px_rgba(245,158,11,0.08)]";
          badgeClasses = "bg-accent-amber/15 text-accent-amber border-accent-amber/40";
          iconClasses = "bg-accent-amber/15 text-accent-amber border-accent-amber/30";
        } else if (isRose) {
          borderClasses = "border-accent-rose/30 hover:border-accent-rose/60 shadow-[0_0_12px_rgba(239,68,68,0.08)]";
          badgeClasses = "bg-accent-rose/15 text-accent-rose border-accent-rose/40";
          iconClasses = "bg-accent-rose/15 text-accent-rose border-accent-rose/30";
        }

        return (
          <div
            key={card.id}
            onClick={() => onSelectTab && onSelectTab(card.tab)}
            className={`p-4 rounded-xl bg-canvas-850 border ${borderClasses} cursor-pointer transition-all duration-300 hover:translate-y-[-2px] flex flex-col justify-between group`}
          >
            {/* Top header */}
            <div className="flex items-center justify-between mb-3">
              <div className={`flex h-8 w-8 items-center justify-center rounded-lg border ${iconClasses}`}>
                <Icon size={16} />
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-black border uppercase tracking-wider ${badgeClasses}`}>
                {card.status}
              </span>
            </div>

            {/* Card Content */}
            <div>
              <span className="text-[10px] font-mono font-bold text-slateText-400 uppercase tracking-wider block">
                {card.title}
              </span>
              <div className="text-sm font-mono font-bold text-slateText-50 mt-1 truncate">
                {card.metric}
              </div>
              <div className="text-[11px] font-mono text-slateText-300 mt-0.5">
                {card.subMetric}
              </div>
            </div>

            {/* Bottom action / copy */}
            <div className="mt-3 pt-2 border-t border-canvas-700/60 flex items-center justify-between text-[10px] font-mono text-slateText-400 group-hover:text-accent-sky transition-colors">
              {card.isHash ? (
                <button
                  onClick={handleCopyHash}
                  className="flex items-center gap-1 hover:text-accent-emerald transition-colors"
                >
                  {copiedHash ? <Check size={11} className="text-accent-emerald" /> : <Copy size={11} />}
                  <span>{copiedHash ? "Copied" : "Copy Hash"}</span>
                </button>
              ) : (
                <span className="flex items-center gap-1">
                  <span>View Details</span>
                  <ExternalLink size={10} />
                </span>
              )}
              <span className="text-[9px] font-mono text-slateText-500">M0{cards.indexOf(card) + 1}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
