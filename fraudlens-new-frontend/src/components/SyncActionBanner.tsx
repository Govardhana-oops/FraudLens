import React, { useState } from "react";
import {
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Calendar,
  HardDrive,
  Info,
} from "lucide-react";
import { formatDate } from "@/utils/formatters";

interface SyncActionBannerProps {
  operatingMode: "ONLINE" | "OFFLINE";
  isLiveConnected: boolean;
  isSyncing: boolean;
  pendingCount: number;
  totalRecords: number;
  lastSyncedAt: string | null;
  onTriggerSync: () => void;
}

export function SyncActionBanner({
  operatingMode,
  isLiveConnected,
  isSyncing,
  pendingCount,
  totalRecords,
  lastSyncedAt,
  onTriggerSync,
}: SyncActionBannerProps) {
  const [showOfflineModal, setShowOfflineModal] = useState(false);
  const isOnline = operatingMode === "ONLINE";
  const isConnected = isOnline && isLiveConnected;

  let bannerTitle = "Synchronization Healthy";
  let bannerDesc = "All records are synchronized and secure.";
  let borderClass = "border-accent-emerald/60 bg-accent-emerald/5 shadow-[0_0_30px_rgba(16,185,129,0.12)]";
  let iconClass = "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40";
  let Icon = ShieldCheck;

  if (isSyncing) {
    bannerTitle = "Replicating Records to Central HQ...";
    bannerDesc = "Differential cryptographic Merkle ledger synchronization in progress.";
    borderClass = "border-accent-sky/60 bg-accent-sky/5 shadow-[0_0_30px_rgba(6,182,212,0.12)]";
    iconClass = "bg-accent-sky/20 text-accent-sky border-accent-sky/40";
    Icon = RefreshCw;
  } else if (!isOnline) {
    bannerTitle = "Offline Mode Active";
    bannerDesc = `${pendingCount} record(s) queued safely in local database. Synchronization will execute when Online mode is selected.`;
    borderClass = "border-accent-amber/60 bg-accent-amber/5 shadow-[0_0_30px_rgba(245,158,11,0.12)]";
    iconClass = "bg-accent-amber/20 text-accent-amber border-accent-amber/40";
    Icon = HardDrive;
  } else if (!isLiveConnected) {
    bannerTitle = "Central Gateway Connection Unavailable";
    bannerDesc = `${pendingCount} record(s) buffered safely in local database. Central HQ is currently unreachable; records will sync once connection returns.`;
    borderClass = "border-accent-amber/60 bg-accent-amber/5 shadow-[0_0_30px_rgba(245,158,11,0.12)]";
    iconClass = "bg-accent-amber/20 text-accent-amber border-accent-amber/40";
    Icon = AlertTriangle;
  } else if (pendingCount > 0) {
    bannerTitle = "Synchronization Pending";
    bannerDesc = `${pendingCount} local record(s) awaiting differential synchronization to Central HQ.`;
    borderClass = "border-accent-amber/60 bg-accent-amber/5 shadow-[0_0_30px_rgba(245,158,11,0.12)]";
    iconClass = "bg-accent-amber/20 text-accent-amber border-accent-amber/40";
    Icon = AlertTriangle;
  }

  return (
    <>
      <div className={`panel-3d p-6 rounded-2xl border transition-all duration-300 ${borderClass}`}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Left: Status Icon & Title */}
          <div className="flex items-start gap-4">
            <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border ${iconClass}`}>
              <Icon size={26} className={isSyncing ? "animate-spin" : ""} />
            </div>

            <div>
              <h2 className="text-base font-mono font-black text-slateText-50 tracking-tight">
                {bannerTitle}
              </h2>
              <p className="text-xs font-mono text-slateText-300 mt-1 max-w-xl">
                {bannerDesc}
              </p>
            </div>
          </div>

          {/* Right: Last Updated & Action Button */}
          <div className="flex flex-wrap items-center gap-4 self-end lg:self-center">
            {/* Last Updated block */}
            <div className="flex items-center gap-2 text-right">
              <Calendar size={18} className="text-slateText-400 shrink-0" />
              <div className="text-left font-mono">
                <span className="text-[10px] text-slateText-400 block uppercase font-bold">
                  Last Updated
                </span>
                <span className="text-xs text-slateText-200 font-bold block">
                  {lastSyncedAt ? formatDate(lastSyncedAt) : "—"}
                </span>
              </div>
            </div>

            {/* Action Button */}
            {isOnline ? (
              <button
                onClick={onTriggerSync}
                disabled={isSyncing}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-accent-sky to-accent-teal hover:opacity-90 disabled:opacity-50 text-canvas-950 text-xs font-mono font-black uppercase tracking-wider transition-all shadow-[0_0_20px_rgba(6,182,212,0.35)] cursor-pointer"
              >
                <RefreshCw size={14} className={isSyncing ? "animate-spin" : ""} />
                <span>{isSyncing ? "Syncing..." : "Sync Now"}</span>
              </button>
            ) : (
              <button
                onClick={() => setShowOfflineModal(true)}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-canvas-900 hover:bg-canvas-800 border border-accent-amber/40 hover:border-accent-amber text-accent-amber text-xs font-mono font-bold uppercase tracking-wider transition-all shadow-md cursor-pointer"
              >
                <HardDrive size={14} />
                <span>Queued for Sync</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Offline Mode Information Dialog */}
      {showOfflineModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-accent-amber/50 bg-canvas-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-3 text-accent-amber">
              <div className="p-2 rounded-xl bg-accent-amber/20 border border-accent-amber/40">
                <Info size={20} />
              </div>
              <h3 className="text-base font-mono font-bold text-slateText-50">
                Offline Mode Active
              </h3>
            </div>

            <p className="text-xs font-mono text-slateText-300 leading-relaxed">
              Records will remain safely stored in local offline storage and synchronize automatically when Online mode is restored.
            </p>

            <div className="p-3 rounded-xl bg-canvas-950 border border-canvas-800 font-mono text-xs text-slateText-400 flex justify-between">
              <span>Locally Queued Records:</span>
              <span className="font-bold text-accent-amber">{pendingCount}</span>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowOfflineModal(false)}
                className="btn-primary text-xs font-mono py-2 px-4"
              >
                Understood
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
