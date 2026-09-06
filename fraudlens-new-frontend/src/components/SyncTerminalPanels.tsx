import React from "react";
import { Laptop, Cloud, Server, Shield, Database } from "lucide-react";
import { formatDate } from "@/utils/formatters";
import type { ConsoleSettings } from "@/types";

interface SyncTerminalPanelsProps {
  settings: ConsoleSettings;
  operatingMode: "ONLINE" | "OFFLINE";
  isLiveConnected: boolean;
  totalRecords: number;
  pendingCount: number;
  lastSyncedAt: string | null;
}

export function SyncTerminalPanels({
  settings,
  operatingMode,
  isLiveConnected,
  totalRecords,
  pendingCount,
  lastSyncedAt,
}: SyncTerminalPanelsProps) {
  const isOnline = operatingMode === "ONLINE";
  const isConnected = isOnline && isLiveConnected;

  const checkpointPrefix = settings.checkpointName
    ? settings.checkpointName.split("-")[0].trim().toUpperCase().replace(/[^A-Z0-9]/g, "-")
    : settings.checkpointId
    ? settings.checkpointId.toUpperCase()
    : "TERMINAL-B";
  const officerSuffix = settings.officerId ? settings.officerId.toUpperCase() : "CP-0082";
  const terminalId = `${checkpointPrefix}-${officerSuffix}`;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Panel: Local Terminal */}
      <div className="panel-3d p-6 rounded-2xl border border-canvas-600/80 bg-canvas-850 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-canvas-600/80">
          <h2 className="text-sm font-mono font-bold text-slateText-100 flex items-center gap-2">
            <Laptop size={18} className="text-accent-sky" />
            <span>Local Terminal</span>
          </h2>
          <span className="flex items-center gap-1.5 text-[11px] font-mono text-accent-emerald font-bold px-2 py-0.5 rounded bg-accent-emerald/10 border border-accent-emerald/30">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald animate-ping" />
            <span>System Active</span>
          </span>
        </div>

        <div className="space-y-2.5 font-mono text-xs">
          <div className="p-3 rounded-xl bg-canvas-900 border border-canvas-700/80 flex items-center justify-between">
            <span className="text-slateText-400">Terminal ID:</span>
            <span className="text-accent-sky font-bold tracking-wider">{terminalId}</span>
          </div>

          <div className="p-3 rounded-xl bg-canvas-900 border border-canvas-700/80 flex items-center justify-between">
            <span className="text-slateText-400">Local Records:</span>
            <span className="text-slateText-100 font-bold">{totalRecords}</span>
          </div>

          <div className="p-3 rounded-xl bg-canvas-900 border border-canvas-700/80 flex items-center justify-between">
            <span className="text-slateText-400">Database Status:</span>
            <span className="flex items-center gap-1.5 text-accent-emerald font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-emerald" />
              <span>Active (SQLite WAL)</span>
            </span>
          </div>

          <div className="p-3 rounded-xl bg-canvas-900 border border-canvas-700/80 flex items-center justify-between">
            <span className="text-slateText-400">Last Sync:</span>
            <span className="text-slateText-300">
              {lastSyncedAt ? formatDate(lastSyncedAt) : "—"}
            </span>
          </div>
        </div>
      </div>

      {/* Right Panel: Central HQ Connection */}
      <div className="panel-3d p-6 rounded-2xl border border-canvas-600/80 bg-canvas-850 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-canvas-600/80">
          <h2 className="text-sm font-mono font-bold text-slateText-100 flex items-center gap-2">
            <Cloud size={18} className="text-accent-teal" />
            <span>Central HQ Connection</span>
          </h2>
          <span
            className={`flex items-center gap-1.5 text-[11px] font-mono font-bold px-2 py-0.5 rounded border ${
              isConnected
                ? "bg-accent-emerald/10 text-accent-emerald border-accent-emerald/30"
                : isOnline
                ? "bg-accent-amber/10 text-accent-amber border-accent-amber/30"
                : "bg-canvas-900 text-slateText-400 border-canvas-700"
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isConnected
                  ? "bg-accent-emerald animate-ping"
                  : isOnline
                  ? "bg-accent-amber"
                  : "bg-slateText-500"
              }`}
            />
            <span>{isConnected ? "Connected" : isOnline ? "Unavailable" : "Offline"}</span>
          </span>
        </div>

        <div className="space-y-2.5 font-mono text-xs">
          <div className="p-3 rounded-xl bg-canvas-900 border border-canvas-700/80 flex items-center justify-between">
            <span className="text-slateText-400">Server Endpoint:</span>
            <span className="text-accent-teal font-bold truncate max-w-[220px]">
              {settings.apiBaseUrl || "https://fraudlens-api-xpym.onrender.com"}
            </span>
          </div>

          <div className="p-3 rounded-xl bg-canvas-900 border border-canvas-700/80 flex items-center justify-between">
            <span className="text-slateText-400">Connection Status:</span>
            <span
              className={`flex items-center gap-1.5 font-bold ${
                isConnected
                  ? "text-accent-emerald"
                  : isOnline
                  ? "text-accent-amber"
                  : "text-slateText-400"
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  isConnected ? "bg-accent-emerald" : isOnline ? "bg-accent-amber" : "bg-slateText-500"
                }`}
              />
              <span>
                {isConnected
                  ? "Connected"
                  : isOnline
                  ? "Unavailable (Gateway Unreachable)"
                  : "Disconnected (Offline Mode)"}
              </span>
            </span>
          </div>

          <div className="p-3 rounded-xl bg-canvas-900 border border-canvas-700/80 flex items-center justify-between">
            <span className="text-slateText-400">Security:</span>
            <span className="text-slateText-100 font-bold">TLS 1.3 / HTTPS Encrypted</span>
          </div>

          <div className="p-3 rounded-xl bg-canvas-900 border border-canvas-700/80 flex items-center justify-between">
            <span className="text-slateText-400">Sync Mode:</span>
            <span className="text-slateText-200">
              {isConnected
                ? "Real-time (Online)"
                : isOnline
                ? `Online Standby (${pendingCount} queued)`
                : `Offline Queue (${pendingCount} pending)`}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
