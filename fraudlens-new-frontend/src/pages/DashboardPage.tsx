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
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { MetricTile } from "@/components/MetricTile";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { ActivityBarChart } from "@/components/ActivityBarChart";
import { formatDate, truncateMiddle } from "@/utils/formatters";

export function DashboardPage() {
  const { stats, records, refreshData, isLiveConnected, settings } = useApp();

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const recentRecords = records.slice(0, 8);
  const watchlistHits = records.filter(
    (r) =>
      r.status === "WATCHLIST_HIT" ||
      r.status === "TAMPERED" ||
      r.status === "FRAUD_DETECTED"
  );

  return (
    <div className="space-y-6">
      {/* Top Welcome & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slateText-50 tracking-tight">Border Operations Dashboard</h1>
            <span className="rounded bg-canvas-850 px-2 py-0.5 text-xs font-mono font-bold text-brand-teal border border-canvas-600">
              {settings.checkpointId}
            </span>
          </div>
          <p className="text-sm font-semibold text-slateText-300">
            Real-time screening intelligence, forensic metrics, and checkpoint throughput
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => refreshData()}
            className="btn-secondary flex items-center gap-2 text-xs font-bold uppercase tracking-wider"
          >
            <RefreshCw size={14} />
            <span>Sync Stats</span>
          </button>

          <Link
            to="/screening"
            className="btn-primary flex items-center gap-2 text-xs font-bold uppercase tracking-wider"
          >
            <PlusCircle size={14} />
            <span>New Screening</span>
          </Link>
        </div>
      </div>

      {/* Security Alert Banner (if any flagged documents) */}
      {watchlistHits.length > 0 && (
        <div className="rounded-xl border border-accent-rose/50 bg-accent-rose/10 p-4 shadow-glow-rose flex items-start gap-3">
          <ShieldAlert className="h-6 w-6 text-accent-rose shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-bold text-accent-rose uppercase tracking-wider">
              High-Risk Forensic Alert ({watchlistHits.length} Flagged Incident{watchlistHits.length > 1 ? "s" : ""})
            </h3>
            <p className="text-xs font-medium text-slateText-200 mt-1">
              One or more documents screened at this terminal exhibited severe tampering anomalies or watchlist matches.
              Inspect the respective forensic evidence dossiers immediately.
            </p>
          </div>
          <Link
            to={`/evidence?id=${watchlistHits[0].screening_id}`}
            className="btn-danger text-xs uppercase tracking-wider shrink-0"
          >
            Inspect Alert
          </Link>
        </div>
      )}

      {/* Primary Operational Metrics (100% Calculated & Traceable) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricTile
          label="Total Screened"
          value={stats.totalScreened}
          icon={FileCheck2}
          variant="neutral"
          helperText="All documents processed"
        />
        <MetricTile
          label="Valid / Passed"
          value={stats.validCount}
          icon={CheckCircle2}
          variant="emerald"
          helperText="High-assurance clearance"
        />
        <MetricTile
          label="Review Required"
          value={stats.reviewRequiredCount}
          icon={AlertTriangle}
          variant="amber"
          helperText="Secondary officer review"
        />
        <MetricTile
          label="Expired / Fraud"
          value={stats.expiredCount}
          icon={XCircle}
          variant="rose"
          helperText="Tampered, expired or flagged"
        />
        <MetricTile
          label="Avg Latency"
          value={stats.avgLatencyMs > 0 ? stats.avgLatencyMs : "—"}
          suffix={stats.avgLatencyMs > 0 ? "ms" : ""}
          icon={Clock}
          variant="sky"
          helperText="End-to-end pipeline time"
        />
        <MetricTile
          label="Sync Health"
          value={isLiveConnected ? "100%" : "Local"}
          icon={RefreshCw}
          variant={isLiveConnected ? "teal" : "amber"}
          helperText={isLiveConnected ? "Connected to HQ" : "Offline buffer mode"}
        />
      </div>

      {/* Middle Section: Chart & Quick Console Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ActivityBarChart records={records} />
        </div>

        <div className="panel-3d p-5 flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slateText-200 mb-3 flex items-center justify-between">
              <span>Checkpoint Operations</span>
              <span className="text-[11px] font-mono text-brand-teal">ACTIVE</span>
            </h2>
            <div className="space-y-3">
              <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-slateText-100">Officer Assigned</div>
                  <div className="text-[11px] font-mono text-slateText-300">{settings.officerId}</div>
                </div>
                <Link to="/settings" className="text-xs text-brand-teal hover:underline font-bold">
                  Edit
                </Link>
              </div>

              <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-slateText-100">Terminal Location</div>
                  <div className="text-[11px] font-semibold text-slateText-300">{settings.checkpointName}</div>
                </div>
                <span className="text-xs font-bold text-accent-emerald">ONLINE</span>
              </div>

              <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex items-center justify-between">
                <div>
                  <div className="text-xs font-bold text-slateText-100">Audit Ledger Verification</div>
                  <div className="text-[11px] font-mono text-slateText-300">SHA-256 Chained</div>
                </div>
                <Link to="/audit" className="text-xs text-brand-teal hover:underline font-bold">
                  Inspect
                </Link>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-canvas-600 flex flex-col gap-2">
            <Link to="/screening" className="btn-primary w-full text-center text-xs uppercase tracking-wider">
              Execute Document Screening
            </Link>
            <Link to="/database" className="btn-secondary w-full text-center text-xs uppercase tracking-wider">
              Open Searchable Database
            </Link>
          </div>
        </div>
      </div>

      {/* Bottom Section: Recent Screenings Table */}
      <div className="panel-3d p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-slateText-50">Recent Document Screenings</h2>
            <p className="text-xs font-medium text-slateText-300">
              Audit-verified screening events recorded at this terminal
            </p>
          </div>

          {records.length > 0 && (
            <Link
              to="/database"
              className="flex items-center gap-1.5 text-xs font-bold text-brand-teal hover:text-brand-cyan transition-colors"
            >
              <span>View All ({records.length}) Records</span>
              <ArrowRight size={14} />
            </Link>
          )}
        </div>

        {recentRecords.length === 0 ? (
          <EmptyState
            title="No screening records available"
            description="Perform a document screening to populate the real-time operational ledger."
            actionLabel="Start Screening Now"
            onAction="/screening"
          />
        ) : (
          <div className="table-container">
            <table className="table-custom">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Screening ID</th>
                  <th>Timestamp</th>
                  <th>Document Type</th>
                  <th>Subject Name</th>
                  <th>Document No.</th>
                  <th>Confidence</th>
                  <th>Forensic Risk</th>
                  <th className="text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {recentRecords.map((rec) => (
                  <tr key={rec.screening_id}>
                    <td>
                      <StatusBadge status={rec.status} size="sm" />
                    </td>
                    <td className="font-mono text-xs text-brand-teal font-bold">
                      {truncateMiddle(rec.screening_id, 14)}
                    </td>
                    <td className="text-xs text-slateText-300 font-medium">
                      {formatDate(rec.timestamp)}
                    </td>
                    <td>
                      <span className="badge-neutral text-[11px] font-bold">
                        {rec.document_type || "PASSPORT"}
                      </span>
                    </td>
                    <td className="font-bold text-slateText-50 text-xs">
                      {rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("name"))?.extracted_value ||
                        rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("surname"))?.extracted_value ||
                        rec.document_number ||
                        "—"}
                    </td>
                    <td className="font-mono text-xs text-slateText-200 font-bold">
                      {rec.document_number ||
                        rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("doc"))?.extracted_value ||
                        "—"}
                    </td>
                    <td>
                      <span className="font-mono text-xs font-bold text-accent-emerald">
                        {rec.confidence_score ? `${Math.round(rec.confidence_score * 100)}%` : "—"}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`font-mono text-xs font-bold ${
                          (rec.tampering_analysis?.tampering_score || 0) > 0.4
                            ? "text-accent-rose"
                            : "text-accent-emerald"
                        }`}
                      >
                        {rec.tampering_analysis
                          ? `${Math.round((rec.tampering_analysis.tampering_score || 0) * 100)}%`
                          : "—"}
                      </span>
                    </td>
                    <td className="text-right">
                      <Link
                        to={`/evidence?id=${rec.screening_id}`}
                        className="inline-flex items-center gap-1 text-xs font-bold text-brand-teal hover:text-brand-cyan hover:underline"
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
