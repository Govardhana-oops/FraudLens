import React from "react";
import { Link } from "react-router-dom";
import { Shield, Bell, RefreshCw, PlusCircle, Activity } from "lucide-react";
import { useApp } from "@/context/AppContext";

export function TopBar() {
  const { settings, isLiveConnected, refreshData } = useApp();

  return (
    <header className="h-16 bg-canvas-900 border-b border-canvas-600 px-6 flex items-center justify-between shrink-0 z-40">
      <div className="flex items-center gap-3">
        <div className="text-xs font-bold text-slateText-300 uppercase tracking-wider">
          Station: <span className="text-slateText-50 font-bold">{settings.checkpointName}</span>
        </div>
        <span className="rounded bg-canvas-850 px-2 py-0.5 text-[11px] font-mono font-bold text-brand-teal border border-canvas-600">
          {settings.checkpointId}
        </span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => refreshData()}
          className="p-2 rounded-lg bg-canvas-850 border border-canvas-600 text-slateText-300 hover:text-brand-teal hover:border-brand-teal/50 transition-colors"
          title="Refresh Data"
        >
          <RefreshCw size={16} />
        </button>

        <Link
          to="/health"
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-canvas-850 border border-canvas-600 text-xs font-bold text-slateText-200 hover:border-brand-teal/50 transition-colors"
        >
          <Activity size={14} className={isLiveConnected ? "text-accent-emerald" : "text-accent-amber"} />
          <span className="hidden sm:inline">Module Diagnostics</span>
        </Link>

        <Link
          to="/screening"
          className="btn-primary flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider shadow-glow-teal"
        >
          <PlusCircle size={14} />
          <span>Inspect Document</span>
        </Link>
      </div>
    </header>
  );
}
