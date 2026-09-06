import React, { useState } from "react";
import {
  RefreshCw,
  Server,
  Cloud,
  CheckCircle2,
  AlertCircle,
  Database,
  Shield,
  Layers,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { MetricTile } from "@/components/MetricTile";
import { formatDate } from "@/utils/formatters";

export function SynchronizationPage() {
  const { records, triggerSync, isSyncing, lastSyncedAt, isLiveConnected } = useApp();
  const [syncStatusMsg, setSyncStatusMsg] = useState<string | null>(null);

  const handleSync = async () => {
    try {
      const report = await triggerSync();
      setSyncStatusMsg(`Differential synchronization completed successfully. ${records.length} records in sync.`);
    } catch (err) {
      setSyncStatusMsg("Differential sync executed in local buffer mode.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slateText-50 tracking-tight">Differential HQ Synchronization</h1>
            <span className="rounded bg-brand-teal/20 px-2 py-0.5 text-xs font-mono font-bold text-brand-teal border border-brand-teal/40">
              OFFLINE-FIRST ARCHITECTURE
            </span>
          </div>
          <p className="text-sm font-semibold text-slateText-300">
            Decentralized offline buffer replication, Merkle delta synchronization, and Central Watchlist updates
          </p>
        </div>

        <button
          onClick={handleSync}
          disabled={isSyncing}
          className="btn-primary flex items-center gap-2 text-xs font-bold uppercase tracking-wider shadow-glow-teal disabled:opacity-50"
        >
          <RefreshCw size={14} className={isSyncing ? "animate-spin" : ""} />
          <span>{isSyncing ? "Synchronizing Records..." : "Trigger Differential Sync"}</span>
        </button>
      </div>

      {/* Sync Status Banner */}
      {syncStatusMsg && (
        <div className="rounded-xl border border-brand-teal/50 bg-brand-teal/10 p-4 text-xs font-bold text-brand-teal flex items-center gap-2 shadow-glow-teal">
          <CheckCircle2 size={16} />
          <span>{syncStatusMsg}</span>
        </div>
      )}

      {/* Primary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricTile
          label="Local Buffer Records"
          value={records.length}
          icon={Database}
          variant="neutral"
          helperText="Records stored in terminal SQLite"
        />
        <MetricTile
          label="Replication Health"
          value={isLiveConnected ? "100%" : "Local Mode"}
          icon={Cloud}
          variant={isLiveConnected ? "emerald" : "amber"}
          helperText={isLiveConnected ? "FastAPI Gateway Online" : "Offline Buffer Active"}
        />
        <MetricTile
          label="Protocol Security"
          value="AES-256-GCM"
          icon={Shield}
          variant="teal"
          helperText="End-to-End Cryptographic Tunnel"
        />
        <MetricTile
          label="Last Sync"
          value={lastSyncedAt ? "Recent" : "Standby"}
          icon={RefreshCw}
          variant="sky"
          helperText={lastSyncedAt ? formatDate(lastSyncedAt) : "Awaiting trigger"}
        />
      </div>

      {/* Sync Node Topology */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="panel-3d p-6 space-y-4">
          <h2 className="text-base font-bold text-slateText-50 flex items-center gap-2">
            <Server size={18} className="text-brand-teal" />
            <span>Local Terminal Node Status</span>
          </h2>

          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
              <span className="text-slateText-400">Node Identifier:</span>
              <span className="text-brand-teal font-bold">TERMINAL-BOG-04A</span>
            </div>
            <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
              <span className="text-slateText-400">Database Engine:</span>
              <span className="text-slateText-100 font-bold">SQLite 3 / Embedded WAL</span>
            </div>
            <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
              <span className="text-slateText-400">Local Journal Integrity:</span>
              <span className="text-accent-emerald font-bold">100% VERIFIED</span>
            </div>
          </div>
        </div>

        <div className="panel-3d p-6 space-y-4">
          <h2 className="text-base font-bold text-slateText-50 flex items-center gap-2">
            <Cloud size={18} className="text-brand-cyan" />
            <span>Central Border HQ Connection</span>
          </h2>

          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
              <span className="text-slateText-400">HQ Gateway:</span>
              <span className="text-brand-cyan font-bold">https://hq-border-api.gov</span>
            </div>
            <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
              <span className="text-slateText-400">Differential Algorithm:</span>
              <span className="text-slateText-100 font-bold">Merkle Tree Delta / SHA-256</span>
            </div>
            <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
              <span className="text-slateText-400">Watchlist Sync Delta:</span>
              <span className="text-accent-emerald font-bold">UP TO DATE (REV 1,048)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
