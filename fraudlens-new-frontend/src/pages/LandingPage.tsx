import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Shield,
  FileCheck2,
  ScanFace,
  FolderLock,
  Database,
  RefreshCw,
  ScrollText,
  Activity,
  Settings,
  Info,
  ArrowRight,
  CheckCircle2,
  Cpu,
  Layers,
  Sparkles,
} from "lucide-react";
import { api } from "@/services/api";
import { useApp } from "@/context/AppContext";

export function LandingPage() {
  const { stats } = useApp();
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [modulesCount, setModulesCount] = useState<number>(0);

  useEffect(() => {
    async function checkHealth() {
      try {
        const health = await api.getHealth();
        if (health && (health.status === "HEALTHY" || health.status === "healthy")) {
          setBackendStatus("online");
          setModulesCount(health.modules_ready?.length || 7);
        } else {
          setBackendStatus("offline");
        }
      } catch {
        setBackendStatus("offline");
      }
    }
    checkHealth();
  }, []);

  const navCards = [
    {
      title: "Document Screening",
      desc: "Perform real-time multi-engine OCR, MRZ validation, and forensic tamper analysis.",
      to: "/screening",
      icon: FileCheck2,
      badge: "Primary Pipeline",
      variant: "teal",
    },
    {
      title: "Operations Dashboard",
      desc: "Live border security operational metrics, screening distribution, and active alerts.",
      to: "/dashboard",
      icon: Shield,
      badge: `${stats.totalScreened} Screened`,
      variant: "emerald",
    },
    {
      title: "Biometric Face Verification",
      desc: "1:1 Live facial matching and anti-spoofing liveness analysis against credential photo.",
      to: "/live-verification",
      icon: ScanFace,
      badge: "Biometric Engine",
      variant: "sky",
    },
    {
      title: "Forensic Evidence Dossier",
      desc: "Interactive 3D graph, tampering heatmaps, and cryptographic provenance trails.",
      to: "/evidence",
      icon: FolderLock,
      badge: "Forensics",
      variant: "amber",
    },
    {
      title: "Screening Database",
      desc: "Search, filter, inspect, and export verified records across all border checkpoints.",
      to: "/database",
      icon: Database,
      badge: `${stats.totalScreened} Records`,
      variant: "neutral",
    },
    {
      title: "Audit Ledger",
      desc: "Cryptographically linked immutable audit trail with SHA-256 chain verification.",
      to: "/audit",
      icon: ScrollText,
      badge: "SHA-256 Chained",
      variant: "emerald",
    },
    {
      title: "Differential Sync",
      desc: "Decentralized offline buffer synchronization with central border security HQ.",
      to: "/sync",
      icon: RefreshCw,
      badge: "Offline-First",
      variant: "teal",
    },
    {
      title: "System Health Diagnostics",
      desc: "Real-time health monitoring of Modules 1 through 7 sub-services and micro-engines.",
      to: "/health",
      icon: Activity,
      badge: backendStatus === "online" ? `${modulesCount}/7 Ready` : "Standby",
      variant: backendStatus === "online" ? "emerald" : "rose",
    },
    {
      title: "Console Settings",
      desc: "Configure officer credentials, checkpoint identifier, and inspection threshold tolerances.",
      to: "/settings",
      icon: Settings,
      badge: "Config",
      variant: "neutral",
    },
    {
      title: "System Architecture",
      desc: "ICAO Doc 9303 specifications, ISO/IEC 19794-5 standards, and multi-module pipelines.",
      to: "/about",
      icon: Info,
      badge: "Doc 9303 Compliant",
      variant: "neutral",
    },
  ];

  return (
    <div className="min-h-screen bg-canvas-950 text-slateText-100 flex flex-col justify-between">
      {/* Top Banner */}
      <header className="border-b border-canvas-600 bg-canvas-900/90 backdrop-blur-md px-6 py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-teal to-brand-cyan shadow-glow-teal">
              <Shield className="h-6 w-6 text-canvas-950" strokeWidth={2.5} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-black tracking-wider text-slateText-50">FRAUDLENS</h1>
                <span className="rounded bg-brand-teal/20 px-1.5 py-0.5 text-[10px] font-mono font-bold text-brand-teal border border-brand-teal/40">
                  AI-DIDSS
                </span>
              </div>
              <p className="text-xs font-semibold text-slateText-300">
                AI Document Intelligence & Border Security Screening System
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-canvas-850 border border-canvas-600">
              <span className="text-xs font-bold text-slateText-300">FastAPI Core:</span>
              {backendStatus === "checking" && (
                <span className="flex items-center gap-1.5 text-xs font-bold text-accent-amber">
                  <span className="h-2 w-2 rounded-full bg-accent-amber animate-pulse" /> Connecting...
                </span>
              )}
              {backendStatus === "online" && (
                <span className="flex items-center gap-1.5 text-xs font-bold text-accent-emerald">
                  <span className="h-2 w-2 rounded-full bg-accent-emerald shadow-glow-emerald" /> {modulesCount} Submodules Active
                </span>
              )}
              {backendStatus === "offline" && (
                <span className="flex items-center gap-1.5 text-xs font-bold text-accent-rose">
                  <span className="h-2 w-2 rounded-full bg-accent-rose shadow-glow-rose" /> Backend Standby
                </span>
              )}
            </div>

            <Link
              to="/screening"
              className="btn-primary flex items-center gap-2 text-xs uppercase tracking-wider"
            >
              <span>Launch Screening</span>
              <ArrowRight size={14} />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-12 flex-1 flex flex-col justify-center">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-teal/10 border border-brand-teal/30 text-brand-teal text-xs font-bold uppercase tracking-wider mb-4">
            <Sparkles size={14} />
            <span>Next-Generation Border Intelligence Console</span>
          </div>
          <h2 className="text-4xl sm:text-5xl font-extrabold text-slateText-50 tracking-tight leading-tight mb-4">
            High-Assurance Identity Verification & Forensic Tamper Detection
          </h2>
          <p className="text-base text-slateText-300 leading-relaxed max-w-2xl mx-auto">
            Zero-hardcoded, fully traceable document intelligence system combining Multi-Engine OCR,
            deep forensic tampering neural networks, biometric 1:1 facial matching, and SHA-256 cryptographic audit provenance.
          </p>
        </div>

        {/* Navigation Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-12">
          {navCards.map((card) => {
            const Icon = card.icon;
            return (
              <Link
                key={card.to}
                to={card.to}
                className="panel-3d group p-6 flex flex-col justify-between hover:border-brand-teal/60 transition-all duration-200"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-canvas-850 border border-canvas-600 group-hover:border-brand-teal/50 group-hover:bg-brand-teal/10 transition-colors">
                      <Icon className="h-6 w-6 text-brand-teal group-hover:text-brand-cyan transition-colors" strokeWidth={2.2} />
                    </div>
                    <span className="rounded-md bg-canvas-850 px-2.5 py-1 text-xs font-mono font-bold text-slateText-200 border border-canvas-600">
                      {card.badge}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-slateText-50 group-hover:text-brand-teal transition-colors mb-2">
                    {card.title}
                  </h3>
                  <p className="text-sm font-medium text-slateText-300 leading-relaxed">
                    {card.desc}
                  </p>
                </div>

                <div className="mt-6 flex items-center gap-1.5 text-xs font-bold text-brand-teal group-hover:translate-x-1 transition-transform">
                  <span>Open Console Module</span>
                  <ArrowRight size={14} />
                </div>
              </Link>
            );
          })}
        </div>

        {/* Feature Strip */}
        <div className="panel-3d p-6 border-canvas-600 bg-canvas-900/60 flex flex-wrap items-center justify-around gap-6">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="h-5 w-5 text-accent-emerald" />
            <div>
              <div className="text-xs font-bold text-slateText-100">ICAO Doc 9303 MRZ Engine</div>
              <div className="text-[11px] font-semibold text-slateText-300">Format checksums & check-digits</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Cpu className="h-5 w-5 text-brand-cyan" />
            <div>
              <div className="text-xs font-bold text-slateText-100">Multi-Engine OCR Ensemble</div>
              <div className="text-[11px] font-semibold text-slateText-300">EasyOCR • Tesseract • Hybrid</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Layers className="h-5 w-5 text-accent-amber" />
            <div>
              <div className="text-xs font-bold text-slateText-100">Deep Neural Forensics</div>
              <div className="text-[11px] font-semibold text-slateText-300">ELA, Copy-Move, Font Anomaly</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Shield className="h-5 w-5 text-accent-sky" />
            <div>
              <div className="text-xs font-bold text-slateText-100">Immutable Audit Ledger</div>
              <div className="text-[11px] font-semibold text-slateText-300">SHA-256 Merkle Provenance</div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-canvas-600 bg-canvas-950 px-6 py-4 text-center text-xs font-semibold text-slateText-400">
        FraudLens / AI-DIDSS Security Architecture • Projector-Ready Enterprise Console • All Rights Reserved
      </footer>
    </div>
  );
}
