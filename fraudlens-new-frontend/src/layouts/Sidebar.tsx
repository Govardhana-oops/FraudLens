import React from "react";
import { NavLink } from "react-router-dom";
import {
  Shield,
  LayoutDashboard,
  FileCheck2,
  ScanFace,
  FolderLock,
  Database,
  RefreshCw,
  ScrollText,
  Activity,
  Settings,
  Info,
} from "lucide-react";
import { useApp } from "@/context/AppContext";

export function Sidebar() {
  const { stats, isLiveConnected } = useApp();

  const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { to: "/screening", label: "Screening", icon: FileCheck2 },
    { to: "/live-verification", label: "Biometrics", icon: ScanFace },
    { to: "/evidence", label: "Evidence Dossier", icon: FolderLock },
    { to: "/database", label: "Database", icon: Database, badge: stats.totalScreened > 0 ? String(stats.totalScreened) : undefined },
    { to: "/sync", label: "HQ Sync", icon: RefreshCw },
    { to: "/audit", label: "Audit Ledger", icon: ScrollText },
    { to: "/health", label: "Diagnostics", icon: Activity },
    { to: "/settings", label: "Settings", icon: Settings },
    { to: "/about", label: "About & Standards", icon: Info },
  ];

  return (
    <aside className="w-64 bg-canvas-900 border-r border-canvas-600 flex flex-col justify-between shrink-0 select-none">
      {/* Brand Header */}
      <div>
        <div className="p-5 border-b border-canvas-600 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-teal to-brand-cyan shadow-glow-teal shrink-0">
            <Shield className="h-6 w-6 text-canvas-950" strokeWidth={2.5} />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-base font-black tracking-wider text-slateText-50">FRAUDLENS</span>
              <span className="rounded bg-brand-teal/20 px-1 py-0.2 text-[9px] font-mono font-bold text-brand-teal border border-brand-teal/40">
                PRO
              </span>
            </div>
            <p className="text-[11px] font-semibold text-slateText-300">Border AI-DIDSS Console</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  isActive ? "nav-link-active" : "nav-link-inactive"
                }
              >
                <Icon size={18} className="shrink-0" strokeWidth={2.2} />
                <span className="flex-1 truncate">{item.label}</span>
                {item.badge && (
                  <span className="rounded bg-canvas-850 px-1.5 py-0.5 text-[10px] font-mono font-bold text-brand-teal border border-canvas-600">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Status */}
      <div className="p-4 border-t border-canvas-600 bg-canvas-950/60">
        <div className="flex items-center justify-between text-xs">
          <span className="font-bold text-slateText-300">Backend Core:</span>
          <span className="flex items-center gap-1.5 font-bold font-mono text-[11px]">
            <span
              className={`h-2 w-2 rounded-full ${
                isLiveConnected ? "bg-accent-emerald shadow-glow-emerald" : "bg-accent-amber"
              }`}
            />
            <span className={isLiveConnected ? "text-accent-emerald" : "text-accent-amber"}>
              {isLiveConnected ? "FASTAPI ONLINE" : "LOCAL BUFFER"}
            </span>
          </span>
        </div>
      </div>
    </aside>
  );
}
