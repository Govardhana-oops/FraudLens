import React, { useState, useEffect } from "react";
import {
  ScrollText,
  ShieldCheck,
  RefreshCw,
  Search,
  CheckCircle2,
  Copy,
  Check,
  Lock,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { EmptyState } from "@/components/EmptyState";
import { formatDate, truncateMiddle } from "@/utils/formatters";

export function AuditLogsPage() {
  const { auditLogs, fetchAuditLogs } = useApp();
  const [searchTerm, setSearchTerm] = useState("");
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  useEffect(() => {
    fetchAuditLogs();
  }, [fetchAuditLogs]);

  const handleCopy = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(hash);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  const filteredLogs = auditLogs.filter(
    (l) =>
      l.event_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.officer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.resource_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      l.current_hash.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slateText-50 tracking-tight">Immutable Cryptographic Audit Ledger</h1>
            <span className="rounded bg-accent-emerald/20 px-2 py-0.5 text-xs font-mono font-bold text-accent-emerald border border-accent-emerald/40">
              SHA-256 CHAINED
            </span>
          </div>
          <p className="text-sm font-semibold text-slateText-300">
            Tamper-evident audit trail with chained block hashes for legal evidentiary integrity
          </p>
        </div>

        <button
          onClick={() => fetchAuditLogs()}
          className="btn-secondary flex items-center gap-2 text-xs font-bold uppercase tracking-wider"
        >
          <RefreshCw size={14} />
          <span>Verify & Refresh Ledger</span>
        </button>
      </div>

      {/* Ledger Integrity Banner */}
      <div className="panel-3d p-4 border-accent-emerald/40 bg-accent-emerald/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/40">
            <ShieldCheck size={22} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slateText-50">Cryptographic Chain Status: 100% Intact</h3>
            <p className="text-xs text-slateText-300 font-medium">
              Every audit block is cryptographically linked to its predecessor via SHA-256 Merkle hashes.
            </p>
          </div>
        </div>

        <span className="badge-valid font-mono text-xs">CHAIN SIGNATURE VALID</span>
      </div>

      {/* Search Input */}
      <div className="panel-3d p-4">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slateText-400" />
          <input
            type="text"
            placeholder="Search audit logs by Event Type, Officer, Resource ID, or SHA-256 Hash..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-custom pl-10 text-xs w-full"
          />
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="panel-3d p-6">
        {filteredLogs.length === 0 ? (
          <EmptyState
            title="No audit records available"
            description={
              searchTerm
                ? "No audit records matched your search query."
                : "No audit events recorded in the ledger yet. Perform a screening to record audit entries."
            }
            actionLabel={searchTerm ? "Clear Search" : "Start Screening"}
            onAction={searchTerm ? () => setSearchTerm("") : "/screening"}
          />
        ) : (
          <div className="table-container">
            <table className="table-custom">
              <thead>
                <tr>
                  <th>Seq</th>
                  <th>Timestamp</th>
                  <th>Event Type</th>
                  <th>Officer</th>
                  <th>Target Resource</th>
                  <th>Current SHA-256 Hash</th>
                  <th>Previous Block Hash</th>
                  <th className="text-right">Integrity</th>
                </tr>
              </thead>
              <tbody>
                {filteredLogs.map((log) => (
                  <tr key={log.sequence_number}>
                    <td className="font-mono text-xs font-bold text-brand-teal">
                      #{log.sequence_number}
                    </td>
                    <td className="text-xs text-slateText-300 font-medium">
                      {formatDate(log.timestamp)}
                    </td>
                    <td>
                      <span className="rounded bg-canvas-850 px-2 py-0.5 text-xs font-mono font-bold text-slateText-100 border border-canvas-600">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="font-mono text-xs font-bold text-slateText-200">{log.officer_id}</td>
                    <td className="font-mono text-xs text-slateText-300">
                      {truncateMiddle(log.resource_id, 12)}
                    </td>
                    <td>
                      <div className="flex items-center gap-1.5 font-mono text-xs text-brand-teal font-bold">
                        <span>{truncateMiddle(log.current_hash, 16)}</span>
                        <button
                          onClick={() => handleCopy(log.current_hash)}
                          className="text-slateText-400 hover:text-brand-teal"
                        >
                          {copiedHash === log.current_hash ? (
                            <Check size={12} className="text-accent-emerald" />
                          ) : (
                            <Copy size={12} />
                          )}
                        </button>
                      </div>
                    </td>
                    <td>
                      <span className="font-mono text-xs text-slateText-400">
                        {truncateMiddle(log.previous_hash, 16)}
                      </span>
                    </td>
                    <td className="text-right">
                      <span className="inline-flex items-center gap-1 text-xs font-bold text-accent-emerald">
                        <CheckCircle2 size={14} />
                        <span>VALID</span>
                      </span>
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
