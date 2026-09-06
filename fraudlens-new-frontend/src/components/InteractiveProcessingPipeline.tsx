import React from "react";
import {
  FileText,
  CheckCircle2,
  Code2,
  Search,
  ScanFace,
  Check,
  Loader2,
  Activity,
} from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface InteractiveProcessingPipelineProps {
  currentResult: UnifiedScreeningDossier | null;
  isScreening: boolean;
  pipelineStep: number; // 0 to 5
}

export function InteractiveProcessingPipeline({
  currentResult,
  isScreening,
  pipelineStep,
}: InteractiveProcessingPipelineProps) {
  const stages = [
    { step: 1, name: "OCR\nExtraction", icon: FileText },
    { step: 2, name: "Data\nValidation", icon: CheckCircle2 },
    { step: 3, name: "MRZ\nCheck", icon: Code2 },
    { step: 4, name: "Tamper\nAnalysis", icon: Search },
    { step: 5, name: "Face\nAnalysis", icon: ScanFace },
  ];

  const durationSec = currentResult
    ? ((currentResult.processing_time_ms || 2400) / 1000).toFixed(1)
    : "4.8";

  return (
    <div className="p-4 rounded-2xl bg-[#071322]/90 border border-cyan-900/60 shadow-lg backdrop-blur-md">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Left: Section Header & Connected Pipeline Nodes */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
              Processing Pipeline
            </h2>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2.5 overflow-x-auto pb-1">
            {stages.map((st, idx) => {
              const Icon = st.icon;
              const isCompleted = !isScreening && currentResult;
              const isCurrentActive = isScreening && pipelineStep === st.step;
              const isPassed = isScreening && pipelineStep > st.step;

              let iconBoxClass = "bg-[#040C16] border-slate-800 text-slate-500";
              let statusGlow = "";

              if (isCompleted || isPassed) {
                iconBoxClass = "bg-emerald-950/80 border-[#00F5A0] text-[#00F5A0] shadow-[0_0_12px_rgba(0,245,160,0.3)]";
              } else if (isCurrentActive) {
                iconBoxClass = "bg-cyan-950/90 border-cyan-400 text-cyan-300 shadow-[0_0_15px_rgba(0,217,245,0.4)] animate-pulse scale-105";
                statusGlow = "ring-2 ring-cyan-400/40";
              }

              return (
                <React.Fragment key={st.step}>
                  <div className="flex flex-col items-center gap-1.5 shrink-0 group">
                    <div
                      className={`w-9 h-9 rounded-xl border flex items-center justify-center transition-all duration-300 ${iconBoxClass} ${statusGlow}`}
                    >
                      {isCurrentActive ? (
                        <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
                      ) : (
                        <Icon className="w-4 h-4" />
                      )}
                    </div>
                    <div className="text-[9.5px] font-mono font-bold leading-tight text-center text-slate-300">
                      <span className="text-[9px] text-[#7E9AB8] block">
                        {st.step}
                      </span>
                      {st.name.split("\n").map((line, lIdx) => (
                        <span key={lIdx} className="block whitespace-nowrap">
                          {line}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Connecting Line / Arrow */}
                  {idx < stages.length - 1 && (
                    <div className="flex items-center mb-5 shrink-0 px-0.5">
                      <div
                        className={`w-3.5 sm:w-5 h-[2px] rounded-full transition-all duration-300 ${
                          isCompleted || isPassed
                            ? "bg-[#00F5A0] shadow-[0_0_8px_#00F5A0]"
                            : isCurrentActive
                            ? "bg-cyan-400 animate-pulse"
                            : "bg-slate-800"
                        }`}
                      />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Right: Glowing COMPLETE / Status Badge */}
        <div className="shrink-0 flex items-center self-end sm:self-center">
          {currentResult && !isScreening ? (
            <div className="px-4 py-2.5 rounded-xl bg-gradient-to-br from-[#062424] to-[#031414] border border-[#00F5A0] shadow-[0_0_20px_rgba(0,245,160,0.25)] flex flex-col items-center justify-center text-center">
              <div className="flex items-center gap-1.5 text-xs font-mono font-black text-[#00F5A0]">
                <Check className="w-4 h-4 stroke-[3]" />
                <span>COMPLETE</span>
              </div>
              <div className="text-[10px] font-mono text-slate-300 mt-0.5 whitespace-nowrap">
                Processing completed in {durationSec}s
              </div>
            </div>
          ) : isScreening ? (
            <div className="px-4 py-2.5 rounded-xl bg-cyan-950/60 border border-cyan-400 shadow-[0_0_15px_rgba(0,217,245,0.3)] flex flex-col items-center justify-center text-center animate-pulse">
              <div className="flex items-center gap-1.5 text-xs font-mono font-black text-cyan-300">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>SCREENING</span>
              </div>
              <div className="text-[10px] font-mono text-slate-300 mt-0.5">
                Executing Stage {pipelineStep || 1} of 5...
              </div>
            </div>
          ) : (
            <div className="px-4 py-2.5 rounded-xl bg-[#040C16] border border-cyan-950 flex flex-col items-center justify-center text-center opacity-70">
              <div className="text-xs font-mono font-bold text-slate-400">
                STANDBY
              </div>
              <div className="text-[10px] font-mono text-[#5A7A9C] mt-0.5">
                Upload credential to screen
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
