import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Scan,
  UserCheck,
  Folder,
  Database,
  RefreshCw,
  FileText,
  Activity,
  Settings,
  Home,
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
    { to: "/settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-60 bg-[#040A12] border-r border-cyan-950/70 flex flex-col justify-between shrink-0 select-none z-30">
      {/* Navigation Links */}
      <div className="py-4">
        {/* Navigation Category Label */}
        <div className="px-4 mb-2">
          <span className="text-[10px] font-mono font-bold tracking-[0.18em] text-[#5A7A9C] uppercase">
            OPERATIONS
          </span>
        </div>

        <nav className="px-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  isActive
                    ? "flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold border border-[#20E3C2]/60 bg-[#0B2535] text-[#20E3C2] shadow-[0_0_15px_rgba(32,227,194,0.22)] transition-all duration-200"
                    : "flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold text-[#7E9AB8] hover:text-white hover:bg-[#0A1A2B] hover:border-cyan-900/60 border border-transparent transition-all duration-200 group"
                }
              >
                <Icon size={16} className="shrink-0 group-hover:text-[#20E3C2] transition-colors" />
                <span className="flex-1 truncate">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom Hub & Landing Portal */}
      <div className="p-3 border-t border-cyan-950/60 space-y-2">
        <NavLink
          to="/"
          className="flex items-center gap-3 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#5A7A9C] hover:text-white hover:bg-[#0A1A2B] transition-colors"
        >
          <Home size={15} className="shrink-0 text-cyan-400" />
          <span className="truncate">Reference Landing Hub</span>
        </NavLink>

        <div className="px-3 py-2 rounded-lg bg-[#06101B] border border-cyan-950 flex items-center justify-between text-[11px] font-mono">
          <span className="text-[#5A7A9C]">FastAPI Core</span>
          <span className="flex items-center gap-1.5 font-bold">
            <span
              className={`h-2 w-2 rounded-full ${
                isLiveConnected ? "bg-emerald-400 shadow-[0_0_6px_#10B981] animate-pulse" : "bg-amber-400"
              }`}
            />
            <span className={isLiveConnected ? "text-emerald-400" : "text-amber-400"}>
              {isLiveConnected ? "CONNECTED" : "OFFLINE"}
            </span>
          </span>
        </div>
      </div>
    </aside>
  );
}
