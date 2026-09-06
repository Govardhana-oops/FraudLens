import React from "react";
import {
  FileText,
  ShieldCheck,
  Radio,
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  HardDrive,
} from "lucide-react";
import { formatDate } from "@/utils/formatters";

interface SyncSummaryCardsProps {
  operatingMode: "ONLINE" | "OFFLINE";
  isLiveConnected: boolean;
  isSyncing: boolean;
  totalRecords: number;
  syncedCount: number;
  pendingCount: number;
  lastSyncedAt: string | null;
}

export function SyncSummaryCards({
  operatingMode,
  isLiveConnected,
  isSyncing,
  totalRecords,
  syncedCount,
  pendingCount,
  lastSyncedAt,
}: SyncSummaryCardsProps) {
  const isOnline = operatingMode === "ONLINE";
  const isConnected = isOnline && isLiveConnected;

  // Determine Sync Status
  let syncStatusLabel = "Up to Date";
  let syncStatusSub = lastSyncedAt ? `Last sync: ${formatDate(lastSyncedAt)}` : "Awaiting trigger";
  let syncStatusColor = "emerald";

  if (isSyncing) {
    syncStatusLabel = "Syncing...";
    syncStatusSub = "Replicating delta records to HQ";
    syncStatusColor = "sky";
  } else if (!isOnline) {
    syncStatusLabel = "Offline Queue";
    syncStatusSub = `${pendingCount} records stored locally`;
    syncStatusColor = "amber";
  } else if (!isLiveConnected) {
    syncStatusLabel = "Connection Unavailable";
    syncStatusSub = `${pendingCount} records buffered locally`;
    syncStatusColor = "amber";
  } else if (pendingCount > 0) {
    syncStatusLabel = "Sync Pending";
    syncStatusSub = `${pendingCount} records awaiting sync`;
    syncStatusColor = "amber";
  }

  const cards = [
    {
      id: "synced_records",
      title: isOnline ? "SYNCED RECORDS" : "LOCAL RECORDS",
      value: totalRecords,
      subtext: isOnline ? "Total records in sync" : "Total records in local ledger",
      icon: FileText,
      theme: "cyan",
    },
    {
      id: "sync_status",
      title: "SYNC STATUS",
      value: syncStatusLabel,
      subtext: syncStatusSub,
      icon: isSyncing ? RefreshCw : ShieldCheck,
      theme: syncStatusColor,
      isSpinning: isSyncing,
    },
    {
      id: "connection",
      title: "CONNECTION",
      value: isConnected ? "Online" : isOnline ? "Unavailable" : "Offline",
      subtext: isConnected
        ? "Secure HTTPS Channel"
        : isOnline
        ? "Gateway unreachable • Local buffer"
        : "Local database active",
      icon: Radio,
      theme: isConnected ? "emerald" : isOnline ? "amber" : "purple",
    },
    {
      id: "sync_mode",
      title: "SYNC MODE",
      value: isOnline ? "Real-time" : "Local Queue",
      subtext: isOnline ? "Automatic synchronization" : "Manual sync when online",
      icon: isOnline ? BarChart3 : HardDrive,
      theme: "gold",
    },
  ];

  const getThemeClasses = (theme: string) => {
    switch (theme) {
      case "emerald":
        return {
          border: "border-accent-emerald/40 hover:border-accent-emerald/70 shadow-[0_0_20px_rgba(16,185,129,0.12)]",
          bg: "bg-gradient-to-br from-canvas-900 via-canvas-950 to-emerald-950/20",
          iconBg: "bg-accent-emerald/15 text-accent-emerald border-accent-emerald/40",
          valColor: "text-accent-emerald",
        };
      case "amber":
        return {
          border: "border-accent-amber/40 hover:border-accent-amber/70 shadow-[0_0_20px_rgba(245,158,11,0.12)]",
          bg: "bg-gradient-to-br from-canvas-900 via-canvas-950 to-amber-950/20",
          iconBg: "bg-accent-amber/15 text-accent-amber border-accent-amber/40",
          valColor: "text-accent-amber",
        };
      case "purple":
        return {
          border: "border-purple-500/40 hover:border-purple-500/70 shadow-[0_0_20px_rgba(168,85,247,0.12)]",
          bg: "bg-gradient-to-br from-canvas-900 via-canvas-950 to-purple-950/20",
          iconBg: "bg-purple-500/15 text-purple-400 border-purple-500/40",
          valColor: isConnected ? "text-accent-emerald" : isOnline ? "text-purple-300" : "text-accent-amber",
        };
      case "gold":
        return {
          border: "border-amber-600/40 hover:border-amber-600/70 shadow-[0_0_20px_rgba(217,119,6,0.12)]",
          bg: "bg-gradient-to-br from-canvas-900 via-canvas-950 to-amber-950/20",
          iconBg: "bg-amber-500/15 text-amber-400 border-amber-500/40",
          valColor: "text-amber-400",
        };
      case "cyan":
      default:
        return {
          border: "border-accent-sky/40 hover:border-accent-sky/70 shadow-[0_0_20px_rgba(6,182,212,0.12)]",
          bg: "bg-gradient-to-br from-canvas-900 via-canvas-950 to-cyan-950/20",
          iconBg: "bg-accent-sky/15 text-accent-sky border-accent-sky/40",
          valColor: "text-slateText-50",
        };
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        const style = getThemeClasses(card.theme);

        return (
          <div
            key={card.id}
            className={`p-5 rounded-2xl border ${style.border} ${style.bg} transition-all duration-300 hover:translate-y-[-2px] flex flex-col justify-between`}
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] font-mono font-black uppercase tracking-wider text-slateText-300">
                {card.title}
              </span>
              <div className={`flex h-9 w-9 items-center justify-center rounded-xl border ${style.iconBg}`}>
                <Icon size={18} className={card.isSpinning ? "animate-spin" : ""} />
              </div>
            </div>

            <div>
              <div className={`text-2xl font-mono font-black tracking-tight ${style.valColor}`}>
                {card.value}
              </div>
              <p className="text-[11px] font-mono text-slateText-400 mt-1 truncate">
                {card.subtext}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
