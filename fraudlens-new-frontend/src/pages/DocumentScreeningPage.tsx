import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  FileCheck2,
  Scan,
  Shield,
  AlertTriangle,
  FolderLock,
  Download,
  RotateCcw,
  ExternalLink,
  Copy,
  Check,
  Sparkles,
  Camera,
  Layers,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { DocumentDropzone } from "@/components/DocumentDropzone";
import { PipelineProgress } from "@/components/PipelineProgress";
import { ConfidenceRing } from "@/components/ConfidenceRing";
import { StatusBadge } from "@/components/StatusBadge";
import { ExtractedFieldsGrid } from "@/components/ExtractedFieldsGrid";
import { ValidationChecksList } from "@/components/ValidationChecksList";
import { ForensicAnalysisCard } from "@/components/ForensicAnalysisCard";
import { BiometricComparison } from "@/components/BiometricComparison";
import { EmptyState } from "@/components/EmptyState";
import { formatDate, truncateMiddle } from "@/utils/formatters";
import type { DocumentType, UnifiedScreeningDossier } from "@/types";

export function DocumentScreeningPage() {
  const { currentResult, executeScreening, clearCurrentResult, isScreening, settings } = useApp();

  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [liveFaceFile, setLiveFaceFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<DocumentType>("PASSPORT");
  const [copiedHash, setCopiedHash] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(0);

  const docTypes: { type: DocumentType; label: string }[] = [
    { type: "PASSPORT", label: "Passport" },
    { type: "VISA", label: "Visa" },
    { type: "NATIONAL_ID", label: "National ID" },
    { type: "RESIDENCE_PERMIT", label: "Residence Permit" },
    { type: "DRIVER_LICENSE", label: "Driver License" },
    { type: "AUTO_DETECT", label: "Auto-Detect" },
  ];

  const handleStartScreening = async () => {
    if (!documentFile) return;

    // Simulate stepping for the progress bar visual while async API runs
    setPipelineStep(1);
    const stepInterval = setInterval(() => {
      setPipelineStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 400);

    try {
      await executeScreening(documentFile, liveFaceFile, docType);
      setPipelineStep(5);
    } catch (err) {
      console.error("Screening error:", err);
    } finally {
      clearInterval(stepInterval);
    }
  };

  const handleReset = () => {
    setDocumentFile(null);
    setLiveFaceFile(null);
    clearCurrentResult();
    setPipelineStep(0);
  };

  const handleCopyHash = (hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

  const handleDownloadJSON = (result: UnifiedScreeningDossier) => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Screening_${result.screening_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slateText-50 tracking-tight">Document Screening Terminal</h1>
            <span className="rounded bg-brand-teal/20 px-2 py-0.5 text-xs font-mono font-bold text-brand-teal border border-brand-teal/40">
              MODULE 1-7 ENSEMBLE
            </span>
          </div>
          <p className="text-sm font-semibold text-slateText-300">
            Multi-Engine OCR extraction, ICAO 9303 checksum validation, deep forensics, and biometric pairing
          </p>
        </div>

        {currentResult && (
          <div className="flex items-center gap-3">
            <button
              onClick={handleReset}
              className="btn-secondary flex items-center gap-2 text-xs font-bold uppercase tracking-wider"
            >
              <RotateCcw size={14} />
              <span>New Inspection</span>
            </button>

            <Link
              to={`/evidence?id=${currentResult.screening_id}`}
              className="btn-primary flex items-center gap-2 text-xs font-bold uppercase tracking-wider"
            >
              <FolderLock size={14} />
              <span>Full Dossier</span>
            </Link>
          </div>
        )}
      </div>

      {/* Input / Upload Section (When not showing results or when uploading) */}
      {!currentResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Document Dropzone */}
          <div className="lg:col-span-2 space-y-4">
            <div className="panel-3d p-6 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slateText-200">
                  Select Document Standard
                </label>
                <div className="flex flex-wrap gap-1.5">
                  {docTypes.map((dt) => (
                    <button
                      key={dt.type}
                      type="button"
                      onClick={() => setDocType(dt.type)}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                        docType === dt.type
                          ? "bg-brand-teal text-canvas-950 shadow-glow-teal font-black"
                          : "bg-canvas-850 text-slateText-300 border border-canvas-600 hover:border-canvas-500 hover:text-slateText-100"
                      }`}
                    >
                      {dt.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slateText-300 mb-2">
                  Document Image Feed (ID / Passport / Visa)
                </label>
                <DocumentDropzone
                  onFileSelected={setDocumentFile}
                  selectedFile={documentFile}
                  label="Drop passport or identity document here, or browse"
                />
              </div>
            </div>

            {/* Optional Companion Live Face Feed */}
            <div className="panel-3d p-6">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Camera className="h-4 w-4 text-brand-cyan" />
                  <label className="text-xs font-bold uppercase tracking-wider text-slateText-200">
                    Optional Companion Live Face (1:1 Biometrics)
                  </label>
                </div>
                <span className="text-[11px] font-mono text-slateText-300">OPTIONAL</span>
              </div>
              <p className="text-xs text-slateText-300 font-medium mb-3">
                Upload a live passenger selfie or capture from the inspection webcam to cross-verify against the credential photo.
              </p>
              <DocumentDropzone
                onFileSelected={setLiveFaceFile}
                selectedFile={liveFaceFile}
                label="Drop live traveler face image here, or capture"
              />
            </div>
          </div>

          {/* Screening Trigger & Inspector Card */}
          <div className="panel-3d p-6 flex flex-col justify-between space-y-6">
            <div className="space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slateText-100 flex items-center gap-2">
                <Shield size={16} className="text-brand-teal" />
                <span>Screening Configuration</span>
              </h2>

              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600">
                  <div className="text-[11px] font-bold text-slateText-400">OFFICER ID</div>
                  <div className="text-xs font-mono font-bold text-slateText-100">{settings.officerId}</div>
                </div>

                <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600">
                  <div className="text-[11px] font-bold text-slateText-400">CHECKPOINT NODE</div>
                  <div className="text-xs font-bold text-slateText-100">{settings.checkpointName} ({settings.checkpointId})</div>
                </div>

                <div className="p-3 rounded-lg bg-canvas-850 border border-canvas-600">
                  <div className="text-[11px] font-bold text-slateText-400">ACTIVE ENGINES</div>
                  <div className="text-xs font-bold text-accent-emerald flex items-center gap-1.5 mt-0.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent-emerald animate-pulse" />
                    <span>Multi-Engine OCR • ELA • Deep Tampering • 1:1 Face</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {isScreening && <PipelineProgress currentStep={pipelineStep} />}

              <button
                type="button"
                disabled={!documentFile || isScreening}
                onClick={handleStartScreening}
                className="btn-primary w-full py-3.5 text-sm uppercase tracking-wider font-black flex items-center justify-center gap-2 shadow-glow-teal disabled:opacity-50 disabled:pointer-events-none"
              >
                <Scan size={18} />
                <span>{isScreening ? "Processing Document Pipeline..." : "Execute Screening"}</span>
              </button>

              <p className="text-[11px] text-center text-slateText-400 font-medium">
                High-assurance verification via Module 7 pipeline ensemble
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Comprehensive Result Panels (When result exists) */}
      {currentResult && (
        <div className="space-y-6">
          {/* Result Overview Banner */}
          <div className="panel-3d p-6 border-brand-teal/40 bg-gradient-to-r from-canvas-900 via-canvas-850 to-canvas-900">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div className="flex items-start gap-4">
                <StatusBadge status={currentResult.status} size="lg" />
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-xl font-black text-slateText-50">
                      Screening Dossier: {currentResult.document_type || "PASSPORT"}
                    </h2>
                    <span className="rounded bg-canvas-850 px-2 py-0.5 text-xs font-mono font-bold text-slateText-200 border border-canvas-600">
                      {currentResult.document_number || "EXTRACTED"}
                    </span>
                  </div>
                  <p className="text-xs font-medium text-slateText-300 mt-1">
                    Processed at {formatDate(currentResult.timestamp)} • Latency: {currentResult.processing_time_ms || 0}ms • Officer: {currentResult.officer_id || settings.officerId}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-6 self-center lg:self-auto">
                <ConfidenceRing
                  score={currentResult.confidence_score || 0}
                  size={64}
                  label="Confidence"
                />
                <ConfidenceRing
                  score={1 - (currentResult.tampering_analysis?.tampering_score || 0)}
                  size={64}
                  label="Integrity"
                  color={
                    (currentResult.tampering_analysis?.tampering_score || 0) > 0.4
                      ? "#F43F5E"
                      : "#10B981"
                  }
                />
              </div>
            </div>

            {/* Cryptographic SHA-256 Provenance Strip */}
            <div className="mt-5 pt-4 border-t border-canvas-600 flex flex-wrap items-center justify-between gap-2 text-xs">
              <div className="flex items-center gap-2 text-slateText-300 font-mono">
                <span className="font-bold text-brand-teal">RECORD SHA-256:</span>
                <span className="text-slateText-200">{truncateMiddle(currentResult.record_hash, 24)}</span>
                <button
                  onClick={() => handleCopyHash(currentResult.record_hash)}
                  className="p-1 hover:text-brand-teal text-slateText-400 transition-colors"
                  title="Copy full hash"
                >
                  {copiedHash ? <Check size={14} className="text-accent-emerald" /> : <Copy size={14} />}
                </button>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleDownloadJSON(currentResult)}
                  className="btn-secondary text-[11px] py-1 px-2.5 uppercase tracking-wider flex items-center gap-1.5"
                >
                  <Download size={12} />
                  <span>Export JSON</span>
                </button>

                <Link
                  to={`/evidence?id=${currentResult.screening_id}`}
                  className="btn-primary text-[11px] py-1 px-2.5 uppercase tracking-wider flex items-center gap-1.5"
                >
                  <span>3D Evidence Graph</span>
                  <ExternalLink size={12} />
                </Link>
              </div>
            </div>
          </div>

          {/* Grid of Extracted Fields & Validation Checks */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ExtractedFieldsGrid fields={currentResult.extracted_fields} />
            <ValidationChecksList checks={currentResult.validation_checks} />
          </div>

          {/* Forensic Tampering & Biometrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ForensicAnalysisCard analysis={currentResult.tampering_analysis} />
            <BiometricComparison comparison={currentResult.face_comparison} />
          </div>
        </div>
      )}
    </div>
  );
}
