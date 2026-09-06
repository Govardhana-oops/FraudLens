import React from "react";
import { NavLink } from "react-router-dom";
import {
  Shield,
  LayoutDashboard,
  Scan,
  UserCheck,
  Folder,
  Database,
  RefreshCw,
  FileText,
  Activity,
  Settings,
} from "lucide-react";
import { useApp } from "@/context/AppContext";

export function Sidebar() {
  const { isLiveConnected } = useApp();

  const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { to: "/screening", label: "Screen Document", icon: Scan },
    { to: "/live-verification", label: "Live Verification", icon: UserCheck },
    { to: "/evidence", label: "Evidence Dossier", icon: Folder },
    { to: "/database", label: "Database", icon: Database },
    { to: "/sync", label: "Synchronization", icon: RefreshCw },
    { to: "/audit", label: "Audit Logs", icon: FileText },
    { to: "/health", label: "System Health", icon: Activity },
  ];

  return (
    <aside className="w-64 bg-[#0B0F17] border-r border-slate-800/80 flex flex-col justify-between shrink-0 select-none">
      {/* Brand Header */}
      <div>
        <div className="p-5 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-950/60 border border-teal-500/40 text-teal-400 shrink-0">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white">FraudLens</h1>
            <p className="text-[11px] text-slate-400">Screening Console</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="px-3 py-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  isActive
                    ? "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium border border-teal-500/60 bg-teal-950/30 text-teal-400 transition-colors"
                    : "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-900/50 transition-colors"
                }
              >
                <Icon size={17} className="shrink-0" />
                <span className="flex-1 truncate">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer / Settings Link */}
      <div className="p-3 border-t border-slate-800/60 space-y-1">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            isActive
              ? "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium border border-teal-500/60 bg-teal-950/30 text-teal-400 transition-colors"
              : "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-900/50 transition-colors"
          }
        >
          <Settings size={17} className="shrink-0" />
          <span>Settings</span>
        </NavLink>

        <div className="pt-2 px-3 flex items-center justify-between text-[11px] text-slate-500">
          <span>Backend status:</span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className={`h-2 w-2 rounded-full ${isLiveConnected ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
            <span className={isLiveConnected ? "text-emerald-400" : "text-amber-400"}>
              {isLiveConnected ? "ONLINE" : "OFFLINE"}
            </span>
          </span>
        </div>
      </div>
    </aside>
  );
}
