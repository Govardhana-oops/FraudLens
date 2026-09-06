import React from "react";
import { CheckCircle2, CircleDashed } from "lucide-react";
import clsx from "clsx";

interface PipelineProgressProps {
  currentStep: number; // 1 to 5
}

export function PipelineProgress({ currentStep }: PipelineProgressProps) {
  const steps = [
    { title: "Module 1", subtitle: "Multi-Engine OCR" },
    { title: "Module 2", subtitle: "ICAO Validation" },
    { title: "Module 3", subtitle: "Forensic Tamper" },
    { title: "Module 4", subtitle: "Biometric 1:1" },
    { title: "Module 6/7", subtitle: "Audit Hashing" },
  ];

  return (
    <div className="panel-3d p-4 bg-canvas-850">
      <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-slateText-300 mb-3">
        <span>Processing Inspection Pipeline</span>
        <span className="font-mono text-brand-teal">Step {Math.min(currentStep, 5)} of 5</span>
      </div>

      <div className="grid grid-cols-5 gap-2">
        {steps.map((s, idx) => {
          const stepNum = idx + 1;
          const isDone = currentStep > stepNum;
          const isCurrent = currentStep === stepNum;

          return (
            <div
              key={s.title}
              className={clsx(
                "p-2.5 rounded-lg border text-center transition-all duration-150",
                isDone && "bg-accent-emerald/15 border-accent-emerald/50 text-accent-emerald",
                isCurrent && "bg-brand-teal/20 border-brand-teal text-brand-teal shadow-glow-teal animate-pulse",
                !isDone && !isCurrent && "bg-canvas-900 border-canvas-600 text-slateText-400"
              )}
            >
              <div className="flex items-center justify-center mb-1">
                {isDone ? (
                  <CheckCircle2 size={16} className="text-accent-emerald" />
                ) : isCurrent ? (
                  <CircleDashed size={16} className="text-brand-teal animate-spin" />
                ) : (
                  <span className="font-mono text-xs">{stepNum}</span>
                )}
              </div>
              <div className="text-[11px] font-bold">{s.title}</div>
              <div className="text-[9px] font-medium text-slateText-300 truncate">{s.subtitle}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
