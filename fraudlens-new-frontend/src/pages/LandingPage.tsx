import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FileText,
  BarChart2,
  ScanFace,
  FolderLock,
  Database,
  ScrollText,
  RefreshCw,
  Activity,
  Settings,
  Info,
  ChevronRight,
  FileSearch,
} from "lucide-react";
import { api } from "@/services/api";
import { useApp } from "@/context/AppContext";

export function LandingPage() {
  const { stats } = useApp();
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [modulesCount, setModulesCount] = useState<number>(7);
  const [currentTime, setCurrentTime] = useState<string>("");
  const [currentDate, setCurrentDate] = useState<string>("");

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

  // Backend Health Check
  useEffect(() => {
    let isMounted = true;
    async function checkHealth() {
      try {
        const health = await api.getHealth();
        if (isMounted) {
          if (health && (health.status === "HEALTHY" || health.status === "healthy")) {
            setBackendStatus("online");
            setModulesCount(health.modules_ready?.length || 7);
          } else {
            setBackendStatus("offline");
          }
        }
      } catch {
        if (isMounted) {
          setBackendStatus("offline");
        }
      }
    }
    checkHealth();
    return () => {
      isMounted = false;
    };
  }, []);

  // 10 Navigation Items arranged strictly in 2 rows of 5
  const navItemsRow1 = [
    {
      title: "Document Screening",
      caption: "Primary Pipeline",
      to: "/screening",
      icon: FileText,
    },
    {
      title: "Dashboard",
      caption: `${stats.totalScreened} Screened`,
      to: "/dashboard",
      icon: BarChart2,
    },
    {
      title: "Live Verification",
      caption: "Biometric Engine",
      to: "/live-verification",
      icon: ScanFace,
    },
    {
      title: "Evidence Dossier",
      caption: "Forensics",
      to: "/evidence",
      icon: FolderLock,
    },
    {
      title: "Database",
      caption: `${stats.totalScreened} Records`,
      to: "/database",
      icon: Database,
    },
  ];

  const navItemsRow2 = [
    {
      title: "Audit Logs",
      caption: "SHA-256 Chained",
      to: "/audit",
      icon: ScrollText,
    },
    {
      title: "Differential Sync",
      caption: "Offline-First",
      to: "/sync",
      icon: RefreshCw,
    },
    {
      title: "System Health",
      caption: backendStatus === "online" ? `${modulesCount}/7 Ready` : "Standby",
      to: "/health",
      icon: Activity,
    },
    {
      title: "Settings",
      caption: "Config",
      to: "/settings",
      icon: Settings,
    },
    {
      title: "About",
      caption: "Doc 9303 Compliant",
      to: "/about",
      icon: Info,
    },
  ];

  return (
    <div className="relative min-h-screen bg-[#030712] text-slate-100 flex flex-col justify-between overflow-x-hidden select-none font-sans">
      {/* Dynamic Ambient Background Elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
        {/* Radial Center Glow */}
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[650px] rounded-full blur-[140px] pointer-events-none opacity-40"
          style={{
            background:
              "radial-gradient(circle, rgba(0, 245, 160, 0.18) 0%, rgba(0, 217, 245, 0.12) 35%, transparent 75%)",
          }}
        />

        {/* Dotted World Map Grid */}
        <svg
          className="absolute inset-0 w-full h-full opacity-25"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <pattern
              id="dot-grid"
              x="0"
              y="0"
              width="24"
              height="24"
              patternUnits="userSpaceOnUse"
            >
              <circle cx="2" cy="2" r="1" fill="#00D9F5" opacity="0.4" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dot-grid)" />
        </svg>

        {/* Perspective Grid Floor at Bottom */}
        <div
          className="absolute bottom-0 left-0 right-0 h-48 opacity-30 pointer-events-none"
          style={{
            background:
              "linear-gradient(to top, rgba(0, 245, 160, 0.08) 0%, transparent 100%)",
            maskImage: "linear-gradient(to top, black, transparent)",
            WebkitMaskImage: "linear-gradient(to top, black, transparent)",
          }}
        >
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <line x1="0%" y1="100%" x2="50%" y2="0%" stroke="#00D9F5" strokeWidth="0.8" opacity="0.3" />
            <line x1="15%" y1="100%" x2="50%" y2="0%" stroke="#00D9F5" strokeWidth="0.8" opacity="0.3" />
            <line x1="30%" y1="100%" x2="50%" y2="0%" stroke="#00D9F5" strokeWidth="0.8" opacity="0.3" />
            <line x1="45%" y1="100%" x2="50%" y2="0%" stroke="#00D9F5" strokeWidth="0.8" opacity="0.3" />
            <line x1="55%" y1="100%" x2="50%" y2="0%" stroke="#00D9F5" strokeWidth="0.8" opacity="0.3" />
            <line x1="70%" y1="100%" x2="50%" y2="0%" stroke="#00D9F5" strokeWidth="0.8" opacity="0.3" />
            <line x1="85%" y1="100%" x2="50%" y2="0%" stroke="#00D9F5" strokeWidth="0.8" opacity="0.3" />
            <line x1="100%" y1="100%" x2="50%" y2="0%" stroke="#00D9F5" strokeWidth="0.8" opacity="0.3" />
            <line x1="0" y1="90%" x2="100%" y2="90%" stroke="#00F5A0" strokeWidth="0.6" opacity="0.25" />
            <line x1="0" y1="75%" x2="100%" y2="75%" stroke="#00F5A0" strokeWidth="0.6" opacity="0.2" />
            <line x1="0" y1="55%" x2="100%" y2="55%" stroke="#00F5A0" strokeWidth="0.6" opacity="0.15" />
          </svg>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 1. TOP HEADER                                                */}
      {/* ============================================================ */}
      <header className="relative z-20 w-full px-6 py-4 flex items-center justify-between border-b border-cyan-950/40 bg-[#030712]/70 backdrop-blur-md">
        {/* Left Branding */}
        <div className="flex items-center gap-3.5">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-950 to-emerald-950 border border-[#00F5A0]/50 shadow-[0_0_15px_rgba(0,245,160,0.3)]">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              className="w-5 h-5 text-[#00F5A0]"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m9 12 2 2 4-4"
              />
            </svg>
          </div>
          <div>
            <div className="flex items-baseline">
              <span className="text-xl font-black tracking-tight text-white">Fraud</span>
              <span className="text-xl font-black tracking-tight text-[#00F5A0]">Lens</span>
            </div>
            <p className="text-[11px] font-mono font-medium text-[#7E9AB8] tracking-wide">
              Border AI-DIDSS Console
            </p>
          </div>
        </div>

        {/* Right Status Indicator */}
        <div className="flex items-center gap-5">
          <div className="hidden sm:block text-[11px] font-mono font-bold tracking-[0.15em] text-[#5A7A9C]">
            SECURE BORDERS <span className="mx-1 text-cyan-800">|</span> SAFER NATIONS
          </div>

          <div className="flex items-center gap-3 px-3.5 py-1.5 rounded-full bg-[#05111E] border border-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.18)]">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500 shadow-[0_0_8px_#10B981]"></span>
              </span>
              <span className="text-xs font-mono font-bold tracking-wider text-emerald-400">
                {backendStatus === "online" ? "ONLINE" : backendStatus === "checking" ? "CONNECTING" : "STANDBY"}
              </span>
            </div>
            <div className="h-3.5 w-px bg-emerald-800/60" />
            <div className="text-right">
              <div className="text-[11px] font-mono font-bold text-slate-200 leading-none">
                {currentTime || "06:56 PM"}
              </div>
              <div className="text-[9px] font-mono text-[#7E9AB8] leading-none mt-0.5">
                {currentDate || "6 Sep 2026"}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ============================================================ */}
      {/* 2. CENTER HERO & VISUAL WORKBENCH                            */}
      {/* ============================================================ */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-4 py-6 max-w-7xl mx-auto w-full">
        {/* Overline Subheading */}
        <div className="text-center mb-2">
          <span className="text-[11px] sm:text-xs font-mono font-bold tracking-[0.25em] text-[#00D9F5] uppercase">
            AI-POWERED DOCUMENT INTELLIGENCE
          </span>
        </div>

        {/* Large Main Headline */}
        <h1 className="text-3xl sm:text-5xl md:text-6xl font-black text-center tracking-tight leading-tight mb-3">
          <span className="text-white">Verify Today. </span>
          <span className="bg-gradient-to-r from-[#00F5A0] to-[#00D9F5] bg-clip-text text-transparent drop-shadow-[0_0_25px_rgba(0,245,160,0.35)]">
            Safer Tomorrow.
          </span>
        </h1>

        {/* Feature Bullets Subtitle */}
        <div className="flex items-center justify-center flex-wrap gap-2 text-xs sm:text-sm font-medium text-[#8FA8C6] mb-8 text-center">
          <span>Multi-engine document screening</span>
          <span className="text-[#00F5A0] font-bold">•</span>
          <span>Biometric verification</span>
          <span className="text-[#00F5A0] font-bold">•</span>
          <span>Forensic analysis</span>
          <span className="text-[#00F5A0] font-bold">•</span>
          <span>Secure border operations</span>
        </div>

        {/* ============================================================ */}
        {/* 3. CENTER GRAPHICAL STAGE WITH HUD CARDS & LAUNCH CTA       */}
        {/* ============================================================ */}
        <div className="relative w-full max-w-5xl flex items-center justify-center py-4 my-2">
          {/* Left HUD Card: Tilted Holographic Passport */}
          <div className="hidden lg:flex flex-col items-center absolute left-2 xl:left-8 top-1/2 -translate-y-1/2 pointer-events-none opacity-85 select-none">
            <div
              className="relative w-52 h-68 rounded-2xl p-4 bg-gradient-to-br from-[#061928]/80 to-[#020A14]/90 border border-cyan-500/40 backdrop-blur-md shadow-[0_0_25px_rgba(0,217,245,0.15)] flex flex-col justify-between"
              style={{
                transform: "perspective(800px) rotateY(18deg) rotateX(4deg)",
              }}
            >
              {/* Top Passport Header */}
              <div>
                <div className="flex items-center justify-between text-[10px] font-mono text-[#00D9F5] mb-2">
                  <span className="font-bold tracking-wider">PASSPORT</span>
                  <span className="text-[8px] bg-cyan-950/60 px-1 py-0.5 rounded border border-cyan-500/30">
                    ICAO 9303
                  </span>
                </div>
                {/* Holographic Globe Wireframe */}
                <div className="relative my-3 flex items-center justify-center">
                  <svg className="w-20 h-20 text-[#00D9F5]/40" viewBox="0 0 100 100" fill="none" stroke="currentColor">
                    <circle cx="50" cy="50" r="45" strokeWidth="1.5" />
                    <ellipse cx="50" cy="50" rx="45" ry="18" strokeWidth="1.2" />
                    <ellipse cx="50" cy="50" rx="18" ry="45" strokeWidth="1.2" />
                    <line x1="5" y1="50" x2="95" y2="50" strokeWidth="1.2" />
                    <line x1="50" y1="5" x2="50" y2="95" strokeWidth="1.2" />
                  </svg>
                  {/* Biometric Chip Icon */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-8 h-6 rounded border border-[#00F5A0] bg-[#00F5A0]/10 flex items-center justify-center shadow-[0_0_10px_rgba(0,245,160,0.5)]">
                      <div className="w-3 h-3 rounded-full border border-[#00F5A0]" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Holographic MRZ Lines */}
              <div className="bg-[#020B16]/80 p-2 rounded-lg border border-cyan-900/50 font-mono text-[7px] text-[#00F5A0]/80 leading-tight">
                <div>P&lt;UTOERIKSSON&lt;&lt;ANNA&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;</div>
                <div>L898902C36UTO7408122F1204159ZE184226B&lt;&lt;&lt;&lt;&lt;</div>
              </div>

              {/* Corner Sci-Fi Brackets */}
              <div className="absolute top-1.5 left-1.5 w-3 h-3 border-t-2 border-l-2 border-[#00D9F5]" />
              <div className="absolute top-1.5 right-1.5 w-3 h-3 border-t-2 border-r-2 border-[#00D9F5]" />
              <div className="absolute bottom-1.5 left-1.5 w-3 h-3 border-b-2 border-l-2 border-[#00D9F5]" />
              <div className="absolute bottom-1.5 right-1.5 w-3 h-3 border-b-2 border-r-2 border-[#00D9F5]" />
            </div>
          </div>

          {/* Central Holographic Concentric Radar Elements */}
          <div className="relative flex flex-col items-center justify-center z-10">
            {/* Concentric Radar Circles */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none -z-10">
              <div className="w-72 sm:w-88 h-72 sm:h-88 rounded-full border border-cyan-500/15 animate-[spin_60s_linear_infinite]" />
              <div className="absolute w-56 sm:w-68 h-56 sm:h-68 rounded-full border border-emerald-500/20 border-dashed animate-[spin_40s_linear_infinite_reverse]" />
              <div className="absolute w-44 sm:w-52 h-44 sm:h-52 rounded-full border border-teal-500/10" />

              {/* Targeting HUD Brackets */}
              <div className="absolute -left-8 sm:-left-12 text-[#00F5A0] text-3xl font-light opacity-60">
                [
              </div>
              <div className="absolute -right-8 sm:-right-12 text-[#00F5A0] text-3xl font-light opacity-60">
                ]
              </div>
            </div>

            {/* MAIN LAUNCH SCREENING BUTTON */}
            <Link
              to="/screening"
              className="group relative inline-flex items-center justify-center gap-3.5 px-8 sm:px-11 py-4 sm:py-4.5 rounded-full bg-gradient-to-r from-[#00F5A0] via-[#00E5A3] to-[#00D9F5] text-slate-950 font-black text-base sm:text-lg tracking-wider uppercase shadow-[0_0_40px_rgba(0,245,160,0.55),0_0_80px_rgba(0,217,245,0.3)] hover:shadow-[0_0_55px_rgba(0,245,160,0.85),0_0_100px_rgba(0,217,245,0.45)] hover:scale-105 active:scale-95 transition-all duration-300 cursor-pointer"
            >
              {/* Glowing Outline Ring on Hover */}
              <span className="absolute -inset-1 rounded-full bg-gradient-to-r from-[#00F5A0] to-[#00D9F5] opacity-30 group-hover:opacity-75 blur-md transition-opacity duration-300 pointer-events-none" />

              {/* Document Search Icon */}
              <FileSearch className="w-6 h-6 text-slate-950 relative z-10 stroke-[2.5]" />

              {/* Text */}
              <span className="relative z-10 tracking-widest text-slate-950 font-extrabold">
                LAUNCH SCREENING
              </span>

              {/* Arrow */}
              <span className="relative z-10 text-xl font-bold group-hover:translate-x-1.5 transition-transform duration-200">
                →
              </span>
            </Link>

            {/* Subtext Below Launch Button */}
            <div className="mt-3.5 text-center">
              <span className="text-[10px] sm:text-[11px] font-mono font-bold tracking-[0.25em] text-[#7E9AB8] uppercase">
                UPLOAD • VERIFY • ANALYZE • PROTECT
              </span>
            </div>
          </div>

          {/* Right HUD Card: Tilted Holographic Biometric Identity */}
          <div className="hidden lg:flex flex-col items-center absolute right-2 xl:right-8 top-1/2 -translate-y-1/2 pointer-events-none opacity-85 select-none">
            <div
              className="relative w-52 h-68 rounded-2xl p-4 bg-gradient-to-bl from-[#061928]/80 to-[#020A14]/90 border border-cyan-500/40 backdrop-blur-md shadow-[0_0_25px_rgba(0,217,245,0.15)] flex flex-col justify-between"
              style={{
                transform: "perspective(800px) rotateY(-18deg) rotateX(4deg)",
              }}
            >
              {/* Top Face Scanner Header */}
              <div>
                <div className="flex items-center justify-between text-[10px] font-mono text-[#00D9F5] mb-2">
                  <span className="font-bold tracking-wider">BIOMETRIC 1:1</span>
                  <span className="text-[8px] bg-emerald-950/60 text-emerald-400 px-1 py-0.5 rounded border border-emerald-500/30">
                    LIVENESS
                  </span>
                </div>

                {/* Wireframe Face Mesh Illustration */}
                <div className="relative my-2 flex items-center justify-center">
                  <svg
                    className="w-24 h-24 text-[#00D9F5]/70"
                    viewBox="0 0 100 100"
                    fill="none"
                    stroke="currentColor"
                  >
                    {/* Outer Face Contour */}
                    <path
                      d="M25 35 C25 15, 75 15, 75 35 C75 60, 60 85, 50 90 C40 85, 25 60, 25 35 Z"
                      strokeWidth="1.5"
                    />
                    {/* Eyebrows and Eyes Mesh */}
                    <path d="M32 36 L44 36 M56 36 L68 36" strokeWidth="1.2" />
                    <circle cx="38" cy="42" r="4" strokeWidth="1.2" />
                    <circle cx="62" cy="42" r="4" strokeWidth="1.2" />
                    <circle cx="38" cy="42" r="1.5" fill="#00F5A0" />
                    <circle cx="62" cy="42" r="1.5" fill="#00F5A0" />
                    {/* Nose Bridge */}
                    <path d="M50 36 L50 58 L45 62 L55 62" strokeWidth="1.2" />
                    {/* Lips */}
                    <path d="M40 72 Q50 68 60 72 Q50 78 40 72 Z" strokeWidth="1.2" />
                    {/* Geometric Mesh Lines */}
                    <line x1="38" y1="42" x2="50" y2="58" strokeWidth="0.8" opacity="0.4" />
                    <line x1="62" y1="42" x2="50" y2="58" strokeWidth="0.8" opacity="0.4" />
                    <line x1="50" y1="58" x2="50" y2="68" strokeWidth="0.8" opacity="0.4" />
                    <line x1="25" y1="35" x2="38" y2="42" strokeWidth="0.8" opacity="0.4" />
                    <line x1="75" y1="35" x2="62" y2="42" strokeWidth="0.8" opacity="0.4" />
                  </svg>

                  {/* Scanning Horizontal Laser Bar */}
                  <div className="absolute inset-x-2 h-0.5 bg-gradient-to-r from-transparent via-[#00F5A0] to-transparent shadow-[0_0_8px_#00F5A0] animate-pulse" />
                </div>
              </div>

              {/* Bottom Badge */}
              <div className="bg-[#021812]/90 p-1.5 rounded-lg border border-emerald-500/50 font-mono text-[9px] text-emerald-400 font-bold text-center tracking-wider flex items-center justify-center gap-1.5 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                IDENTITY VERIFIED
              </div>

              {/* Corner Sci-Fi Brackets */}
              <div className="absolute top-1.5 left-1.5 w-3 h-3 border-t-2 border-l-2 border-[#00D9F5]" />
              <div className="absolute top-1.5 right-1.5 w-3 h-3 border-t-2 border-r-2 border-[#00D9F5]" />
              <div className="absolute bottom-1.5 left-1.5 w-3 h-3 border-b-2 border-l-2 border-[#00D9F5]" />
              <div className="absolute bottom-1.5 right-1.5 w-3 h-3 border-b-2 border-r-2 border-[#00D9F5]" />
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* 4. 10 NAVIGATION ITEMS (ROW 1 & ROW 2) — EXACT 5+5 CAPSULES  */}
        {/* ============================================================ */}
        <div className="w-full max-w-6xl mt-6 flex flex-col gap-3">
          {/* ROW 1 (5 ITEMS) */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 justify-items-center">
            {navItemsRow1.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="w-full max-w-[215px] h-[50px] px-3 py-2 rounded-xl bg-[#06121E]/85 border border-cyan-900/60 hover:border-[#00F5A0] hover:bg-[#0A2033] hover:shadow-[0_0_18px_rgba(0,245,160,0.28)] transition-all duration-200 group flex items-center justify-between cursor-pointer backdrop-blur-sm"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="flex-shrink-0 text-cyan-400 group-hover:text-[#00F5A0] group-hover:drop-shadow-[0_0_8px_rgba(0,245,160,0.6)] transition-all">
                      <Icon className="w-4 h-4" strokeWidth={2.2} />
                    </div>
                    <div className="min-w-0">
                      <div className="text-[11.5px] font-bold text-slate-100 group-hover:text-white truncate transition-colors">
                        {item.title}
                      </div>
                      <div className="text-[9px] font-mono text-[#5A7A9C] group-hover:text-[#00D9F5] truncate transition-colors">
                        {item.caption}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-[#00F5A0] group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-1" />
                </Link>
              );
            })}
          </div>

          {/* ROW 2 (5 ITEMS) */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 justify-items-center">
            {navItemsRow2.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="w-full max-w-[215px] h-[50px] px-3 py-2 rounded-xl bg-[#06121E]/85 border border-cyan-900/60 hover:border-[#00F5A0] hover:bg-[#0A2033] hover:shadow-[0_0_18px_rgba(0,245,160,0.28)] transition-all duration-200 group flex items-center justify-between cursor-pointer backdrop-blur-sm"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className="flex-shrink-0 text-cyan-400 group-hover:text-[#00F5A0] group-hover:drop-shadow-[0_0_8px_rgba(0,245,160,0.6)] transition-all">
                      <Icon className="w-4 h-4" strokeWidth={2.2} />
                    </div>
                    <div className="min-w-0">
                      <div className="text-[11.5px] font-bold text-slate-100 group-hover:text-white truncate transition-colors">
                        {item.title}
                      </div>
                      <div className="text-[9px] font-mono text-[#5A7A9C] group-hover:text-[#00D9F5] truncate transition-colors">
                        {item.caption}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-[#00F5A0] group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-1" />
                </Link>
              );
            })}
          </div>
        </div>
      </main>

      {/* ============================================================ */}
      {/* 5. FOOTER                                                    */}
      {/* ============================================================ */}
      <footer className="relative z-20 w-full px-6 py-3 border-t border-cyan-950/40 bg-[#030712]/90 backdrop-blur-md flex items-center justify-between flex-wrap gap-2 text-[11px] font-mono text-[#5A7A9C]">
        {/* Left */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-bold text-slate-300">FRAUDLENS</span>
          <span className="text-cyan-500 font-semibold">v1.0.0</span>
          <span>|</span>
          <span>Smart India Hackathon</span>
          <span>|</span>
          <span className="text-[#8FA8C6]">AI for a Safer Tomorrow</span>
        </div>

        {/* Right */}
        <div className="flex items-center gap-2 flex-wrap">
          <Link to="/about" className="hover:text-cyan-400 transition-colors">
            Privacy
          </Link>
          <span>|</span>
          <Link to="/about" className="hover:text-cyan-400 transition-colors">
            Terms
          </Link>
          <span>|</span>
          <Link to="/about" className="hover:text-cyan-400 transition-colors">
            Help
          </Link>
          <span>|</span>
          <span>Made in India 🇮🇳</span>
          <span>|</span>
          <span className="text-emerald-400">For a Safer World</span>
        </div>
      </footer>
    </div>
  );
}
