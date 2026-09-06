import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Database,
  Search,
  Filter,
  Download,
  Trash2,
  ExternalLink,
  RefreshCw,
  FileCheck2,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { formatDate, truncateMiddle } from "@/utils/formatters";
import type { ScreeningStatus } from "@/types";

export function DatabasePage() {
  const { records, deleteRecord, refreshData } = useApp();

  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");

  const filteredRecords = records.filter((rec) => {
    const matchesSearch =
      rec.screening_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (rec.document_number || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (rec.document_type || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      rec.extracted_fields?.some(
        (f) =>
          f.extracted_value.toLowerCase().includes(searchTerm.toLowerCase()) ||
          f.field_name.toLowerCase().includes(searchTerm.toLowerCase())
      );

    const matchesStatus = statusFilter === "ALL" || rec.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const handleExportCSV = () => {
    if (records.length === 0) return;

    const headers = ["ScreeningID", "Timestamp", "DocumentType", "DocumentNumber", "Status", "Confidence", "RecordHash"];
    const rows = records.map((r) => [
      r.screening_id,
      r.timestamp,
      r.document_type || "PASSPORT",
      r.document_number || "",
      r.status,
      r.confidence_score || "",
      r.record_hash,
    ]);

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Screening_Database_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const statusOptions: { value: string; label: string }[] = [
    { value: "ALL", label: "All Statuses" },
    { value: "VALID", label: "Valid" },
    { value: "REVIEW_REQUIRED", label: "Review Required" },
    { value: "EXPIRED", label: "Expired" },
    { value: "TAMPERED", label: "Tampered" },
    { value: "WATCHLIST_HIT", label: "Watchlist Hit" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slateText-50 tracking-tight">Screening Records Database</h1>
            <span className="rounded bg-canvas-850 px-2 py-0.5 text-xs font-mono font-bold text-brand-teal border border-canvas-600">
              {records.length} TOTAL RECORDS
            </span>
          </div>
          <p className="text-sm font-semibold text-slateText-300">
            Search, filter, inspect, and export verified records across all border checkpoints
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => refreshData()}
            className="btn-secondary flex items-center gap-2 text-xs font-bold uppercase tracking-wider"
          >
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleExportCSV}
            disabled={records.length === 0}
            className="btn-primary flex items-center gap-2 text-xs font-bold uppercase tracking-wider disabled:opacity-50"
          >
            <Download size={14} />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="panel-3d p-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slateText-400" />
          <input
            type="text"
            placeholder="Search by Document No, Name, ID, or Hash..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-custom pl-10 text-xs w-full"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter size={14} className="text-slateText-400 shrink-0" />
          <div className="flex flex-wrap gap-1.5">
            {statusOptions.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setStatusFilter(opt.value)}
                className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                  statusFilter === opt.value
                    ? "bg-brand-teal text-canvas-950 font-black shadow-glow-teal"
                    : "bg-canvas-850 text-slateText-300 border border-canvas-600 hover:border-canvas-500 hover:text-slateText-100"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Database Table */}
      <div className="panel-3d p-6">
        {filteredRecords.length === 0 ? (
          <EmptyState
            title="No screening records available"
            description={
              searchTerm || statusFilter !== "ALL"
                ? "No records matched your search query or filter criteria."
                : "The screening database is currently empty. Run an inspection to populate records."
            }
            actionLabel={searchTerm || statusFilter !== "ALL" ? "Clear Filters" : "Run Document Screening"}
            onAction={
              searchTerm || statusFilter !== "ALL"
                ? () => {
                    setSearchTerm("");
                    setStatusFilter("ALL");
                  }
                : "/screening"
            }
          />
        ) : (
          <div className="table-container">
            <table className="table-custom">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Screening ID</th>
                  <th>Timestamp</th>
                  <th>Doc Type</th>
                  <th>Subject Name</th>
                  <th>Document Number</th>
                  <th>Confidence</th>
                  <th>Risk Score</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((rec) => {
                  const subjectName =
                    rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("name"))?.extracted_value ||
                    rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("surname"))?.extracted_value ||
                    rec.document_number ||
                    "—";

                  const docNo =
                    rec.document_number ||
                    rec.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("doc"))?.extracted_value ||
                    "—";

                  return (
                    <tr key={rec.screening_id}>
                      <td>
                        <StatusBadge status={rec.status} size="sm" />
                      </td>
                      <td className="font-mono text-xs font-bold text-brand-teal">
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
                      <td className="font-bold text-slateText-50 text-xs">{subjectName}</td>
                      <td className="font-mono text-xs text-slateText-200 font-bold">{docNo}</td>
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
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/evidence?id=${rec.screening_id}`}
                            className="p-1.5 rounded-lg bg-canvas-850 border border-canvas-600 hover:border-brand-teal text-slateText-300 hover:text-brand-teal transition-colors"
                            title="Open Dossier"
                          >
                            <ExternalLink size={14} />
                          </Link>

                          <button
                            onClick={() => deleteRecord(rec.screening_id)}
                            className="p-1.5 rounded-lg bg-canvas-850 border border-canvas-600 hover:border-accent-rose text-slateText-300 hover:text-accent-rose transition-colors"
                            title="Delete Record"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
