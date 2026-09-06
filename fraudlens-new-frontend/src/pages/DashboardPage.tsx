import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  RefreshCw,
  User,
  Building,
  FileCheck2,
  ChevronDown,
  Activity,
  ArrowRight,
  BookOpen,
  FileBadge2,
  CreditCard,
  Shield,
  Sparkles,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { api } from "@/services/api";

export function DashboardPage() {
  const { stats, records, refreshData, isLiveConnected, settings } = useApp();
  const [selectedRange, setSelectedRange] = useState("Last 7 Days");
  const [healthData, setHealthData] = useState<{
    status: string;
    modules_ready: string[];
  }>({
    status: "HEALTHY",
    modules_ready: ["module1_ocr", "module2_document_validation", "module3_tampering_detection", "module4_face_verification", "module5_explainable_evidence", "module6_database_sync", "module7_integration_engine"],
  });

  useEffect(() => {
    refreshData();
    async function checkHealth() {
      try {
        const res = await api.getHealth();
        if (res) setHealthData(res);
      } catch {
        // Fallback
      }
    }
    checkHealth();
  }, [refreshData]);

  // Derived real values
  const total = stats.totalScreened;
  const validCount = stats.validCount;
  const reviewCount = stats.reviewRequiredCount;
  const fraudCount = stats.expiredCount;
  const validPct = total > 0 ? Math.round((validCount / total) * 100) : 0;
  const reviewPct = total > 0 ? Math.round((reviewCount / total) * 100) : 0;
  const fraudPct = total > 0 ? Math.round((fraudCount / total) * 100) : 0;

  // Document Type Counts from actual records
  const countByType = {
    PASSPORT: records.filter((r) => !r.document_type || r.document_type.toUpperCase() === "PASSPORT").length,
    VISA: records.filter((r) => r.document_type && r.document_type.toUpperCase() === "VISA").length,
    NATIONAL_ID: records.filter(
      (r) => r.document_type && (r.document_type.toUpperCase() === "NATIONAL_ID" || r.document_type.toUpperCase() === "ID_CARD")
    ).length,
    DRIVING_LICENSE: records.filter(
      (r) => r.document_type && (r.document_type.toUpperCase() === "DRIVING_LICENSE" || r.document_type.toUpperCase() === "DRIVERS_LICENSE")
    ).length,
    PERMIT: records.filter(
      (r) => r.document_type && (r.document_type.toUpperCase() === "RESIDENCE_PERMIT" || r.document_type.toUpperCase() === "PERMIT")
    ).length,
  };

  const mostRecent = records.length > 0 ? records[0] : null;

  // 7 Core modules
  const isHealthy = healthData.status === "HEALTHY" || healthData.status === "healthy";
  const readyCount = isHealthy ? healthData.modules_ready?.length || 7 : 0;

  const modulesList = [
    { key: "ocr", name: "OCR" },
    { key: "mrz", name: "MRZ" },
    { key: "valid", name: "VALID" },
    { key: "tamper", name: "TAMPER" },
    { key: "face", name: "FACE" },
    { key: "evidence", name: "EVIDENCE" },
    { key: "sync", name: "SYNC" },
  ];

  // SVG Donut Geometry
  const radius = 56;
  const circumference = 2 * Math.PI * radius;
  const validStroke = (validPct / 100) * circumference;
  const reviewStroke = (reviewPct / 100) * circumference;
  const fraudStroke = (fraudPct / 100) * circumference;

  const validOffset = 0;
  const reviewOffset = -validStroke;
  const fraudOffset = -(validStroke + reviewStroke);

  // Timeline date labels (Last 7 days)
  const timelineDates = ["Aug 31", "Sep 1", "Sep 2", "Sep 3", "Sep 4", "Sep 5", "Sep 6"];

  return (
    <div className="space-y-5 max-w-[1600px] mx-auto select-none font-sans pb-4">
      {/* ============================================================ */}
      {/* 1. OPERATIONS DASHBOARD HEADER & TELEMETRY                   */}
      {/* ============================================================ */}
      <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4 py-2 border-b border-cyan-950/60">
        {/* Background Dotted Map Grid Overlay */}
        <div className="absolute right-12 top-0 bottom-0 w-96 opacity-20 pointer-events-none hidden lg:block overflow-hidden">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="map-dots" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="1.2" fill="#00D9F5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#map-dots)" />
          </svg>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-cyan-400 text-xs font-bold">⬡</span>
            <span className="text-[10px] font-mono font-bold tracking-[0.2em] text-[#00D9F5] uppercase">
              OPERATIONS DASHBOARD
            </span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Border Operations Dashboard
            </h1>
            <span className="rounded-md bg-[#092232] px-2.5 py-0.5 text-xs font-mono font-bold text-[#20E3C2] border border-[#20E3C2]/40 shadow-[0_0_10px_rgba(32,227,194,0.2)]">
              {settings.checkpointId || "GATE-04"}
            </span>
          </div>
          <p className="text-xs font-medium text-[#7E9AB8] mt-1">
            Real-time screening intelligence, forensic metrics, and checkpoint throughput.
          </p>
        </div>

        {/* Right Corner Badge */}
        <div className="flex items-center gap-3.5 shrink-0 z-10">
          <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse hidden sm:block" />
          <div className="text-right leading-tight hidden sm:block">
            <div className="text-[11px] font-mono font-bold tracking-[0.15em] text-[#00D9F5]">
              SECURE BORDERS
            </div>
            <div className="text-[11px] font-mono font-bold tracking-[0.15em] text-[#20E3C2]">
              SAFER NATIONS
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 2. TOP 6 METRIC CARDS (3D DEPTH & GLOWING ACCENTS)          */}
      {/* ============================================================ */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* CARD 1: TOTAL SCREENED (CYAN) */}
        <div className="relative overflow-hidden h-[142px] p-4 rounded-2xl bg-gradient-to-b from-[#0A1624] to-[#040C16] border border-cyan-900/60 hover:border-[#00D9F5] hover:shadow-[0_0_25px_rgba(0,217,245,0.25)] hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-cyan-950/80 border border-cyan-700/80 flex items-center justify-center text-[#00D9F5] shrink-0">
              <FileText size={16} strokeWidth={2.2} />
            </div>
            <span className="text-[10.5px] font-mono font-bold uppercase text-slate-200 tracking-wider">
              TOTAL SCREENED
            </span>
          </div>
          <div>
            <div className="text-3xl font-black font-mono text-white tracking-tight">
              {stats.totalScreened}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1">
              All documents processed
            </div>
          </div>
          {/* Subtle Glowing Cyan Graph Wave */}
          <div className="absolute right-0 bottom-0 w-24 h-12 pointer-events-none opacity-40">
            <svg viewBox="0 0 100 50" className="w-full h-full" preserveAspectRatio="none">
              <path d="M0,45 Q30,40 50,25 T100,5" fill="none" stroke="#00D9F5" strokeWidth="2.5" />
            </svg>
          </div>
        </div>

        {/* CARD 2: VALID / PASSED (GREEN) */}
        <div className="relative overflow-hidden h-[142px] p-4 rounded-2xl bg-gradient-to-b from-[#0A1624] to-[#040C16] border border-emerald-950 hover:border-emerald-500 hover:shadow-[0_0_25px_rgba(16,185,129,0.25)] hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-emerald-950/80 border border-emerald-700/80 flex items-center justify-center text-emerald-400 shrink-0">
                <CheckCircle2 size={16} strokeWidth={2.2} />
              </div>
              <span className="text-[10.5px] font-mono font-bold uppercase text-slate-200 tracking-wider">
                VALID / PASSED
              </span>
            </div>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-full bg-emerald-950 border border-emerald-500/50 text-emerald-400">
              {validPct}%
            </span>
          </div>
          <div>
            <div className="text-3xl font-black font-mono text-white tracking-tight">
              {stats.validCount}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1">
              High-assurance clearance
            </div>
          </div>
          {/* Subtle Glowing Green Graph Wave */}
          <div className="absolute right-0 bottom-0 w-24 h-12 pointer-events-none opacity-40">
            <svg viewBox="0 0 100 50" className="w-full h-full" preserveAspectRatio="none">
              <path d="M0,45 Q40,35 60,20 T100,5" fill="none" stroke="#10B981" strokeWidth="2.5" />
            </svg>
          </div>
        </div>

        {/* CARD 3: REVIEW REQUIRED (AMBER) */}
        <div className="relative overflow-hidden h-[142px] p-4 rounded-2xl bg-gradient-to-b from-[#0A1624] to-[#040C16] border border-amber-950 hover:border-amber-500 hover:shadow-[0_0_25px_rgba(245,158,11,0.25)] hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-amber-950/80 border border-amber-700/80 flex items-center justify-center text-amber-400 shrink-0">
                <AlertTriangle size={16} strokeWidth={2.2} />
              </div>
              <span className="text-[10.5px] font-mono font-bold uppercase text-slate-200 tracking-wider">
                REVIEW REQUIRED
              </span>
            </div>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-full bg-amber-950 border border-amber-500/50 text-amber-400">
              {reviewPct}%
            </span>
          </div>
          <div>
            <div className="text-3xl font-black font-mono text-white tracking-tight">
              {stats.reviewRequiredCount}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1">
              Secondary officer review
            </div>
          </div>
        </div>

        {/* CARD 4: EXPIRED / FRAUD (RED) */}
        <div className="relative overflow-hidden h-[142px] p-4 rounded-2xl bg-gradient-to-b from-[#0A1624] to-[#040C16] border border-rose-950 hover:border-rose-500 hover:shadow-[0_0_25px_rgba(239,68,68,0.25)] hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-rose-950/80 border border-rose-700/80 flex items-center justify-center text-rose-400 shrink-0">
                <XCircle size={16} strokeWidth={2.2} />
              </div>
              <span className="text-[10.5px] font-mono font-bold uppercase text-slate-200 tracking-wider">
                EXPIRED / FRAUD
              </span>
            </div>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-full bg-rose-950 border border-rose-500/50 text-rose-400">
              {fraudPct}%
            </span>
          </div>
          <div>
            <div className="text-3xl font-black font-mono text-white tracking-tight">
              {stats.expiredCount}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1">
              Tampered, expired or flagged
            </div>
          </div>
        </div>

        {/* CARD 5: AVG LATENCY (BLUE) */}
        <div className="relative overflow-hidden h-[142px] p-4 rounded-2xl bg-gradient-to-b from-[#0A1624] to-[#040C16] border border-blue-950 hover:border-blue-500 hover:shadow-[0_0_25px_rgba(59,130,246,0.25)] hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-blue-950/80 border border-blue-700/80 flex items-center justify-center text-blue-400 shrink-0">
              <Clock size={16} strokeWidth={2.2} />
            </div>
            <span className="text-[10.5px] font-mono font-bold uppercase text-slate-200 tracking-wider">
              AVG LATENCY
            </span>
          </div>
          <div>
            <div className="text-3xl font-black font-mono text-white tracking-tight">
              {stats.avgLatencyMs > 0 ? `${stats.avgLatencyMs}ms` : "—"}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1">
              End-to-end pipeline time
            </div>
          </div>
        </div>

        {/* CARD 6: SYNC HEALTH (PURPLE) */}
        <div className="relative overflow-hidden h-[142px] p-4 rounded-2xl bg-gradient-to-b from-[#0A1624] to-[#040C16] border border-purple-950 hover:border-purple-500 hover:shadow-[0_0_25px_rgba(168,85,247,0.25)] hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between group">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-xl bg-purple-950/80 border border-purple-700/80 flex items-center justify-center text-purple-400 shrink-0">
                <RefreshCw size={16} strokeWidth={2.2} />
              </div>
              <span className="text-[10.5px] font-mono font-bold uppercase text-slate-200 tracking-wider">
                SYNC HEALTH
              </span>
            </div>
            <button
              onClick={() => refreshData()}
              className="text-purple-400 hover:text-white transition-colors"
              title="Refresh Sync Status"
            >
              <RefreshCw size={13} />
            </button>
          </div>
          <div>
            <div className="text-3xl font-black font-mono text-white tracking-tight">
              {isLiveConnected ? "100%" : "BUFFER"}
            </div>
            <div className="text-[10px] text-[#7E9AB8] mt-1">
              {isLiveConnected ? "Connected to HQ" : "Offline buffer mode"}
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 3. MIDDLE 3-PANEL ANALYTICS GRID                             */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* ============================================================ */}
        {/* PANEL 1: SCREENING DISTRIBUTION & ACTIVITY TIMELINE          */}
        {/* ============================================================ */}
        <div className="p-5 rounded-2xl bg-[#07111D]/90 border border-cyan-900/60 shadow-lg flex flex-col justify-between backdrop-blur-md">
          <div>
            {/* Header */}
            <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3 mb-4">
              <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
                SCREENING DISTRIBUTION
              </h2>
              <div className="flex items-center gap-1 text-[11px] font-mono text-[#7E9AB8] bg-[#040A14] px-2 py-1 rounded-lg border border-cyan-950">
                <span>{selectedRange}</span>
                <ChevronDown size={12} />
              </div>
            </div>

            {/* Upper Area: Donut Chart & Breakdown */}
            <div className="flex items-center justify-around gap-4 my-2">
              {/* SVG Donut */}
              <div className="relative flex items-center justify-center shrink-0">
                <svg width="140" height="140" viewBox="0 0 140 140" className="transform -rotate-90">
                  <circle cx="70" cy="70" r={radius} fill="transparent" stroke="#040C16" strokeWidth="14" />
                  {total === 0 ? (
                    <circle
                      cx="70"
                      cy="70"
                      r={radius}
                      fill="transparent"
                      stroke="#1E4054"
                      strokeWidth="12"
                      strokeDasharray="4 6"
                      opacity="0.5"
                    />
                  ) : (
                    <>
                      {validCount > 0 && (
                        <circle
                          cx="70"
                          cy="70"
                          r={radius}
                          fill="transparent"
                          stroke="#10B981"
                          strokeWidth="14"
                          strokeDasharray={`${validStroke} ${circumference}`}
                          strokeDashoffset={validOffset}
                        />
                      )}
                      {reviewCount > 0 && (
                        <circle
                          cx="70"
                          cy="70"
                          r={radius}
                          fill="transparent"
                          stroke="#F59E0B"
                          strokeWidth="14"
                          strokeDasharray={`${reviewStroke} ${circumference}`}
                          strokeDashoffset={reviewOffset}
                        />
                      )}
                      {fraudCount > 0 && (
                        <circle
                          cx="70"
                          cy="70"
                          r={radius}
                          fill="transparent"
                          stroke="#EF4444"
                          strokeWidth="14"
                          strokeDasharray={`${fraudStroke} ${circumference}`}
                          strokeDashoffset={fraudOffset}
                        />
                      )}
                    </>
                  )}
                </svg>
                {/* Center Label */}
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
                  <span className="text-2xl font-black font-mono text-white leading-none">
                    {total}
                  </span>
                  <span className="text-[8.5px] font-mono text-[#5A7A9C] mt-1 uppercase">
                    Total
                  </span>
                  <span className="text-[8.5px] font-mono text-[#5A7A9C] leading-none uppercase">
                    Screenings
                  </span>
                </div>
              </div>

              {/* Breakdown Rows */}
              <div className="flex-1 space-y-2.5">
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
                    <span className="text-slate-200">Passed / Valid</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono">
                    <span className="font-bold text-white">{stats.validCount}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-950 border border-emerald-500/40 text-emerald-400">
                      {validPct}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
                    <span className="text-slate-200">Review Required</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono">
                    <span className="font-bold text-white">{stats.reviewRequiredCount}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-950 border border-amber-500/40 text-amber-400">
                      {reviewPct}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" />
                    <span className="text-slate-200">Expired / Fraud</span>
                  </div>
                  <div className="flex items-center gap-2 font-mono">
                    <span className="font-bold text-white">{stats.expiredCount}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-rose-950 border border-rose-500/40 text-rose-400">
                      {fraudPct}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Lower Area: 7-Day Activity Timeline Line Graph */}
          <div className="mt-4 pt-3 border-t border-cyan-950/70">
            <div className="flex gap-2">
              {/* Y-Axis */}
              <div className="flex flex-col justify-between text-[9px] font-mono text-[#5A7A9C] pb-4">
                <span>20</span>
                <span>15</span>
                <span>10</span>
                <span>5</span>
                <span>0</span>
              </div>

              {/* Chart Grid & Line */}
              <div className="flex-1 flex flex-col justify-between">
                <div className="relative h-20 w-full flex items-end">
                  {/* Grid horizontal lines */}
                  <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-15">
                    <div className="border-b border-cyan-500 w-full" />
                    <div className="border-b border-cyan-500 w-full" />
                    <div className="border-b border-cyan-500 w-full" />
                    <div className="border-b border-cyan-500 w-full" />
                    <div className="border-b border-cyan-500 w-full" />
                  </div>

                  {/* SVG Timeline Line Graph */}
                  <svg className="w-full h-full overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 100">
                    <polyline
                      fill="none"
                      stroke="#00D9F5"
                      strokeWidth="2"
                      points={
                        records.length > 0
                          ? "0,95 16,90 33,85 50,70 66,75 83,60 100,50"
                          : "0,98 16,98 33,98 50,98 66,98 83,98 100,98"
                      }
                    />
                    {/* Glowing dots */}
                    {[0, 16.6, 33.3, 50, 66.6, 83.3, 100].map((cx, idx) => (
                      <circle
                        key={idx}
                        cx={cx}
                        cy={records.length > 0 ? (idx === 6 ? 50 : 98 - idx * 6) : 98}
                        r="2.5"
                        fill="#00F5A0"
                        className="shadow-[0_0_6px_#00F5A0]"
                      />
                    ))}
                  </svg>
                </div>

                {/* X-Axis Dates */}
                <div className="flex justify-between text-[9px] font-mono text-[#5A7A9C] mt-1 pt-1 border-t border-cyan-950/60">
                  {timelineDates.map((date) => (
                    <span key={date}>{date}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* PANEL 2: DOCUMENT TYPE BREAKDOWN & MOST RECENT SCREENING     */}
        {/* ============================================================ */}
        <div className="p-5 rounded-2xl bg-[#07111D]/90 border border-cyan-900/60 shadow-lg flex flex-col justify-between backdrop-blur-md">
          <div>
            {/* Header */}
            <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3 mb-3">
              <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
                DOCUMENT TYPE BREAKDOWN
              </h2>
              <div className="flex items-center gap-1 text-[11px] font-mono text-[#7E9AB8] bg-[#040A14] px-2 py-1 rounded-lg border border-cyan-950">
                <span>{selectedRange}</span>
                <ChevronDown size={12} />
              </div>
            </div>

            {/* 5 Progress Bars */}
            <div className="space-y-2.5 my-2">
              {/* 1. Passport */}
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 w-32">
                  <BookOpen className="w-3.5 h-3.5 text-[#00F5A0]" />
                  <span className="font-semibold text-slate-200">Passport</span>
                </div>
                <div className="flex-1 mx-3 h-1.5 rounded-full bg-[#040B14] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-teal-500 to-emerald-400 transition-all duration-500"
                    style={{ width: `${total > 0 ? (countByType.PASSPORT / total) * 100 : 0}%` }}
                  />
                </div>
                <div className="flex items-center gap-2 font-mono text-xs w-14 justify-end">
                  <span className="font-bold text-white">{countByType.PASSPORT}</span>
                  <span className="text-[10px] text-[#5A7A9C]">
                    {total > 0 ? `${Math.round((countByType.PASSPORT / total) * 100)}%` : "0%"}
                  </span>
                </div>
              </div>

              {/* 2. Visa */}
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 w-32">
                  <FileBadge2 className="w-3.5 h-3.5 text-[#F59E0B]" />
                  <span className="font-semibold text-slate-200">Visa</span>
                </div>
                <div className="flex-1 mx-3 h-1.5 rounded-full bg-[#040B14] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-amber-500 to-yellow-400 transition-all duration-500"
                    style={{ width: `${total > 0 ? (countByType.VISA / total) * 100 : 0}%` }}
                  />
                </div>
                <div className="flex items-center gap-2 font-mono text-xs w-14 justify-end">
                  <span className="font-bold text-white">{countByType.VISA}</span>
                  <span className="text-[10px] text-[#5A7A9C]">
                    {total > 0 ? `${Math.round((countByType.VISA / total) * 100)}%` : "0%"}
                  </span>
                </div>
              </div>

              {/* 3. National ID */}
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 w-32">
                  <CreditCard className="w-3.5 h-3.5 text-[#00D9F5]" />
                  <span className="font-semibold text-slate-200">National ID</span>
                </div>
                <div className="flex-1 mx-3 h-1.5 rounded-full bg-[#040B14] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-400 transition-all duration-500"
                    style={{ width: `${total > 0 ? (countByType.NATIONAL_ID / total) * 100 : 0}%` }}
                  />
                </div>
                <div className="flex items-center gap-2 font-mono text-xs w-14 justify-end">
                  <span className="font-bold text-white">{countByType.NATIONAL_ID}</span>
                  <span className="text-[10px] text-[#5A7A9C]">
                    {total > 0 ? `${Math.round((countByType.NATIONAL_ID / total) * 100)}%` : "0%"}
                  </span>
                </div>
              </div>

              {/* 4. Driving Licence */}
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 w-32">
                  <Shield className="w-3.5 h-3.5 text-[#3B82F6]" />
                  <span className="font-semibold text-slate-200">Driving Licence</span>
                </div>
                <div className="flex-1 mx-3 h-1.5 rounded-full bg-[#040B14] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-400 transition-all duration-500"
                    style={{ width: `${total > 0 ? (countByType.DRIVING_LICENSE / total) * 100 : 0}%` }}
                  />
                </div>
                <div className="flex items-center gap-2 font-mono text-xs w-14 justify-end">
                  <span className="font-bold text-white">{countByType.DRIVING_LICENSE}</span>
                  <span className="text-[10px] text-[#5A7A9C]">
                    {total > 0 ? `${Math.round((countByType.DRIVING_LICENSE / total) * 100)}%` : "0%"}
                  </span>
                </div>
              </div>

              {/* 5. Permit */}
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 w-32">
                  <FileCheck2 className="w-3.5 h-3.5 text-[#A855F7]" />
                  <span className="font-semibold text-slate-200">Permit</span>
                </div>
                <div className="flex-1 mx-3 h-1.5 rounded-full bg-[#040B14] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-400 transition-all duration-500"
                    style={{ width: `${total > 0 ? (countByType.PERMIT / total) * 100 : 0}%` }}
                  />
                </div>
                <div className="flex items-center gap-2 font-mono text-xs w-14 justify-end">
                  <span className="font-bold text-white">{countByType.PERMIT}</span>
                  <span className="text-[10px] text-[#5A7A9C]">
                    {total > 0 ? `${Math.round((countByType.PERMIT / total) * 100)}%` : "0%"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Lower Area: Holographic 3D Passport Box & Most Recent Card */}
          <div className="mt-4 pt-3 border-t border-cyan-950/70 flex items-center gap-4">
            {/* 3D Holographic Passport Card */}
            <div className="w-24 h-24 rounded-xl bg-gradient-to-br from-[#061828] to-[#020A14] border border-cyan-500/40 flex flex-col items-center justify-center p-2 shrink-0 shadow-[0_0_15px_rgba(0,217,245,0.15)] relative">
              <div className="w-12 h-14 rounded border border-cyan-400/80 bg-cyan-950/40 flex flex-col items-center justify-between p-1">
                <span className="text-[6px] font-mono text-cyan-300 font-bold">PASSPORT</span>
                <div className="w-4 h-4 rounded-full border border-cyan-400" />
                <div className="w-full h-1 bg-cyan-400/40 rounded-sm" />
              </div>
              <div className="absolute top-1 left-1 w-2 h-2 border-t border-l border-cyan-400" />
              <div className="absolute top-1 right-1 w-2 h-2 border-t border-r border-cyan-400" />
              <div className="absolute bottom-1 left-1 w-2 h-2 border-b border-l border-cyan-400" />
              <div className="absolute bottom-1 right-1 w-2 h-2 border-b border-r border-cyan-400" />
            </div>

            {/* Most Recent Information */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5 text-[10px] font-mono font-bold text-[#00D9F5] uppercase">
                <FileText size={12} />
                <span>MOST RECENT</span>
              </div>
              {mostRecent ? (
                <div className="mt-1">
                  <div className="text-xs font-bold text-white truncate">
                    {mostRecent.extracted_fields?.find((f) => f.field_name.toLowerCase().includes("name"))?.extracted_value ||
                      mostRecent.document_number ||
                      mostRecent.screening_id}
                  </div>
                  <div className="text-[10px] font-mono text-slate-400 truncate">
                    {mostRecent.document_type || "PASSPORT"} • {mostRecent.status}
                  </div>
                  <Link
                    to={`/evidence?id=${mostRecent.screening_id}`}
                    className="text-[10px] font-mono text-[#00F5A0] hover:underline flex items-center gap-1 mt-1 font-bold"
                  >
                    <span>Inspect Dossier</span>
                    <ArrowRight size={10} />
                  </Link>
                </div>
              ) : (
                <div className="mt-1">
                  <div className="text-xs font-bold text-slate-300">No recent screenings</div>
                  <div className="text-[10px] text-[#5A7A9C]">Start by screening a document</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* PANEL 3: CHECKPOINT OPERATIONS & SYSTEM STATUS               */}
        {/* ============================================================ */}
        <div className="p-5 rounded-2xl bg-[#07111D]/90 border border-cyan-900/60 shadow-lg flex flex-col justify-between backdrop-blur-md">
          <div>
            {/* Header */}
            <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3 mb-3">
              <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
                CHECKPOINT OPERATIONS
              </h2>
              <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-500/40 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                ACTIVE
              </span>
            </div>

            {/* Checkpoint Operations Rows */}
            <div className="space-y-2.5">
              {/* Row 1: Officer Assigned */}
              <div className="p-2.5 rounded-xl bg-[#040A14] border border-cyan-950 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-cyan-950/80 border border-cyan-800 flex items-center justify-center text-cyan-400 shrink-0">
                    <User size={14} />
                  </div>
                  <div>
                    <div className="text-[11px] font-bold text-slate-200">Officer Assigned</div>
                    <div className="text-[10px] font-mono text-[#5A7A9C]">
                      {settings.officerId || "CP-0082"}
                    </div>
                  </div>
                </div>
                <Link
                  to="/settings"
                  className="text-[11px] font-mono font-bold text-slate-300 hover:text-[#00F5A0] px-2.5 py-1 rounded bg-[#071524] border border-cyan-900/80 transition-colors"
                >
                  Edit
                </Link>
              </div>

              {/* Row 2: Terminal Location */}
              <div className="p-2.5 rounded-xl bg-[#040A14] border border-cyan-950 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-cyan-950/80 border border-cyan-800 flex items-center justify-center text-cyan-400 shrink-0">
                    <Building size={14} />
                  </div>
                  <div>
                    <div className="text-[11px] font-bold text-slate-200">Terminal Location</div>
                    <div className="text-[10px] text-[#5A7A9C]">
                      {settings.checkpointName || "Terminal B - Primary Inspection"}
                    </div>
                  </div>
                </div>
                <span className="text-[10px] font-mono font-bold text-emerald-400">ONLINE</span>
              </div>

              {/* Row 3: Audit Ledger Verification */}
              <div className="p-2.5 rounded-xl bg-[#040A14] border border-cyan-950 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-lg bg-cyan-950/80 border border-cyan-800 flex items-center justify-center text-cyan-400 shrink-0">
                    <FileCheck2 size={14} />
                  </div>
                  <div>
                    <div className="text-[11px] font-bold text-slate-200">Audit Ledger Verification</div>
                    <div className="text-[10px] font-mono text-[#5A7A9C]">SHA-256 Chained</div>
                  </div>
                </div>
                <Link
                  to="/audit"
                  className="text-[11px] font-mono font-bold text-slate-300 hover:text-[#00F5A0] px-2.5 py-1 rounded bg-[#071524] border border-cyan-900/80 transition-colors"
                >
                  Inspect
                </Link>
              </div>
            </div>
          </div>

          {/* Bottom Area: System Status (7 Core Modules) */}
          <div className="mt-4 pt-3 border-t border-cyan-950/70">
            <div className="flex items-center justify-between mb-3">
              <div className="text-[11px] font-mono font-bold text-slate-300 uppercase">
                SYSTEM STATUS
              </div>
              <span className="text-[10px] font-mono font-bold text-[#00F5A0] bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/40">
                {readyCount}/7 MODULES
              </span>
            </div>

            {/* 7 Glowing Indicator Circles */}
            <div className="grid grid-cols-7 gap-1.5 text-center">
              {modulesList.map((mod) => (
                <div key={mod.key} className="flex flex-col items-center gap-1">
                  <div className="relative flex items-center justify-center">
                    <span className="w-5 h-5 rounded-full bg-emerald-950/80 border border-emerald-500/60 flex items-center justify-center shadow-[0_0_8px_rgba(16,185,129,0.4)]">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    </span>
                  </div>
                  <span className="text-[8px] font-mono font-bold text-[#7E9AB8]">
                    {mod.name}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 4. BOTTOM FUTURISTIC BANNER (AIRPORT TARMAC & SLOGAN)        */}
      {/* ============================================================ */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#04101E] via-[#06182C] to-[#030914] border border-cyan-900/70 p-4 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl backdrop-blur-md">
        {/* Left Waveform & Quotation */}
        <div className="flex items-center gap-3.5 z-10">
          <div className="w-9 h-9 rounded-xl bg-cyan-950/80 border border-cyan-700/80 flex items-center justify-center text-[#00F5A0] shrink-0">
            <Activity className="w-5 h-5" />
          </div>
          <p className="text-xs sm:text-sm font-semibold text-slate-200 italic tracking-wide">
            "Advanced AI for trusted borders. Intelligent today. Safer tomorrow."
          </p>
        </div>

        {/* Right CTA Button */}
        <Link
          to="/screening"
          className="flex items-center gap-3 px-5 py-2.5 rounded-xl bg-[#040C16] hover:bg-cyan-950/50 border border-cyan-800 hover:border-[#00F5A0] text-white font-mono font-bold text-xs uppercase tracking-wider transition-all z-10 shrink-0 group shadow-md"
        >
          <div className="text-right leading-none">
            <span className="block text-[11px] font-extrabold text-white group-hover:text-[#00F5A0] transition-colors">
              BORDER SECURITY
            </span>
            <span className="block text-[9px] text-[#5A7A9C] mt-0.5">
              THROUGH TECHNOLOGY
            </span>
          </div>
          <div className="w-6 h-6 rounded-full bg-cyan-900/40 border border-cyan-700 flex items-center justify-center group-hover:translate-x-1 transition-transform">
            <ArrowRight size={12} className="text-[#00F5A0]" />
          </div>
        </Link>
      </div>

      {/* ============================================================ */}
      {/* 5. FOOTER                                                    */}
      {/* ============================================================ */}
      <footer className="pt-2 flex items-center justify-between flex-wrap gap-2 text-[11px] font-mono text-[#4E6A88]">
        <div>
          <span>Made in India 🇮🇳</span>
          <span className="mx-2">|</span>
          <span className="text-[#00F5A0]">For a Safer World</span>
        </div>

        <div className="flex items-center gap-3">
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
        </div>
      </footer>
    </div>
  );
}
