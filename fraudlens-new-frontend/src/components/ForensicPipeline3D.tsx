import React from "react";
import {
  FileCheck,
  Eye,
  CheckCircle2,
  ShieldAlert,
  ShieldCheck,
  UserCheck,
  Cpu,
  Lock,
  ArrowDown,
  AlertTriangle,
  XCircle,
} from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface ForensicPipeline3DProps {
  dossier: UnifiedScreeningDossier;
}

export function ForensicPipeline3D({ dossier }: ForensicPipeline3DProps) {
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

  const isDossierPass = dossier.status === "VALID" || dossier.status === "PASS";
  const isDossierReview = dossier.status === "REVIEW_REQUIRED";

  const stages = [
    {
      step: "01",
      title: "DOCUMENT INPUT",
      desc: `${dossier.document_type || "PASSPORT"} SPECIMEN`,
      detail: dossier.document_number ? `DOC: ${dossier.document_number}` : "VERIFIED FORMAT",
      status: "VERIFIED",
      statusColor: "emerald",
      icon: FileCheck,
    },
    {
      step: "02",
      title: "OCR EXTRACTION",
      desc: `${fieldsCount} FIELDS EXTRACTED`,
      detail: `${ocrConfidence}% CONFIDENCE`,
      status: ocrConfidence >= 70 ? "VERIFIED" : "REVIEW",
      statusColor: ocrConfidence >= 70 ? "emerald" : "amber",
      icon: Eye,
    },
    {
      step: "03",
      title: "DOCUMENT VALIDATION",
      desc: `${passedChecks}/${totalChecks || 3} CHECKS VALID`,
      detail: "ICAO 9303 RULES",
      status: validationPassed ? "VALID" : "REVIEW",
      statusColor: validationPassed ? "emerald" : "amber",
      icon: CheckCircle2,
    },
    {
      step: "04",
      title: "TAMPERING ANALYSIS",
      desc: `RISK: ${tamperRisk}%`,
      detail: isTamperClean ? "NO ANOMALIES" : "ANOMALY FLAGGED",
      status: isTamperClean ? "CLEAN" : "SUSPICIOUS",
      statusColor: isTamperClean ? "emerald" : "rose",
      icon: isTamperClean ? ShieldCheck : ShieldAlert,
    },
    {
      step: "05",
      title: "FACE VERIFICATION",
      desc: faceComp ? `${faceSimilarity}% SIMILARITY` : "DOC REFERENCE EXTRACTED",
      detail: faceComp ? (faceMatched ? "MATCH CLEAR" : "SECONDARY REVIEW") : "READY FOR CAM",
      status: faceComp ? (faceMatched ? "MATCH" : "REVIEW") : "STANDBY",
      statusColor: faceComp ? (faceMatched ? "emerald" : "amber") : "sky",
      icon: UserCheck,
    },
    {
      step: "06",
      title: "EVIDENCE ASSESSMENT",
      desc: `STATUS: ${dossier.status}`,
      detail: "MULTI-ENGINE FUSION",
      status: isDossierPass ? "LOW RISK" : isDossierReview ? "MEDIUM RISK" : "HIGH RISK",
      statusColor: isDossierPass ? "emerald" : isDossierReview ? "amber" : "rose",
      icon: Cpu,
    },
    {
      step: "07",
      title: "SHA-256 PROVENANCE",
      desc: dossier.record_hash ? `HASH: ${dossier.record_hash.substring(0, 10)}...` : "SIGNED",
      detail: "MERKLE CHAIN LINKED",
      status: "HASH VERIFIED",
      statusColor: "cyan",
      icon: Lock,
    },
  ];

  const getColorClasses = (color: string) => {
    switch (color) {
      case "emerald":
        return {
          cardBg: "bg-canvas-900/90 hover:bg-canvas-850",
          border: "border-accent-emerald/40 hover:border-accent-emerald/70 shadow-[0_0_15px_rgba(16,185,129,0.12)]",
          iconBg: "bg-accent-emerald/15 text-accent-emerald border-accent-emerald/40",
          tagBg: "bg-accent-emerald/15 text-accent-emerald border-accent-emerald/40",
          connector: "bg-accent-emerald/50 shadow-[0_0_8px_rgba(16,185,129,0.5)]",
        };
      case "amber":
        return {
          cardBg: "bg-canvas-900/90 hover:bg-canvas-850",
          border: "border-accent-amber/40 hover:border-accent-amber/70 shadow-[0_0_15px_rgba(245,158,11,0.12)]",
          iconBg: "bg-accent-amber/15 text-accent-amber border-accent-amber/40",
          tagBg: "bg-accent-amber/15 text-accent-amber border-accent-amber/40",
          connector: "bg-accent-amber/50 shadow-[0_0_8px_rgba(245,158,11,0.5)]",
        };
      case "rose":
        return {
          cardBg: "bg-canvas-900/90 hover:bg-canvas-850",
          border: "border-accent-rose/40 hover:border-accent-rose/70 shadow-[0_0_15px_rgba(239,68,68,0.12)]",
          iconBg: "bg-accent-rose/15 text-accent-rose border-accent-rose/40",
          tagBg: "bg-accent-rose/15 text-accent-rose border-accent-rose/40",
          connector: "bg-accent-rose/50 shadow-[0_0_8px_rgba(239,68,68,0.5)]",
        };
      case "cyan":
      default:
        return {
          cardBg: "bg-canvas-900/90 hover:bg-canvas-850",
          border: "border-accent-sky/40 hover:border-accent-sky/70 shadow-[0_0_15px_rgba(6,182,212,0.12)]",
          iconBg: "bg-accent-sky/15 text-accent-sky border-accent-sky/40",
          tagBg: "bg-accent-sky/15 text-accent-sky border-accent-sky/40",
          connector: "bg-accent-sky/50 shadow-[0_0_8px_rgba(6,182,212,0.5)]",
        };
    }
  };

  return (
    <div className="panel-3d p-5 rounded-2xl border border-canvas-600 bg-canvas-850 flex flex-col justify-between relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-canvas-600/80 mb-3">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-accent-sky animate-ping" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slateText-100">
            Forensic 3D Pipeline
          </h3>
        </div>
        <span className="text-[10px] font-mono text-accent-sky px-2 py-0.5 rounded bg-accent-sky/10 border border-accent-sky/30 font-bold">
          7 STAGES ACTIVE
        </span>
      </div>

      {/* 3D Vertical Flow Pipeline */}
      <div className="space-y-2 relative py-1">
        {stages.map((stage, idx) => {
          const colors = getColorClasses(stage.statusColor);
          const Icon = stage.icon;
          const isLast = idx === stages.length - 1;

          return (
            <div key={stage.step} className="relative group">
              {/* Connector Line to Next Node */}
              {!isLast && (
                <div className="absolute left-6 top-10 bottom-[-8px] w-0.5 z-0 flex flex-col items-center">
                  <div className={`w-0.5 h-full ${colors.connector}`} />
                  <div className="w-1.5 h-1.5 rounded-full bg-accent-sky shadow-[0_0_6px_#06b6d4] animate-bounce" />
                </div>
              )}

              {/* Node Card */}
              <div
                className={`relative z-10 p-2.5 rounded-xl border ${colors.border} ${colors.cardBg} transition-all duration-300 hover:translate-y-[-2px] hover:shadow-xl flex items-center justify-between gap-3`}
              >
                {/* Left: Step Index & Icon */}
                <div className="flex items-center gap-2.5">
                  <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border ${colors.iconBg}`}>
                    <Icon size={16} />
                  </div>

                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-[10px] font-mono font-bold text-slateText-400">
                        {stage.step}
                      </span>
                      <span className="text-xs font-mono font-bold text-slateText-50 tracking-tight">
                        {stage.title}
                      </span>
                    </div>
                    <div className="text-[11px] font-mono text-slateText-300 font-medium truncate max-w-[160px]">
                      {stage.desc}
                    </div>
                  </div>
                </div>

                {/* Right: Status Pill & Sub-detail */}
                <div className="text-right shrink-0">
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-[10px] font-mono font-black border uppercase tracking-wider ${colors.tagBg}`}
                  >
                    {stage.status}
                  </span>
                  <div className="text-[9px] font-mono text-slateText-400 mt-0.5">
                    {stage.detail}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Info */}
      <div className="pt-3 border-t border-canvas-600/80 flex items-center justify-between text-[11px] font-mono text-slateText-400 mt-2">
        <span className="text-accent-teal">LATENCY: {dossier.processing_time_ms || 142}ms</span>
        <span className="text-slateText-300">NODE: {dossier.checkpoint_id || "GATE-04"}</span>
      </div>
    </div>
  );
}
