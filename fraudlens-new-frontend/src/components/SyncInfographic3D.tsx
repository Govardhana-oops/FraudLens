import React from "react";
import {
  Laptop,
  Server,
  Cloud,
  Lock,
  CheckCircle2,
  XCircle,
  Database,
  Shield,
  Wifi,
  WifiOff,
  FileText,
  HardDrive,
} from "lucide-react";

interface SyncInfographic3DProps {
  operatingMode: "ONLINE" | "OFFLINE";
  isLiveConnected: boolean;
  isSyncing: boolean;
  pendingCount: number;
  syncedCount: number;
  totalRecords: number;
}

export function SyncInfographic3D({
  operatingMode,
  isLiveConnected,
  isSyncing,
  pendingCount,
  syncedCount,
  totalRecords,
}: SyncInfographic3DProps) {
  const isOnline = operatingMode === "ONLINE";
  const isConnected = isOnline && isLiveConnected;

  return (
    <div className="relative rounded-2xl border border-canvas-600/80 bg-gradient-to-b from-canvas-900/90 via-canvas-950 to-[#030a16] p-6 lg:p-8 overflow-hidden shadow-[0_0_40px_rgba(3,10,25,0.8)]">
      {/* Background Cyber Grid & Glow */}
      <div className="absolute inset-0 bg-[radial-gradient(#06b6d4_1px,transparent_1px)] [background-size:24px_24px] opacity-10 pointer-events-none" />
      <div
        className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full blur-[100px] pointer-events-none transition-colors duration-700 ${
          isOnline
            ? "bg-accent-sky/15"
            : "bg-accent-amber/10"
        }`}
      />

      {/* 3-Column 3D Infographic Layout */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left: Terminal B (Local Database) */}
        <div className="lg:col-span-3 flex flex-col items-center text-center">
          {/* Header */}
          <div className="mb-4">
            <span className="text-xs font-mono font-black tracking-wider text-slateText-100 uppercase block">
              Terminal B
            </span>
            <span className="text-[11px] font-mono text-slateText-400">
              Local Database ({totalRecords} records)
            </span>
          </div>

          {/* 3D Laptop / Terminal Stage */}
          <div className="relative flex flex-col items-center justify-center my-2">
            {/* Glowing 3D Base Pedestal */}
            <div className="absolute -bottom-3 w-40 h-12 rounded-full bg-gradient-to-r from-accent-sky/20 via-accent-sky/40 to-accent-teal/20 blur-md transform -rotate-x-60 pointer-events-none animate-pulse" />
            <div className="absolute -bottom-2 w-36 h-10 rounded-full border border-accent-sky/50 bg-canvas-900/80 transform -rotate-x-60 pointer-events-none shadow-[0_0_20px_rgba(6,182,212,0.4)]" />

            {/* Laptop 3D Container */}
            <div className="relative z-10 p-5 rounded-2xl bg-gradient-to-b from-canvas-800 to-canvas-900 border border-accent-sky/50 shadow-[0_0_25px_rgba(6,182,212,0.3)] transition-transform duration-300 hover:scale-105">
              <div className="w-16 h-12 rounded-lg bg-canvas-950 border border-accent-sky/60 flex items-center justify-center text-accent-sky relative overflow-hidden">
                <FileText size={22} className="text-accent-sky animate-pulse" />
                <div className="absolute inset-x-0 bottom-0 h-0.5 bg-accent-sky shadow-[0_0_8px_#06b6d4]" />
              </div>
              <div className="w-20 h-1.5 rounded-full bg-canvas-700 border border-accent-sky/30 mt-1.5 mx-auto" />
            </div>
          </div>

          {/* Local Status Tag */}
          <div className="mt-4 flex items-center gap-1.5 text-[11px] font-mono font-bold text-accent-emerald">
            <div className="w-2 h-2 rounded-full bg-accent-emerald animate-ping" />
            <span>LOCAL ENGINE ACTIVE</span>
          </div>
        </div>

        {/* Center: Connecting Data Flow & Secure Sync Cloud */}
        <div className="lg:col-span-6 flex flex-col items-center justify-center text-center px-2">
          {/* Animated Flow Connectors */}
          <div className="w-full flex items-center justify-center relative py-6">
            {/* Flow Line Background */}
            <div
              className={`absolute inset-x-0 h-0.5 transition-colors duration-500 ${
                isConnected
                  ? "bg-gradient-to-r from-accent-sky via-accent-teal to-accent-emerald shadow-[0_0_12px_rgba(6,182,212,0.8)]"
                  : "bg-canvas-700/60"
              }`}
            />

            {/* Animated Data Packets Flowing (When Online) */}
            {isConnected && (
              <div className="absolute inset-x-0 flex items-center justify-around pointer-events-none">
                <div className="w-2 h-2 rounded-sm bg-accent-sky shadow-[0_0_8px_#06b6d4] animate-pulse" />
                <div className="w-2.5 h-2.5 rounded-sm bg-accent-teal shadow-[0_0_10px_#14b8a6] animate-ping" />
                <div className="w-2 h-2 rounded-sm bg-accent-emerald shadow-[0_0_8px_#10b981] animate-pulse" />
              </div>
            )}

            {/* 3D Cloud Centerpiece */}
            <div className="relative z-10 flex flex-col items-center">
              <div
                className={`relative flex items-center justify-center rounded-3xl p-6 border transition-all duration-500 shadow-2xl ${
                  isConnected
                    ? "bg-gradient-to-b from-canvas-850 to-canvas-900 border-accent-sky/60 shadow-[0_0_35px_rgba(6,182,212,0.35)]"
                    : isOnline
                    ? "bg-canvas-900 border-accent-amber/50 shadow-[0_0_25px_rgba(245,158,11,0.25)]"
                    : "bg-canvas-900 border-canvas-600 shadow-[0_0_25px_rgba(100,116,139,0.2)]"
                }`}
              >
                {/* Cloud Silhouette */}
                <div className="relative flex items-center justify-center">
                  <Cloud
                    size={54}
                    className={`transition-colors duration-500 ${
                      isConnected
                        ? "text-accent-sky fill-accent-sky/10 stroke-[1.5]"
                        : isOnline
                        ? "text-accent-amber fill-accent-amber/10 stroke-[1.5]"
                        : "text-slateText-400 fill-slateText-400/10 stroke-[1.5]"
                    }`}
                  />
                  <div className="absolute inset-0 flex items-center justify-center">
                    {isConnected ? (
                      <Lock size={20} className="text-accent-sky" />
                    ) : isOnline ? (
                      <WifiOff size={20} className="text-accent-amber" />
                    ) : (
                      <HardDrive size={20} className="text-slateText-300" />
                    )}
                  </div>
                </div>
              </div>

              {/* Secure Sync Title & Description */}
              <div className="mt-3">
                <span className="text-sm font-mono font-black text-slateText-50 tracking-tight block">
                  {isConnected
                    ? "Secure Sync"
                    : isOnline
                    ? "Connection Standby"
                    : "Local Storage Queue"}
                </span>
                <span className="text-[11px] font-mono text-slateText-300 mt-0.5 block">
                  {isConnected
                    ? "Encrypted • Verified • Real-time"
                    : isOnline
                    ? "Connecting to Central Gateway..."
                    : "Offline Mode • Records Preserved Locally"}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Central HQ (Border Database) */}
        <div className="lg:col-span-3 flex flex-col items-center lg:items-start text-center lg:text-left">
          {/* Header */}
          <div className="mb-4">
            <span className="text-xs font-mono font-black tracking-wider text-slateText-100 uppercase block">
              Central HQ
            </span>
            <span className="text-[11px] font-mono text-slateText-400">
              Border Database (Cloud Ledger)
            </span>
          </div>

          <div className="flex flex-col sm:flex-row lg:flex-col items-center lg:items-start gap-5 w-full">
            {/* 3D Server Tower Stage */}
            <div className="relative flex flex-col items-center justify-center my-2">
              {/* Glowing Pedestal */}
              <div
                className={`absolute -bottom-3 w-40 h-12 rounded-full blur-md transform -rotate-x-60 pointer-events-none transition-colors duration-500 ${
                  isConnected
                    ? "bg-gradient-to-r from-accent-teal/20 via-accent-emerald/40 to-accent-sky/20 animate-pulse"
                    : "bg-canvas-700/30"
                }`}
              />
              <div className="absolute -bottom-2 w-36 h-10 rounded-full border border-accent-teal/40 bg-canvas-900/80 transform -rotate-x-60 pointer-events-none shadow-[0_0_20px_rgba(20,184,166,0.3)]" />

              {/* 3D Server Rack */}
              <div className="relative z-10 p-4 rounded-2xl bg-gradient-to-b from-canvas-800 to-canvas-900 border border-accent-teal/50 shadow-[0_0_25px_rgba(20,184,166,0.25)] space-y-1.5 transition-transform duration-300 hover:scale-105">
                {[1, 2, 3].map((slot) => (
                  <div
                    key={slot}
                    className="w-16 h-3.5 rounded bg-canvas-950 border border-canvas-700 flex items-center justify-between px-1.5"
                  >
                    <div className="flex gap-1">
                      <div
                        className={`w-1 h-1 rounded-full ${
                          isConnected ? "bg-accent-emerald shadow-[0_0_4px_#10b981]" : "bg-canvas-600"
                        }`}
                      />
                      <div
                        className={`w-1 h-1 rounded-full ${
                          isConnected ? "bg-accent-sky shadow-[0_0_4px_#06b6d4]" : "bg-canvas-600"
                        }`}
                      />
                    </div>
                    <div className="w-3 h-0.5 bg-canvas-700 rounded-full" />
                  </div>
                ))}
              </div>
            </div>

            {/* Checkmark Feature Badges */}
            <div className="space-y-2 text-[11px] font-mono">
              <div className="flex items-center gap-2">
                {isConnected ? (
                  <CheckCircle2 size={14} className="text-accent-emerald shrink-0" />
                ) : (
                  <XCircle size={14} className="text-slateText-400 shrink-0" />
                )}
                <span className={isConnected ? "text-slateText-100 font-bold" : "text-slateText-400"}>
                  {isConnected ? "Secure Connection" : "Central Disconnected"}
                </span>
              </div>

              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-accent-emerald shrink-0" />
                <span className="text-slateText-100 font-bold">Data Integrity</span>
              </div>

              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-accent-emerald shrink-0" />
                <span className="text-slateText-100 font-bold">Incremental Sync</span>
              </div>

              <div className="flex items-center gap-2">
                <CheckCircle2 size={14} className="text-accent-emerald shrink-0" />
                <span className="text-slateText-100 font-bold">
                  {isOnline ? "Real-time Updates" : "Local Storage Ready"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
