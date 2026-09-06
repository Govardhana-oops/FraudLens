import React from "react";
import type { UnifiedScreeningDossier } from "@/types";

interface ActivityBarChartProps {
  records: UnifiedScreeningDossier[];
}

export function ActivityBarChart({ records }: ActivityBarChartProps) {
  const validCount = records.filter((r) => r.status === "VALID" || r.status === "PASS").length;
  const reviewCount = records.filter((r) => r.status === "REVIEW_REQUIRED").length;
  const expiredCount = records.filter(
    (r) =>
      r.status === "EXPIRED" ||
      r.status === "TAMPERED" ||
      r.status === "WATCHLIST_HIT" ||
      r.status === "INVALID"
  ).length;

  const maxVal = Math.max(validCount, reviewCount, expiredCount, 1);

  return (
    <div className="panel-3d p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-canvas-600 pb-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slateText-200">
          Inspection Clearance Distribution
        </h2>
        <span className="text-xs font-mono font-bold text-slateText-300">
          {records.length} Total Screenings
        </span>
      </div>

      <div className="space-y-3 pt-2">
        <div>
          <div className="flex justify-between text-xs font-bold mb-1">
            <span className="text-accent-emerald">Passed / Valid</span>
            <span className="font-mono text-slateText-100">{validCount}</span>
          </div>
          <div className="h-3 w-full rounded-full bg-canvas-850 overflow-hidden border border-canvas-600">
            <div
              className="h-full bg-accent-emerald rounded-full transition-all duration-500 shadow-glow-emerald"
              style={{ width: `${(validCount / maxVal) * 100}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs font-bold mb-1">
            <span className="text-accent-amber">Secondary Review Required</span>
            <span className="font-mono text-slateText-100">{reviewCount}</span>
          </div>
          <div className="h-3 w-full rounded-full bg-canvas-850 overflow-hidden border border-canvas-600">
            <div
              className="h-full bg-accent-amber rounded-full transition-all duration-500 shadow-glow-amber"
              style={{ width: `${(reviewCount / maxVal) * 100}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs font-bold mb-1">
            <span className="text-accent-rose">Expired / Tampered / Fraud</span>
            <span className="font-mono text-slateText-100">{expiredCount}</span>
          </div>
          <div className="h-3 w-full rounded-full bg-canvas-850 overflow-hidden border border-canvas-600">
            <div
              className="h-full bg-accent-rose rounded-full transition-all duration-500 shadow-glow-rose"
              style={{ width: `${(expiredCount / maxVal) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
