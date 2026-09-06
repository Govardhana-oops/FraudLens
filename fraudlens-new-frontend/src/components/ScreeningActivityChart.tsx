import React from "react";
import type { UnifiedScreeningDossier } from "@/types";
import { BarChart3 } from "lucide-react";

interface ScreeningActivityChartProps {
  records: UnifiedScreeningDossier[];
}

export function ScreeningActivityChart({ records }: ScreeningActivityChartProps) {
  // Aggregate real records into recent daily / hour intervals
  const bins: { label: string; count: number; valid: number; review: number; fraud: number }[] = [];

  if (records.length > 0) {
    // Generate buckets based on existing records
    const dateMap = new Map<string, { valid: number; review: number; fraud: number; count: number }>();

    // Process from oldest to newest
    const sorted = [...records].reverse();
    sorted.forEach((r) => {
      const d = r.timestamp ? new Date(r.timestamp) : new Date();
      const dateKey = d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
      const current = dateMap.get(dateKey) || { valid: 0, review: 0, fraud: 0, count: 0 };

      current.count += 1;
      if (r.status === "VALID" || r.status === "PASS") current.valid += 1;
      else if (r.status === "REVIEW_REQUIRED") current.review += 1;
      else current.fraud += 1;

      dateMap.set(dateKey, current);
    });

    dateMap.forEach((val, key) => {
      bins.push({ label: key, ...val });
    });
  }

  const maxCount = bins.length > 0 ? Math.max(...bins.map((b) => b.count), 1) : 1;

  return (
    <div className="panel-3d p-5 flex flex-col justify-between border-cyan-900/60 bg-[#0A1624]/90 backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-[#00D9F5]" />
          <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
            SCREENING ACTIVITY
          </h2>
        </div>
        <span className="text-[11px] font-mono text-[#5A7A9C]">
          Temporal Throughput
        </span>
      </div>

      {/* Main Chart Body */}
      {records.length === 0 ? (
        <div className="my-6 py-8 flex flex-col items-center justify-center text-center">
          <div className="w-10 h-10 rounded-xl bg-cyan-950/40 border border-cyan-800/40 flex items-center justify-center text-[#5A7A9C] mb-3">
            <BarChart3 className="w-5 h-5 opacity-60" />
          </div>
          <span className="text-sm font-bold text-slate-300">No screening activity yet</span>
          <span className="text-xs text-[#5A7A9C] max-w-xs mt-1">
            Activity throughput chart will populate automatically as documents are screened at this checkpoint.
          </span>
        </div>
      ) : (
        <div className="my-4 space-y-4">
          <div className="h-36 flex items-end justify-between gap-3 pt-4 px-2 border-b border-cyan-950/70">
            {bins.map((bin, i) => {
              const heightPct = Math.max(Math.round((bin.count / maxCount) * 100), 15);
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group">
                  <span className="text-[10px] font-mono text-cyan-400 font-bold opacity-0 group-hover:opacity-100 transition-opacity">
                    {bin.count}
                  </span>
                  <div className="w-full max-w-[28px] rounded-t-md overflow-hidden bg-slate-800 flex flex-col-reverse transition-all duration-300 group-hover:shadow-[0_0_12px_rgba(0,217,245,0.4)]"
                    style={{ height: `${heightPct}%` }}
                  >
                    {bin.fraud > 0 && (
                      <div
                        className="w-full bg-rose-500"
                        style={{ height: `${(bin.fraud / bin.count) * 100}%` }}
                        title={`Fraud: ${bin.fraud}`}
                      />
                    )}
                    {bin.review > 0 && (
                      <div
                        className="w-full bg-amber-500"
                        style={{ height: `${(bin.review / bin.count) * 100}%` }}
                        title={`Review: ${bin.review}`}
                      />
                    )}
                    {bin.valid > 0 && (
                      <div
                        className="w-full bg-emerald-500"
                        style={{ height: `${(bin.valid / bin.count) * 100}%` }}
                        title={`Valid: ${bin.valid}`}
                      />
                    )}
                  </div>
                  <span className="text-[10px] font-mono text-slate-400 truncate max-w-[40px]">
                    {bin.label}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="flex items-center justify-center gap-4 text-[10px] font-mono text-slate-400">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span>Valid</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span>Review</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-400" />
              <span>Flagged/Fraud</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
