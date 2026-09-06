import React from "react";
import {
  Info,
  Shield,
  Cpu,
  Layers,
  CheckCircle2,
  FileCheck2,
  Lock,
} from "lucide-react";

export function AboutPage() {
  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slateText-50 tracking-tight">System Architecture & Standards</h1>
        <p className="text-sm font-semibold text-slateText-300">
          FraudLens / AI-DIDSS (AI-Driven Document Intelligence & Security System) Specifications
        </p>
      </div>

      {/* System Overview */}
      <div className="panel-3d p-6 space-y-4">
        <h2 className="text-base font-bold text-slateText-50 flex items-center gap-2">
          <Shield size={18} className="text-brand-teal" />
          <span>Core System Architecture</span>
        </h2>
        <p className="text-xs text-slateText-300 leading-relaxed font-medium">
          FraudLens is a production-grade multi-engine document intelligence and border security inspection system.
          It combines high-accuracy optical character recognition (EasyOCR, Tesseract, OCR-B algorithms),
          deep neural forensic tamper detection (Error Level Analysis, Copy-Move keypoints, Font Anomaly detectors),
          1:1 biometric facial comparison with anti-spoofing liveness verification, and cryptographic SHA-256 chained audit ledgers.
        </p>
      </div>

      {/* Standards Compliance */}
      <div className="panel-3d p-6 space-y-4">
        <h2 className="text-base font-bold text-slateText-50 flex items-center gap-2">
          <FileCheck2 size={18} className="text-accent-emerald" />
          <span>International Standards Compliance</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-canvas-850 border border-canvas-600 space-y-1.5">
            <div className="text-xs font-bold text-brand-teal">ICAO Doc 9303 (Parts 1-12)</div>
            <p className="text-xs text-slateText-300 font-medium">
              Machine Readable Travel Documents (MRTDs), TD1, TD2, and TD3 specifications with 7-3-1 check digit algorithms.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-canvas-850 border border-canvas-600 space-y-1.5">
            <div className="text-xs font-bold text-brand-teal">ISO/IEC 19794-5</div>
            <p className="text-xs text-slateText-300 font-medium">
              Biometric data interchange formats for facial recognition data and photographic quality standards.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-canvas-850 border border-canvas-600 space-y-1.5">
            <div className="text-xs font-bold text-brand-teal">BSI TR-03105</div>
            <p className="text-xs text-slateText-300 font-medium">
              Conformity testing for electronic identity documents and optical inspection verification tolerances.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-canvas-850 border border-canvas-600 space-y-1.5">
            <div className="text-xs font-bold text-brand-teal">NIST SP 800-76</div>
            <p className="text-xs text-slateText-300 font-medium">
              Biometric specifications for personal identity verification and cryptographic chain hashing.
            </p>
          </div>
        </div>
      </div>

      {/* Multi-Module Pipeline */}
      <div className="panel-3d p-6 space-y-4">
        <h2 className="text-base font-bold text-slateText-50 flex items-center gap-2">
          <Layers size={18} className="text-brand-cyan" />
          <span>Submodule Architecture (Modules 1 - 8)</span>
        </h2>

        <div className="space-y-2 font-mono text-xs">
          <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
            <span className="text-slateText-300">Module 1: Document OCR & Preprocessing</span>
            <span className="text-brand-teal font-bold">Multi-Engine OCR Resolver</span>
          </div>
          <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
            <span className="text-slateText-300">Module 2: Rule-Based Logic & Validation</span>
            <span className="text-brand-teal font-bold">ICAO Checksum Engines</span>
          </div>
          <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
            <span className="text-slateText-300">Module 3: Security & Tamper Detection</span>
            <span className="text-brand-teal font-bold">ELA & Neural Forensics</span>
          </div>
          <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
            <span className="text-slateText-300">Module 4: Biometric Face Verification</span>
            <span className="text-brand-teal font-bold">ArcFace 1:1 Biometrics</span>
          </div>
          <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
            <span className="text-slateText-300">Module 5: Watchlist & Risk Assessment</span>
            <span className="text-brand-teal font-bold">Interpol SLTD & Risk Scoring</span>
          </div>
          <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
            <span className="text-slateText-300">Module 6: Audit Logging & Integrity</span>
            <span className="text-brand-teal font-bold">SHA-256 Merkle Ledger</span>
          </div>
          <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
            <span className="text-slateText-300">Module 7: Core Integration Pipeline</span>
            <span className="text-brand-teal font-bold">Pipeline Orchestrator</span>
          </div>
          <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600 flex justify-between">
            <span className="text-slateText-300">Module 8: Backend API & Gateway</span>
            <span className="text-brand-teal font-bold">FastAPI REST Endpoints</span>
          </div>
        </div>
      </div>
    </div>
  );
}
