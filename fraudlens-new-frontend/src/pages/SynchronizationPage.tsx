import React, { useState } from "react";
import {
  Globe,
  Radio,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Info,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { SyncInfographic3D } from "@/components/SyncInfographic3D";
import { SyncSummaryCards } from "@/components/SyncSummaryCards";
import { SyncTerminalPanels } from "@/components/SyncTerminalPanels";
import { SyncActionBanner } from "@/components/SyncActionBanner";

export function SynchronizationPage() {
  const {
    records,
    triggerSync,
    isSyncing,
    lastSyncedAt,
    isLiveConnected,
    settings,
    operatingMode,
    setOperatingMode,
    pendingSyncCount,
    syncedRecordsCount,
  } = useApp();

  const [syncFeedback, setSyncFeedback] = useState<{
    type: "success" | "error" | "info";
    message: string;
  } | null>(null);

  const [showSwitchConfirm, setShowSwitchConfirm] = useState(false);
  const [targetMode, setTargetMode] = useState<"ONLINE" | "OFFLINE">("ONLINE");

  const handleModeToggle = (newMode: "ONLINE" | "OFFLINE") => {
    if (newMode === operatingMode) return;

    if (isSyncing) {
      setTargetMode(newMode);
      setShowSwitchConfirm(true);
      return;
    }

    setOperatingMode(newMode);
    if (newMode === "ONLINE") {
      setSyncFeedback({
        type: "info",
        message: "Switched to Online Mode. Central HQ connection active.",
      });
    } else {
      setSyncFeedback({
        type: "info",
        message: "Switched to Offline Mode. Local database active; records safely queued.",
      });
    }
  };

  const confirmModeSwitch = () => {
    setOperatingMode(targetMode);
    setShowSwitchConfirm(false);
  };

  const handleSync = async () => {
    try {
      setSyncFeedback(null);
      const report = await triggerSync();
      if (operatingMode === "OFFLINE") {
        setSyncFeedback({
          type: "info",
          message: "Offline mode active. Records are safely stored locally in SQLite WAL.",
        });
      } else {
        setSyncFeedback({
          type: "success",
          message: `Differential synchronization completed successfully. ${records.length} records in sync with Central HQ.`,
        });
      }
    } catch (err: any) {
      setSyncFeedback({
        type: "error",
        message: err.message || "Differential synchronization failed. Local buffer preserved.",
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Page Header with Working Mode Switch */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-mono font-black text-slateText-50 tracking-tight">
              Synchronization
            </h1>
            <span
              className={`rounded px-2 py-0.5 text-xs font-mono font-bold border transition-colors ${
                operatingMode === "ONLINE"
                  ? "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40"
                  : "bg-accent-amber/20 text-accent-amber border-accent-amber/40"
              }`}
            >
              {operatingMode === "ONLINE" ? "ONLINE MODE" : "OFFLINE MODE"}
            </span>
          </div>
          <p className="text-xs font-mono text-slateText-300 mt-0.5">
            Data sync between terminal and central border database
          </p>
        </div>

        {/* Segmented Mode Switch */}
        <div className="flex flex-col items-end gap-1">
          <div className="flex items-center p-1 rounded-full bg-canvas-900 border border-canvas-600/90 shadow-[0_0_15px_rgba(0,0,0,0.5)]">
            <button
              onClick={() => handleModeToggle("ONLINE")}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-mono font-black uppercase tracking-wider transition-all duration-300 cursor-pointer ${
                operatingMode === "ONLINE"
                  ? "bg-gradient-to-r from-accent-emerald to-accent-teal text-canvas-950 shadow-[0_0_15px_rgba(16,185,129,0.5)] font-black"
                  : "text-slateText-400 hover:text-slateText-200"
              }`}
            >
              <Globe size={13} />
              <span>ONLINE</span>
            </button>

            <button
              onClick={() => handleModeToggle("OFFLINE")}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-mono font-black uppercase tracking-wider transition-all duration-300 cursor-pointer ${
                operatingMode === "OFFLINE"
                  ? "bg-gradient-to-r from-accent-amber to-amber-600 text-canvas-950 shadow-[0_0_15px_rgba(245,158,11,0.5)] font-black"
                  : "text-slateText-400 hover:text-slateText-200"
              }`}
            >
              <Radio size={13} />
              <span>OFFLINE</span>
            </button>
          </div>
          <span className="text-[10px] font-mono text-slateText-400 pr-2">
            Select mode for operation
          </span>
        </div>
      </div>

      {/* Dynamic Feedback Banner */}
      {syncFeedback && (
        <div
          className={`rounded-xl border p-4 text-xs font-mono font-bold flex items-center justify-between gap-3 animate-in fade-in ${
            syncFeedback.type === "success"
              ? "border-accent-emerald/50 bg-accent-emerald/10 text-accent-emerald shadow-[0_0_15px_rgba(16,185,129,0.15)]"
              : syncFeedback.type === "error"
              ? "border-accent-rose/50 bg-accent-rose/10 text-accent-rose shadow-[0_0_15px_rgba(239,68,68,0.15)]"
              : "border-accent-sky/50 bg-accent-sky/10 text-accent-sky shadow-[0_0_15px_rgba(6,182,212,0.15)]"
          }`}
        >
          <div className="flex items-center gap-2">
            {syncFeedback.type === "success" ? (
              <CheckCircle2 size={16} />
            ) : syncFeedback.type === "error" ? (
              <AlertCircle size={16} />
            ) : (
              <Info size={16} />
            )}
            <span>{syncFeedback.message}</span>
          </div>
          <button
            onClick={() => setSyncFeedback(null)}
            className="text-[10px] font-mono uppercase underline hover:opacity-80 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* 2. Main 3D Synchronization Infographic */}
      <SyncInfographic3D
        operatingMode={operatingMode}
        isLiveConnected={isLiveConnected}
        isSyncing={isSyncing}
        pendingCount={pendingSyncCount}
        syncedCount={syncedRecordsCount}
        totalRecords={records.length}
      />

      {/* 3. Summary Metrics (4 Cards Row) */}
      <SyncSummaryCards
        operatingMode={operatingMode}
        isLiveConnected={isLiveConnected}
        isSyncing={isSyncing}
        totalRecords={records.length}
        syncedCount={syncedRecordsCount}
        pendingCount={pendingSyncCount}
        lastSyncedAt={lastSyncedAt}
      />

      {/* 4. Detailed Status Panels (Local Terminal & Central HQ) */}
      <SyncTerminalPanels
        settings={settings}
        operatingMode={operatingMode}
        isLiveConnected={isLiveConnected}
        totalRecords={records.length}
        pendingCount={pendingSyncCount}
        lastSyncedAt={lastSyncedAt}
      />

      {/* 5. Bottom Synchronization Action Banner */}
      <SyncActionBanner
        operatingMode={operatingMode}
        isLiveConnected={isLiveConnected}
        isSyncing={isSyncing}
        pendingCount={pendingSyncCount}
        totalRecords={records.length}
        lastSyncedAt={lastSyncedAt}
        onTriggerSync={handleSync}
      />

      {/* Mode Switch Confirmation Modal (During active sync) */}
      {showSwitchConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-accent-amber/50 bg-canvas-900 p-6 shadow-2xl space-y-4 font-mono">
            <div className="flex items-center gap-3 text-accent-amber">
              <AlertTriangle size={24} />
              <h3 className="text-base font-bold text-slateText-50">
                Confirm Mode Switch
              </h3>
            </div>

            <p className="text-xs text-slateText-300 leading-relaxed font-sans">
              Active synchronization will pause. Local processing will continue safely in SQLite storage.
            </p>

            <div className="flex justify-end gap-3 pt-2 text-xs">
              <button
                onClick={() => setShowSwitchConfirm(false)}
                className="px-4 py-2 rounded-xl bg-canvas-800 hover:bg-canvas-700 text-slateText-300 border border-canvas-700 font-bold cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={confirmModeSwitch}
                className="px-4 py-2 rounded-xl bg-accent-amber hover:bg-amber-500 text-canvas-950 font-black cursor-pointer shadow-lg"
              >
                Continue Offline
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
