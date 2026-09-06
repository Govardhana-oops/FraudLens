import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from "lucide-react";
import type { ValidationCheck } from "@/types";

interface ValidationChecksListProps {
  checks: ValidationCheck[];
}

export function ValidationChecksList({ checks }: ValidationChecksListProps) {
  if (!checks || checks.length === 0) {
    return (
      <div className="panel-3d p-6 text-center text-xs font-semibold text-slateText-400">
        No rule-based validation checks available.
      </div>
    );
  }

  return (
    <div className="panel-3d p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-canvas-600 pb-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slateText-100">
          ICAO 9303 & Algorithmic Rule Checks
        </h2>
        <span className="rounded bg-canvas-850 px-2 py-0.5 text-xs font-mono font-bold text-accent-emerald border border-canvas-600">
          {checks.filter((c) => c.result === "PASS").length} / {checks.length} PASS
        </span>
      </div>

      <div className="space-y-2.5">
        {checks.map((check, idx) => {
          const isPass = check.result === "PASS";
          const isReview = check.result === "REVIEW_REQUIRED";

          return (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border flex items-start justify-between gap-3 ${
                isPass
                  ? "bg-canvas-850 border-canvas-600 hover:border-canvas-500"
                  : isReview
                  ? "bg-accent-amber/10 border-accent-amber/40"
                  : "bg-accent-rose/10 border-accent-rose/40"
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5 shrink-0">
                  {isPass ? (
                    <CheckCircle2 size={16} className="text-accent-emerald" />
                  ) : isReview ? (
                    <AlertTriangle size={16} className="text-accent-amber" />
                  ) : (
                    <XCircle size={16} className="text-accent-rose" />
                  )}
                </div>
                <div>
                  <div className="text-xs font-bold text-slateText-50">{check.rule_id}</div>
                  <div className="text-xs text-slateText-300 font-medium mt-0.5">{check.description}</div>
                </div>
              </div>

              <span
                className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border uppercase shrink-0 ${
                  isPass
                    ? "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40"
                    : isReview
                    ? "bg-accent-amber/20 text-accent-amber border-accent-amber/40"
                    : "bg-accent-rose/20 text-accent-rose border-accent-rose/40"
                }`}
              >
                {check.result}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
