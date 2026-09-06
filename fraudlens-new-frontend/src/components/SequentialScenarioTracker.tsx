import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, ChevronRight } from "lucide-react";
import type { DemoScenario } from "@/utils/sampleDocs";
import type { UnifiedScreeningDossier } from "@/types";

interface SequentialScenarioTrackerProps {
  currentResult: UnifiedScreeningDossier | null;
  isScreening: boolean;
  activeAnimationStep: number; // 0 (idle), 1..5 (animating), 6 (finished)
  selectedScenario: DemoScenario;
  onSelectScenario: (scenario: DemoScenario) => void;
}

export function SequentialScenarioTracker({
  currentResult,
  isScreening,
  activeAnimationStep,
  selectedScenario,
  onSelectScenario,
}: SequentialScenarioTrackerProps) {
  const scenarios: { id: DemoScenario; step: number; label: string }[] = [
    { id: "valid_passport", step: 1, label: "Valid Passport" },
    { id: "expired_document", step: 2, label: "Expired Document" },
    { id: "ocr_uncertainty", step: 3, label: "OCR Uncertainty" },
    { id: "tampering_review", step: 4, label: "Tampering Review" },
    { id: "face_review", step: 5, label: "Face Review Required" },
  ];

  // Determine active/highlighted scenario based on REAL result
  const getActiveScenarioResult = (): DemoScenario | null => {
    if (!currentResult) return null;
    const status = currentResult.status?.toUpperCase() || "";
    if (status.includes("EXPIRED")) return "expired_document";
    if (status.includes("TAMPER") || (currentResult.tampering_analysis?.tampering_score || 0) > 0.35) return "tampering_review";
    if (status.includes("REVIEW") && currentResult.confidence_score < 0.85) return "ocr_uncertainty";
    if (status.includes("REVIEW") && currentResult.face_comparison && !currentResult.face_comparison.matched) return "face_review";
    if (status.includes("VALID") || status.includes("PASS") || status.includes("CLEAR")) return "valid_passport";
    if (status.includes("REVIEW")) return "ocr_uncertainty";
    return "valid_passport";
  };

  const detectedScenario = getActiveScenarioResult();

  return (
    <div className="p-3.5 rounded-2xl bg-gradient-to-r from-[#071322]/90 via-[#0A1B2E]/90 to-[#071322]/90 border border-cyan-900/60 shadow-xl backdrop-blur-md">
      <div className="flex items-center gap-2.5 flex-wrap">
        <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#7E9AB8] shrink-0 mr-1">
          Demo scenario:
        </span>

        <div className="flex items-center gap-2 flex-wrap flex-1">
          {scenarios.map((sc, idx) => {
            const isProcessingThis = isScreening && activeAnimationStep === sc.step;
            const isDetectedMatch = !isScreening && currentResult && detectedScenario === sc.id;
            const isSelected = selectedScenario === sc.id;

            // Compute styling
            let badgeClass = "border-slate-800/80 bg-[#040C16]/80 text-slate-300 hover:border-cyan-800 hover:text-white";
            let numberBg = "bg-slate-900 text-slate-400 border border-slate-700";
            let iconElement = null;

            if (isProcessingThis) {
              badgeClass = "border-cyan-400 bg-cyan-950/70 text-cyan-300 shadow-[0_0_15px_rgba(0,217,245,0.4)] animate-pulse scale-[1.02]";
              numberBg = "bg-cyan-500 text-slate-950 font-black";
            } else if (isDetectedMatch) {
              if (sc.id === "valid_passport") {
                badgeClass = "border-[#00F5A0] bg-[#00F5A0]/15 text-[#00F5A0] shadow-[0_0_18px_rgba(0,245,160,0.3)] font-bold";
                numberBg = "bg-[#00F5A0] text-slate-950 font-black";
                iconElement = <CheckCircle2 size={13} className="text-[#00F5A0]" />;
              } else if (sc.id === "expired_document" || sc.id === "tampering_review") {
                badgeClass = "border-rose-500 bg-rose-950/40 text-rose-400 shadow-[0_0_18px_rgba(239,68,68,0.3)] font-bold";
                numberBg = "bg-rose-500 text-slate-950 font-black";
                iconElement = <XCircle size={13} className="text-rose-400" />;
              } else {
                badgeClass = "border-amber-500 bg-amber-950/40 text-amber-400 shadow-[0_0_18px_rgba(245,158,11,0.3)] font-bold";
                numberBg = "bg-amber-500 text-slate-950 font-black";
                iconElement = <AlertTriangle size={13} className="text-amber-400" />;
              }
            } else if (isSelected && !currentResult) {
              badgeClass = "border-cyan-500/80 bg-cyan-950/40 text-cyan-300";
              numberBg = "bg-cyan-900 text-cyan-300 border border-cyan-500/60";
            }

            return (
              <React.Fragment key={sc.id}>
                <button
                  type="button"
                  onClick={() => onSelectScenario(sc.id)}
                  title={`Select or test ${sc.label}`}
                  className={`group relative flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs transition-all duration-250 border ${badgeClass}`}
                >
                  <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] shrink-0 ${numberBg}`}>
                    {sc.step}
                  </span>
                  <span className="tracking-tight whitespace-nowrap">{sc.label}</span>
                  {iconElement}
                </button>

                {/* Animated Arrow Connector */}
                {idx < scenarios.length - 1 && (
                  <div className="flex items-center text-cyan-800/80 shrink-0">
                    <ChevronRight size={13} className={isScreening && activeAnimationStep > sc.step ? "text-cyan-400 animate-pulse" : "text-cyan-900"} />
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
}
