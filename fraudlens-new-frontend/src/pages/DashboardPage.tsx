import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import {
  FileCheck2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  RefreshCw,
  PlusCircle,
  ShieldAlert,
  ArrowRight,
  ExternalLink,
  Shield,
  Layers,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { ScreeningDistributionDonut } from "@/components/ScreeningDistributionDonut";
import { ScreeningActivityChart } from "@/components/ScreeningActivityChart";
import { DocumentTypeBreakdown } from "@/components/DocumentTypeBreakdown";
import { SystemStatusPanel } from "@/components/SystemStatusPanel";
import { formatDate, truncateMiddle } from "@/utils/formatters";

export function DashboardPage() {
  const { stats, records, refreshData, isLiveConnected, settings } = useApp();

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const total = stats.totalScreened;
  const validPct = total > 0 ? Math.round((stats.validCount / total) * 100) : 0;
  const reviewPct = total > 0 ? Math.round((stats.reviewRequiredCount / total) * 100) : 0;
  const fraudPct = total > 0 ? Math.round((stats.expiredCount / total) * 100) : 0;

  const recentRecords = records.slice(0, 8);
  const mostRecent = records.length > 0 ? records[0] : null;
  const watchlistHits = records.filter(
    (r) =>
      r.status === "WATCHLIST_HIT" ||
      r.status === "TAMPERED" ||
      r.status === "FRAUD_DETECTED"
  );

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto select-none">
      {/* ============================================================ */}
      {/* 1. TOP WELCOME & MAIN TITLE                                  */}
      {/* ============================================================ */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cyan-950/60 pb-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-black text-white tracking-tight">
              Border Operations Dashboard
            </h1>
            <span className="rounded-md bg-[#092232] px-2.5 py-0.5 text-xs font-mono font-bold text-[#20E3C2] border border-[#20E3C2]/40 shadow-[0_0_10px_rgba(32,227,194,0.2)]">
              {settings.checkpointId || "GATE-04"}
            </span>
          </div>
          <p className="text-xs font-medium text-[#7E9AB8] mt-1">
            Real-time screening intelligence, forensic metrics, and checkpoint throughput.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => refreshData()}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#091827] border border-cyan-900/60 hover:border-[#20E3C2]/60 text-xs font-bold text-slate-200 hover:text-white transition-all shadow-sm"
          >
            <RefreshCw size={14} className="text-cyan-400" />
            <span>Sync Stats</span>
          </button>

          <Link
            to="/screening"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#00F5A0] to-[#00D9F5] text-slate-950 font-black text-xs uppercase tracking-wider shadow-[0_0_20px_rgba(0,245,160,0.4)] hover:shadow-[0_0_30px_rgba(0,245,160,0.6)] hover:scale-105 active:scale-95 transition-all"
          >
            <PlusCircle size={15} className="stroke-[2.5]" />
            <span>New Screening</span>
          </Link>
        </div>
      </div>

      {/* Security Alert Banner (if any flagged documents) */}
      {watchlistHits.length > 0 && (
        <div className="rounded-xl border border-rose-500/50 bg-rose-950/20 p-4 shadow-[0_0_20px_rgba(239,68,68,0.2)] flex items-start gap-3.5">
          <ShieldAlert className="h-6 w-6 text-rose-500 shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-xs font-mono font-bold text-rose-400 uppercase tracking-wider">
              HIGH-RISK FORENSIC ALERT ({watchlistHits.length} FLAGGED INCIDENT{watchlistHits.length > 1 ? "S" : ""})
            </h3>
            <p className="text-xs text-slate-300 mt-1">
              One or more documents screened at this terminal exhibited severe tampering anomalies or watchlist matches.
              Inspect the respective forensic evidence dossiers immediately.
            </p>
          </div>
          <Link
            to={`/evidence?id=${watchlistHits[0].screening_id}`}
            className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs uppercase tracking-wider shrink-0 transition-colors shadow-[0_0_12px_rgba(239,68,68,0.4)]"
          >
            Inspect Alert
          </Link>
        </div>
      )}

      {/* ============================================================ */}
      {/* 2. TOP 6 COMPACT METRIC CARDS (3D DEPTH & NEON ACCENTS)     */}
      {/* ============================================================ */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* CARD 1: TOTAL SCREENED */}
        <div className="h-[140px] p-4 rounded-xl bg-[#091728]/90 border border-cyan-900/60 hover:border-[#00D9F5]/70 hover:shadow-[0_0_20px_rgba(0,217,245,0.25)] hover:-translate-y-0.5 transition-all duration-200 flex flex-col justify-between group backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold uppercase text-[#5A7A9C] tracking-wider">
              TOTAL SCREENED
            </span>
            <div className="w-7 h-7 rounded-lg bg-cyan-950/60 border border-cyan-800 flex items-center justify-center text-[#00D9F5] group-hover:text-white transition-colors">
              <FileCheck2 size={15} />
            </div>
          </div>
          <div>
            <div className="text-3xl font-black font-mono text-white tracking-tight leading-none">
              {stats.totalScreened}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1.5 truncate">
              All processed credentials
            </div>
          </div>
        </div>

        {/* CARD 2: VALID / PASSED */}
        <div className="h-[140px] p-4 rounded-xl bg-[#091728]/90 border border-emerald-950 hover:border-emerald-500/70 hover:shadow-[0_0_20px_rgba(16,185,129,0.25)] hover:-translate-y-0.5 transition-all duration-200 flex flex-col justify-between group backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold uppercase text-emerald-400 tracking-wider">
              VALID / PASSED
            </span>
            <div className="w-7 h-7 rounded-lg bg-emerald-950/60 border border-emerald-800 flex items-center justify-center text-emerald-400 group-hover:text-white transition-colors">
              <CheckCircle2 size={15} />
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black font-mono text-white tracking-tight leading-none">
                {stats.validCount}
              </span>
              <span className="text-xs font-mono font-bold text-emerald-400">
                {validPct}%
              </span>
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1.5 truncate">
              High-assurance clearance
            </div>
          </div>
        </div>

        {/* CARD 3: REVIEW REQUIRED */}
        <div className="h-[140px] p-4 rounded-xl bg-[#091728]/90 border border-amber-950 hover:border-amber-500/70 hover:shadow-[0_0_20px_rgba(245,158,11,0.25)] hover:-translate-y-0.5 transition-all duration-200 flex flex-col justify-between group backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold uppercase text-amber-400 tracking-wider">
              REVIEW REQUIRED
            </span>
            <div className="w-7 h-7 rounded-lg bg-amber-950/60 border border-amber-800 flex items-center justify-center text-amber-400 group-hover:text-white transition-colors">
              <AlertTriangle size={15} />
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black font-mono text-white tracking-tight leading-none">
                {stats.reviewRequiredCount}
              </span>
              <span className="text-xs font-mono font-bold text-amber-400">
                {reviewPct}%
              </span>
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1.5 truncate">
              Secondary inspection
            </div>
          </div>
        </div>

        {/* CARD 4: EXPIRED / FRAUD */}
        <div className="h-[140px] p-4 rounded-xl bg-[#091728]/90 border border-rose-950 hover:border-rose-500/70 hover:shadow-[0_0_20px_rgba(239,68,68,0.25)] hover:-translate-y-0.5 transition-all duration-200 flex flex-col justify-between group backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold uppercase text-rose-400 tracking-wider">
              EXPIRED / FRAUD
            </span>
            <div className="w-7 h-7 rounded-lg bg-rose-950/60 border border-rose-800 flex items-center justify-center text-rose-400 group-hover:text-white transition-colors">
              <XCircle size={15} />
            </div>
          </div>
          <div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-black font-mono text-white tracking-tight leading-none">
                {stats.expiredCount}
              </span>
              <span className="text-xs font-mono font-bold text-rose-400">
                {fraudPct}%
              </span>
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1.5 truncate">
              Tampered or flagged
            </div>
          </div>
        </div>

        {/* CARD 5: AVG LATENCY */}
        <div className="h-[140px] p-4 rounded-xl bg-[#091728]/90 border border-blue-950 hover:border-blue-500/70 hover:shadow-[0_0_20px_rgba(59,130,246,0.25)] hover:-translate-y-0.5 transition-all duration-200 flex flex-col justify-between group backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold uppercase text-blue-400 tracking-wider">
              AVG LATENCY
            </span>
            <div className="w-7 h-7 rounded-lg bg-blue-950/60 border border-blue-800 flex items-center justify-center text-blue-400 group-hover:text-white transition-colors">
              <Clock size={15} />
            </div>
          </div>
          <div>
            <div className="text-3xl font-black font-mono text-white tracking-tight leading-none">
              {stats.avgLatencyMs > 0 ? `${stats.avgLatencyMs}ms` : "—"}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1.5 truncate">
              End-to-end pipeline speed
            </div>
          </div>
        </div>

        {/* CARD 6: SYNC HEALTH */}
        <div className="h-[140px] p-4 rounded-xl bg-[#091728]/90 border border-teal-950 hover:border-teal-500/70 hover:shadow-[0_0_20px_rgba(45,212,191,0.25)] hover:-translate-y-0.5 transition-all duration-200 flex flex-col justify-between group backdrop-blur-md">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-mono font-bold uppercase text-teal-400 tracking-wider">
              SYNC HEALTH
            </span>
            <div className="w-7 h-7 rounded-lg bg-teal-950/60 border border-teal-800 flex items-center justify-center text-teal-400 group-hover:text-white transition-colors">
              <RefreshCw size={15} />
            </div>
          </div>
          <div>
            <div className="text-2xl font-black font-mono text-white tracking-tight leading-none truncate">
              {isLiveConnected ? "100% ONLINE" : "BUFFER"}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1.5 truncate">
              {isLiveConnected ? "Connected to HQ" : "Offline buffer mode"}
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 3. VISUAL ANALYTICS ROW (DONUT + ACTIVITY + DOC TYPES)       */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {/* 1. Screening Distribution Donut */}
        <ScreeningDistributionDonut records={records} />

        {/* 2. Screening Activity Graph */}
        <ScreeningActivityChart records={records} />

        {/* 3. Document Type Breakdown */}
        <DocumentTypeBreakdown records={records} />
      </div>

      {/* ============================================================ */}
      {/* 4. OPERATIONS, DIAGNOSTICS & MOST RECENT SCREENING           */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* CHECKPOINT OPERATIONS PANEL */}
        <div className="panel-3d p-5 flex flex-col justify-between border-cyan-900/60 bg-[#0A1624]/90 backdrop-blur-md">
          <div>
            <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3 mb-3">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-[#20E3C2]" />
                <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
                  CHECKPOINT OPERATIONS
                </h2>
              </div>
              <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/40">
                ACTIVE
              </span>
            </div>

            <div className="space-y-2.5">
              <div className="p-2.5 rounded-lg bg-[#06101B]/80 border border-cyan-950 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-slate-200">Officer Assigned</div>
                  <div className="text-[11px] font-mono text-cyan-400 font-bold">
                    {settings.officerId || "CP-0082"} ({settings.officerName || "Officer"})
                  </div>
                </div>
                <Link to="/settings" className="text-[11px] font-mono text-[#20E3C2] hover:underline font-bold">
                  Edit
                </Link>
              </div>

              <div className="p-2.5 rounded-lg bg-[#06101B]/80 border border-cyan-950 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-slate-200">Terminal Location</div>
                  <div className="text-[11px] font-semibold text-slate-300">
                    {settings.checkpointName || "Terminal B - Primary Inspection"}
                  </div>
                </div>
                <span className="text-[10px] font-mono font-bold text-emerald-400">ONLINE</span>
              </div>

              <div className="p-2.5 rounded-lg bg-[#06101B]/80 border border-cyan-950 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-slate-200">Audit Ledger Verification</div>
                  <div className="text-[11px] font-mono text-slate-400">SHA-256 Chained</div>
                </div>
                <Link to="/audit" className="text-[11px] font-mono text-[#20E3C2] hover:underline font-bold">
                  Inspect
                </Link>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-cyan-950/70 flex gap-2">
            <Link
              to="/screening"
              className="flex-1 py-2 rounded-lg bg-[#20E3C2]/15 hover:bg-[#20E3C2]/25 border border-[#20E3C2]/50 text-[#20E3C2] font-bold text-xs uppercase tracking-wider text-center transition-colors"
            >
              Screen Document
            </Link>
            <Link
              to="/database"
              className="flex-1 py-2 rounded-lg bg-[#06101B] hover:bg-[#0A1A2B] border border-cyan-900 text-slate-200 font-bold text-xs uppercase tracking-wider text-center transition-colors"
            >
              Browse Database
            </Link>
          </div>
        </div>

        {/* SYSTEM STATUS (7 MODULES) */}
        <div className="lg:col-span-2">
          <SystemStatusPanel />
        </div>
      </div>

      {/* ============================================================ */}
      {/* 5. MOST RECENT SCREENING SPOTLIGHT & RECENT TABLE             */}
      {/* ============================================================ */}
      <div className="panel-3d p-6 border-cyan-900/60 bg-[#0A1624]/90 backdrop-blur-md">
        <div className="flex items-center justify-between mb-4 border-b border-cyan-950/70 pb-3">
          <div className="flex items-center gap-2.5">
            <Layers className="w-4 h-4 text-[#20E3C2]" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Recent Document Screenings
            </h2>
          </div>

          {records.length > 0 && (
            <Link
              to="/database"
              className="flex items-center gap-1.5 text-xs font-bold text-[#20E3C2] hover:text-white transition-colors font-mono"
            >
              <span>View All ({records.length}) Records</span>
              <ArrowRight size={14} />
            </Link>
          )}
        </div>

        {recentRecords.length === 0 ? (
          <EmptyState
            title="No screening records available"
            description="Perform a real document screening to populate the operations ledger and live telemetry."
            actionLabel="Start Screening Now"
            onAction="/screening"
          />
        ) : (
          <div className="table-container overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-cyan-950 text-[11px] font-mono text-[#5A7A9C] uppercase">
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Screening ID</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Document Type</th>
                  <th className="py-2.5 px-3">Subject Name</th>
                  <th className="py-2.5 px-3">Document No.</th>
                  <th className="py-2.5 px-3">Confidence</th>
                  <th className="py-2.5 px-3">Forensic Risk</th>
                  <th className="py-2.5 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cyan-950/40">
                {recentRecords.map((rec) => (
                  <tr key={rec.screening_id} className="hover:bg-[#06101B]/60 transition-colors">
                    <td className="py-2.5 px-3">
                      <StatusBadge status={rec.status} size="sm" />
                    </td>
                    <td className="py-2.5 px-3 font-mono font-bold text-[#20E3C2]">
                      {truncateMiddle(rec.screening_id, 14)}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[#7E9AB8]">
                      {formatDate(rec.timestamp)}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded bg-[#06101B] border border-cyan-950 text-[10px] font-mono font-bold text-slate-200">
                        {rec.document_type || "PASSPORT"}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-bold text-white">
                      {rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("name"))?.extracted_value ||
                        rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("surname"))?.extracted_value ||
                        "—"}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-slate-200 font-bold">
                      {rec.document_number ||
                        rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("doc"))?.extracted_value ||
                        "—"}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="font-mono font-bold text-emerald-400">
                        {rec.confidence_score ? `${Math.round(rec.confidence_score * 100)}%` : "—"}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span
                        className={`font-mono font-bold ${
                          (rec.tampering_analysis?.tampering_score || 0) > 0.4
                            ? "text-rose-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {rec.tampering_analysis
                          ? `${Math.round((rec.tampering_analysis.tampering_score || 0) * 100)}%`
                          : "—"}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <Link
                        to={`/evidence?id=${rec.screening_id}`}
                        className="inline-flex items-center gap-1 font-mono font-bold text-[#20E3C2] hover:text-white transition-colors"
                      >
                        <span>Dossier</span>
                        <ExternalLink size={12} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
