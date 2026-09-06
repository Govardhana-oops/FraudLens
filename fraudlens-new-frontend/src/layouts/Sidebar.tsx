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
  Plane,
} from "lucide-react";
import { useApp } from "@/context/AppContext";

export function Sidebar() {
  const { settings } = useApp();

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
    <aside className="w-60 bg-[#030810] border-r border-cyan-950/70 flex flex-col justify-between shrink-0 select-none z-30">
      {/* Navigation Links */}
      <div className="py-4">
        <nav className="px-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  isActive
                    ? "flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold border border-[#20E3C2]/60 bg-[#0B2535] text-[#20E3C2] shadow-[0_0_15px_rgba(32,227,194,0.25)] transition-all duration-200"
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

      {/* Bottom Terminal Widget & Hackathon Footer */}
      <div className="p-3 border-t border-cyan-950/60 space-y-3">
        {/* Terminal Location Card Widget */}
        <div className="p-2.5 rounded-xl bg-[#06121E] border border-cyan-900/60 flex items-center gap-2.5 shadow-sm">
          <div className="w-10 h-10 rounded-lg bg-cyan-950/80 border border-cyan-800/80 flex items-center justify-center text-cyan-400 shrink-0 overflow-hidden relative">
            <Plane className="w-5 h-5 text-cyan-400 transform -rotate-45" />
            <div className="absolute inset-0 bg-gradient-to-t from-cyan-950/80 to-transparent" />
          </div>
          <div className="min-w-0">
            <div className="text-xs font-bold text-white truncate">
              {settings.checkpointName?.split("-")[0]?.trim() || "Terminal B"}
            </div>
            <div className="text-[10px] font-mono text-[#5A7A9C] truncate">
              {settings.checkpointName?.split("-")[1]?.trim() || "Primary Inspection"}
            </div>
          </div>
        </div>

        {/* Hackathon Footer Info */}
        <div className="px-1 text-[10px] font-mono text-[#4E6A88] space-y-0.5">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-500/60" />
            <span>v1.0.0</span>
          </div>
          <div>Smart India Hackathon</div>
          <div className="text-[#3E5670]">AI for a Safer Tomorrow</div>
        </div>
      </div>
    </aside>
  );
}
