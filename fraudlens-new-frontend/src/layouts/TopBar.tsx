import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Shield,
  Search,
  Bell,
  ChevronRight,
  ExternalLink,
} from "lucide-react";
import { useApp } from "@/context/AppContext";

export function TopBar() {
  const { settings, isLiveConnected, records } = useApp();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [currentTime, setCurrentTime] = useState("");
  const [currentDate, setCurrentDate] = useState("");
  const [showNotifications, setShowNotifications] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Live Clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: true,
        })
      );
      setCurrentDate(
        now.toLocaleDateString("en-GB", {
          day: "numeric",
          month: "short",
          year: "numeric",
        })
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Keyboard shortcut Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/database?q=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate("/database");
    }
  };

  const flaggedRecords = records.filter(
    (r) =>
      r.status === "WATCHLIST_HIT" ||
      r.status === "TAMPERED" ||
      r.status === "FRAUD_DETECTED" ||
      r.status === "REVIEW_REQUIRED"
  );

  return (
    <header className="h-16 bg-[#030712]/95 border-b border-cyan-950/70 px-6 flex items-center justify-between shrink-0 z-40 backdrop-blur-md">
      {/* Left Branding */}
      <div className="flex items-center gap-3.5">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-950 to-emerald-950 border border-[#20E3C2]/50 text-[#20E3C2] group-hover:shadow-[0_0_12px_rgba(32,227,194,0.4)] transition-all">
            <Shield className="h-5 w-5" strokeWidth={2.2} />
          </div>
          <div>
            <div className="flex items-baseline">
              <span className="text-base font-black tracking-tight text-white">Fraud</span>
              <span className="text-base font-black tracking-tight text-[#20E3C2]">Lens</span>
            </div>
            <p className="text-[10px] font-mono text-[#7E9AB8] leading-none">
              Border AI-DIDSS Console
            </p>
          </div>
        </Link>
      </div>

      {/* Center Search Field with Ctrl K Hint */}
      <div className="flex-1 max-w-lg mx-6 hidden md:block">
        <form onSubmit={handleSearchSubmit} className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#5A7A9C]" />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents, passengers, or reference IDs..."
            className="w-full pl-9 pr-16 py-1.5 rounded-full bg-[#06101B]/90 border border-cyan-950 text-xs text-slate-200 placeholder-[#5A7A9C] focus:outline-none focus:border-[#20E3C2] focus:ring-1 focus:ring-[#20E3C2]/50 transition-all font-sans"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[9px] font-mono font-bold bg-[#0A1624] px-2 py-0.5 rounded-full border border-cyan-900 text-cyan-400">
            Ctrl K
          </kbd>
        </form>
      </div>

      {/* Right Telemetry & Officer Info */}
      <div className="flex items-center gap-4">
        {/* ONLINE Status Indicator Pill */}
        <div className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-[#05111E] border border-emerald-500/40 shadow-[0_0_12px_rgba(16,185,129,0.18)]">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500 shadow-[0_0_6px_#10B981]"></span>
          </span>
          <span className="text-[11px] font-mono font-bold tracking-wider text-emerald-400">
            {isLiveConnected ? "ONLINE" : "STANDBY"}
          </span>
          <div className="h-3.5 w-px bg-emerald-800/60" />
          <div className="text-right leading-none">
            <span className="text-[11px] font-mono font-bold text-slate-200 block">
              {currentTime || "08:11 PM"}
            </span>
            <span className="text-[9px] font-mono text-[#7E9AB8] block mt-0.5">
              {currentDate || "6 Sep 2026"}
            </span>
          </div>
        </div>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-8 h-8 rounded-full bg-[#06101B] border border-cyan-950 text-[#7E9AB8] hover:text-[#20E3C2] hover:border-[#20E3C2]/50 transition-colors relative flex items-center justify-center"
            title="Security Notifications"
          >
            <Bell className="w-4 h-4" />
            {flaggedRecords.length > 0 ? (
              <span className="absolute -top-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-rose-500 text-[8px] font-mono font-bold text-white flex items-center justify-center shadow-[0_0_6px_#EF4444]">
                {flaggedRecords.length}
              </span>
            ) : null}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-72 p-3 rounded-xl bg-[#081524] border border-cyan-900 shadow-2xl z-50 animate-in fade-in slide-in-from-top-2">
              <div className="flex items-center justify-between pb-2 border-b border-cyan-950 mb-2">
                <span className="text-xs font-mono font-bold text-slate-200">
                  SECURITY NOTIFICATIONS
                </span>
                <span className="text-[10px] font-mono text-cyan-400 font-bold">
                  {flaggedRecords.length} Flagged
                </span>
              </div>
              {flaggedRecords.length === 0 ? (
                <div className="py-4 text-center text-xs text-[#5A7A9C]">
                  All screening telemetry normal. Zero security incidents.
                </div>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {flaggedRecords.slice(0, 4).map((r) => (
                    <Link
                      key={r.screening_id}
                      to={`/evidence?id=${r.screening_id}`}
                      onClick={() => setShowNotifications(false)}
                      className="block p-2 rounded-lg bg-[#050D18] hover:bg-rose-950/30 border border-cyan-950 hover:border-rose-500/50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono font-bold text-rose-400">
                          {r.status}
                        </span>
                        <ExternalLink className="w-3 h-3 text-[#5A7A9C]" />
                      </div>
                      <div className="text-[11px] font-bold text-slate-200 truncate mt-0.5">
                        {r.document_number || r.screening_id}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Officer Profile Pill */}
        <Link
          to="/settings"
          className="flex items-center gap-2.5 px-3 py-1 rounded-full bg-[#06101B] border border-cyan-950 hover:border-cyan-800 transition-colors group"
        >
          <div className="w-7 h-7 rounded-full bg-cyan-950 border border-cyan-700/80 flex items-center justify-center text-xs font-mono font-bold text-cyan-300">
            CP
          </div>
          <div className="text-left leading-tight">
            <div className="text-xs font-bold text-slate-200 group-hover:text-white transition-colors">
              Officer {settings.officerId || "CP-0082"}
            </div>
            <div className="text-[9px] font-mono text-[#5A7A9C]">
              {settings.checkpointName?.split("-")[0]?.trim() || "Terminal B"}
            </div>
          </div>
          <ChevronRight className="w-3.5 h-3.5 text-[#5A7A9C] group-hover:text-cyan-400 group-hover:translate-x-0.5 transition-all" />
        </Link>
      </div>
    </header>
  );
}
