import React from "react";
import { Camera, ScanFace, ShieldAlert, Sliders, Cpu, CheckCircle2, Clock } from "lucide-react";

interface BiometricProcessingStagesProps {
  currentStage: number; // 0 to 6
  isProcessing: boolean;
  isComplete: boolean;
  hasResult: boolean;
}

interface StageConfig {
  id: number;
  label: string;
  sublabel: string;
  icon: React.ElementType;
}

export function BiometricProcessingStages({
  currentStage,
  isProcessing,
  isComplete,
  hasResult,
}: BiometricProcessingStagesProps) {
  const stages: StageConfig[] = [
    { id: 1, label: "Capture", sublabel: "Live Camera Stream", icon: Camera },
    { id: 2, label: "Face Detected", sublabel: "Spatial Bounding Box", icon: ScanFace },
    { id: 3, label: "Anti-Spoof Check", sublabel: "Presentation Attack PAD", icon: ShieldAlert },
    { id: 4, label: "Landmark Quality", sublabel: "Sharpness & Contrast", icon: Sliders },
    { id: 5, label: "Feature Compare", sublabel: "128-D Cosine Metric", icon: Cpu },
    { id: 6, label: "Final Result", sublabel: "Decision Determination", icon: CheckCircle2 },
  ];

  return (
    <div className="panel-3d p-4 bg-canvas-850/90 border-canvas-600/80 shadow-cardElevated">
      <div className="flex items-center justify-between mb-3 border-b border-canvas-700/60 pb-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-slateText-200">
            Pipeline Execution Flow
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-accent-sky/15 text-accent-sky border border-accent-sky/30">
            MODULE 4 STAGES
          </span>
        </div>
        <span className="text-[11px] font-mono text-slateText-400">
          {isProcessing ? "PROCESSING SEQUENTIAL STAGES..." : hasResult ? "ANALYSIS COMPLETED" : "READY TO EXECUTE"}
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
        {stages.map((stage) => {
          const Icon = stage.icon;
          const isActive = isProcessing && currentStage === stage.id;
          const isFinished = hasResult || currentStage > stage.id;
          const isPending = !hasResult && !isActive && currentStage < stage.id;

          let cardBorder = "border-canvas-700 bg-canvas-900/60 text-slateText-400";
          let iconColor = "text-slateText-500";
          let statusBadge = "IDLE";
          let badgeClass = "bg-canvas-800 text-slateText-500 border-canvas-700";

          if (isActive) {
            cardBorder = "border-accent-teal/80 bg-accent-teal/10 text-accent-teal shadow-[0_0_15px_rgba(45,212,191,0.25)] animate-pulse";
            iconColor = "text-accent-teal";
            statusBadge = "RUNNING";
            badgeClass = "bg-accent-teal/20 text-accent-teal border-accent-teal/40";
          } else if (isFinished) {
            cardBorder = "border-accent-emerald/40 bg-accent-emerald/5 text-slateText-100";
            iconColor = "text-accent-emerald";
            statusBadge = "DONE";
            badgeClass = "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40";
          }

          return (
            <div
              key={stage.id}
              className={`p-2.5 rounded-xl border transition-all duration-300 flex flex-col justify-between ${cardBorder}`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] font-mono font-bold text-slateText-400">
                  0{stage.id}
                </span>
                <span className={`px-1.5 py-0.2 rounded text-[9px] font-mono font-bold border ${badgeClass}`}>
                  {statusBadge}
                </span>
              </div>

              <div className="flex items-center gap-2 my-1">
                <Icon size={16} className={iconColor} />
                <span className="text-xs font-bold leading-tight truncate">{stage.label}</span>
              </div>

              <span className="text-[10px] font-mono text-slateText-400 truncate mt-1">
                {stage.sublabel}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
