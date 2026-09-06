import React from "react";
import type { UnifiedScreeningDossier } from "@/types";

interface ScreeningDistributionDonutProps {
  records: UnifiedScreeningDossier[];
}

export function ScreeningDistributionDonut({ records }: ScreeningDistributionDonutProps) {
  const validCount = records.filter((r) => r.status === "VALID" || r.status === "PASS").length;
  const reviewCount = records.filter((r) => r.status === "REVIEW_REQUIRED").length;
  const fraudCount = records.filter(
    (r) =>
      r.status === "EXPIRED" ||
      r.status === "TAMPERED" ||
      r.status === "WATCHLIST_HIT" ||
      r.status === "INVALID" ||
      r.status === "FRAUD_DETECTED"
  ).length;

  const total = records.length;
  const validPct = total > 0 ? Math.round((validCount / total) * 100) : 0;
  const reviewPct = total > 0 ? Math.round((reviewCount / total) * 100) : 0;
  const fraudPct = total > 0 ? Math.round((fraudCount / total) * 100) : 0;

  // Calculate SVG Donut Geometry
  const radius = 58;
  const circumference = 2 * Math.PI * radius; // ~364.42

  const validStroke = (validPct / 100) * circumference;
  const reviewStroke = (reviewPct / 100) * circumference;
  const fraudStroke = (fraudPct / 100) * circumference;

  const validOffset = 0;
  const reviewOffset = -validStroke;
  const fraudOffset = -(validStroke + reviewStroke);

  return (
    <div className="panel-3d p-5 flex flex-col justify-between border-cyan-900/60 bg-[#0A1624]/90 backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#20E3C2] shadow-[0_0_8px_#20E3C2]" />
          <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
            SCREENING DISTRIBUTION
          </h2>
        </div>
        <span className="text-[11px] font-mono text-[#5A7A9C]">
          {total} Processed
        </span>
      </div>

      {/* Chart and Legend Area */}
      <div className="flex flex-col sm:flex-row items-center justify-around gap-6 my-4">
        {/* SVG Donut Chart */}
        <div className="relative flex items-center justify-center shrink-0">
          <svg width="150" height="150" viewBox="0 0 150 150" className="transform -rotate-90">
            {/* Background Track */}
            <circle
              cx="75"
              cy="75"
              r={radius}
              fill="transparent"
              stroke="#07111B"
              strokeWidth="14"
            />

            {total === 0 ? (
              /* Empty State Dashed Track */
              <circle
                cx="75"
                cy="75"
                r={radius}
                fill="transparent"
                stroke="#1E4054"
                strokeWidth="12"
                strokeDasharray="4 6"
                opacity="0.5"
              />
            ) : (
              /* Real Data Segments */
              <>
                {/* Valid Segment */}
                {validCount > 0 && (
                  <circle
                    cx="75"
                    cy="75"
                    r={radius}
                    fill="transparent"
                    stroke="#10B981"
                    strokeWidth="14"
                    strokeDasharray={`${validStroke} ${circumference}`}
                    strokeDashoffset={validOffset}
                    className="transition-all duration-700 ease-out"
                  />
                )}
                {/* Review Segment */}
                {reviewCount > 0 && (
                  <circle
                    cx="75"
                    cy="75"
                    r={radius}
                    fill="transparent"
                    stroke="#F59E0B"
                    strokeWidth="14"
                    strokeDasharray={`${reviewStroke} ${circumference}`}
                    strokeDashoffset={reviewOffset}
                    className="transition-all duration-700 ease-out"
                  />
                )}
                {/* Fraud Segment */}
                {fraudCount > 0 && (
                  <circle
                    cx="75"
                    cy="75"
                    r={radius}
                    fill="transparent"
                    stroke="#EF4444"
                    strokeWidth="14"
                    strokeDasharray={`${fraudStroke} ${circumference}`}
                    strokeDashoffset={fraudOffset}
                    className="transition-all duration-700 ease-out"
                  />
                )}
              </>
            )}
          </svg>

          {/* Center Donut Text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
            <span className="text-2xl font-black font-mono text-white tracking-tight leading-none">
              {total}
            </span>
            <span className="text-[9px] font-mono font-bold text-[#5A7A9C] tracking-wider uppercase mt-1">
              TOTAL
            </span>
          </div>
        </div>

        {/* Breakdown Legend with Real Counts & Percentages */}
        <div className="flex-1 w-full space-y-3">
          {/* Valid */}
          <div className="p-2.5 rounded-lg bg-[#06101B]/80 border border-cyan-950/80 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-[#10B981] shrink-0" />
              <div>
                <div className="text-xs font-bold text-slate-200">Passed / Valid</div>
                <div className="text-[10px] font-mono text-slate-400">High Assurance</div>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono font-bold text-emerald-400">{validCount}</span>
              <span className="text-[10px] font-mono text-slate-400 ml-1.5">({validPct}%)</span>
            </div>
          </div>

          {/* Review Required */}
          <div className="p-2.5 rounded-lg bg-[#06101B]/80 border border-cyan-950/80 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-[#F59E0B] shrink-0" />
              <div>
                <div className="text-xs font-bold text-slate-200">Review Required</div>
                <div className="text-[10px] font-mono text-slate-400">Secondary Check</div>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono font-bold text-amber-400">{reviewCount}</span>
              <span className="text-[10px] font-mono text-slate-400 ml-1.5">({reviewPct}%)</span>
            </div>
          </div>

          {/* Expired / Fraud */}
          <div className="p-2.5 rounded-lg bg-[#06101B]/80 border border-cyan-950/80 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-sm bg-[#EF4444] shrink-0" />
              <div>
                <div className="text-xs font-bold text-slate-200">Expired / Fraud</div>
                <div className="text-[10px] font-mono text-slate-400">Tampered / Blocked</div>
              </div>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono font-bold text-rose-400">{fraudCount}</span>
              <span className="text-[10px] font-mono text-slate-400 ml-1.5">({fraudPct}%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
