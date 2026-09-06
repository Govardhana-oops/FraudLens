import React, { useState, useRef } from "react";
import { Link } from "react-router-dom";
import {
  UploadCloud,
  Camera,
  Wifi,
  WifiOff,
  RotateCcw,
  Shield,
  FolderLock,
  Download,
  Scan,
  X,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { StatusBadge } from "@/components/StatusBadge";
import { ExtractedFieldsGrid } from "@/components/ExtractedFieldsGrid";
import { ValidationChecksList } from "@/components/ValidationChecksList";
import { ForensicAnalysisCard } from "@/components/ForensicAnalysisCard";
import { BiometricComparison } from "@/components/BiometricComparison";
import { PipelineProgress } from "@/components/PipelineProgress";
import { generateSyntheticDocumentFile, type DemoScenario } from "@/utils/sampleDocs";
import { formatDate, formatScorePct } from "@/utils/formatters";
import type { DocumentType, UnifiedScreeningDossier } from "@/types";

export function DocumentScreeningPage() {
  const { currentResult, executeScreening, clearCurrentResult, isScreening, isLiveConnected } = useApp();

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [docPreviewUrl, setDocPreviewUrl] = useState<string | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<DemoScenario>("valid_passport");
  const [selectedDocType, setSelectedDocType] = useState<DocumentType>("PASSPORT");
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [pipelineStep, setPipelineStep] = useState(0);

  const demoScenarios: { id: DemoScenario; label: string }[] = [
    { id: "valid_passport", label: "Valid Passport" },
    { id: "expired_document", label: "Expired Document" },
    { id: "ocr_uncertainty", label: "OCR Uncertainty" },
    { id: "tampering_review", label: "Tampering Review" },
    { id: "face_review", label: "Face Review Required" },
  ];

  const docTypes: { type: DocumentType; label: string }[] = [
    { type: "PASSPORT", label: "Passport" },
    { type: "VISA", label: "Visa" },
    { type: "NATIONAL_ID", label: "National ID" },
    { type: "DRIVER_LICENSE", label: "Driving Licence" },
    { type: "RESIDENCE_PERMIT", label: "Permit" },
  ];

  // Handle File Selection
  const handleFileChange = (file: File | null) => {
    if (file) {
      setDocumentFile(file);
      const url = URL.createObjectURL(file);
      setDocPreviewUrl(url);
      runScreening(file);
    } else {
      setDocumentFile(null);
      if (docPreviewUrl) URL.revokeObjectURL(docPreviewUrl);
      setDocPreviewUrl(null);
    }
  };

  // Run Screening Pipeline
  const runScreening = async (fileToScreen: File) => {
    setPipelineStep(1);
    const stepInterval = setInterval(() => {
      setPipelineStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 350);

    try {
      await executeScreening(fileToScreen, null, selectedDocType);
      setPipelineStep(5);
    } catch (err) {
      console.error("Screening execution error:", err);
    } finally {
      clearInterval(stepInterval);
    }
  };

  // Handle Demo Scenario Click
  const handleSelectScenario = async (scenarioId: DemoScenario) => {
    setSelectedScenario(scenarioId);
    clearCurrentResult();
    const synthFile = await generateSyntheticDocumentFile(scenarioId);
    setDocumentFile(synthFile);
    const url = URL.createObjectURL(synthFile);
    setDocPreviewUrl(url);
    await runScreening(synthFile);
  };

  // Handle Reset / New Inspection
  const handleReset = () => {
    setDocumentFile(null);
    if (docPreviewUrl) URL.revokeObjectURL(docPreviewUrl);
    setDocPreviewUrl(null);
    clearCurrentResult();
    setPipelineStep(0);
  };

  // Webcam Capture Handlers
  const startCamera = async () => {
    setIsCameraOpen(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Webcam access error:", err);
      alert("Unable to access camera. Please check permissions or upload a file.");
      setIsCameraOpen(false);
    }
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "camera_capture.png", { type: "image/png" });
          stopCamera();
          handleFileChange(file);
        }
      }, "image/png");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((t) => t.stop());
    }
    setIsCameraOpen(false);
  };

  // Drag and Drop Handlers
  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const onDragLeave = () => {
    setIsDragOver(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
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
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,application/pdf"
        className="hidden"
        onChange={(e) => {
          if (e.target.files && e.target.files.length > 0) {
            handleFileChange(e.target.files[0]);
          }
        }}
      />

      {/* Top Header Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Document Screening</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Upload an identity document for multi-layer verification.
          </p>
        </div>

        {/* Status Pill Indicator */}
        <div className="flex items-center gap-1.5 p-1 rounded-full border border-slate-800 bg-slate-900/60 self-start sm:self-auto">
          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
              isLiveConnected ? "bg-teal-950/80 text-teal-400 border border-teal-500/40" : "text-slate-500"
            }`}
          >
            <Wifi size={13} className={isLiveConnected ? "text-teal-400 animate-pulse" : "text-slate-500"} />
            <span>ONLINE</span>
          </div>
          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${
              !isLiveConnected ? "bg-amber-950/80 text-amber-400 border border-amber-500/40" : "text-slate-500"
            }`}
          >
            <WifiOff size={13} />
            <span>OFFLINE</span>
          </div>
        </div>
      </div>

      {/* Input / Dropzone Area (Shown when no result) */}
      {!currentResult && (
        <div className="space-y-5">
          {/* Demo Scenario Box */}
          <div className="p-3 rounded-xl border border-slate-800/80 bg-slate-900/40 flex items-center gap-3 flex-wrap">
            <span className="text-xs font-medium text-slate-400 shrink-0">Demo scenario:</span>
            <div className="flex items-center gap-2 flex-wrap">
              {demoScenarios.map((sc) => (
                <button
                  key={sc.id}
                  type="button"
                  onClick={() => handleSelectScenario(sc.id)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-medium transition-all ${
                    selectedScenario === sc.id && documentFile
                      ? "border border-teal-500 bg-teal-950/50 text-teal-400 shadow-[0_0_12px_rgba(20,184,166,0.25)]"
                      : "border border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700 hover:text-white"
                  }`}
                >
                  {sc.label}
                </button>
              ))}
            </div>
          </div>

          {/* Document Type Selector Row */}
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-sm font-medium text-slate-400 shrink-0">Document type:</span>
            <div className="flex items-center gap-2 flex-wrap">
              {docTypes.map((dt) => (
                <button
                  key={dt.type}
                  type="button"
                  onClick={() => setSelectedDocType(dt.type)}
                  className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                    selectedDocType === dt.type
                      ? "border border-teal-500 bg-teal-950/50 text-teal-400 shadow-[0_0_12px_rgba(20,184,166,0.25)]"
                      : "border border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700 hover:text-white"
                  }`}
                >
                  {dt.label}
                </button>
              ))}
            </div>
          </div>

          {/* Screening Progress Indicator */}
          {isScreening && (
            <div className="p-6 rounded-2xl border border-teal-500/40 bg-slate-900/80 shadow-2xl">
              <PipelineProgress currentStep={pipelineStep} />
            </div>
          )}

          {/* Main Large Dropzone (Exact Match to Screenshot) */}
          {!isScreening && (
            <div
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
              className={`border-2 border-dashed rounded-2xl p-16 flex flex-col items-center justify-center text-center relative transition-all ${
                isDragOver
                  ? "border-teal-400 bg-teal-950/20 shadow-[0_0_24px_rgba(20,184,166,0.2)]"
                  : "border-slate-800/90 bg-[#090D14]/80 hover:border-slate-700"
              } bg-[linear-gradient(to_right,#1e293b18_1px,transparent_1px),linear-gradient(to_bottom,#1e293b18_1px,transparent_1px)] bg-[size:24px_24px]`}
            >
              {/* Cloud Icon */}
              <div
                onClick={() => fileInputRef.current?.click()}
                className="cursor-pointer flex flex-col items-center"
              >
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-900/80 border border-slate-800 text-teal-400 mb-4 hover:scale-105 transition-transform">
                  <UploadCloud className="h-8 w-8 text-teal-400" />
                </div>
                <p className="text-sm text-slate-200">
                  Drag & drop a document, or{" "}
                  <span className="text-teal-400 underline font-medium hover:text-teal-300">
                    browse files
                  </span>
                </p>
                <p className="text-xs text-slate-500 mt-1.5">
                  JPG, PNG or PDF • single document per screening
                </p>
              </div>

              {/* Capture Image Button */}
              <button
                type="button"
                onClick={startCamera}
                className="mt-6 inline-flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-lg border border-slate-700 bg-slate-800/60 text-slate-200 hover:bg-slate-700/60 hover:text-white transition-colors"
              >
                <Camera size={14} className="text-teal-400" />
                <span>Capture image</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Camera Live Capture Modal */}
      {isCameraOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Camera size={16} className="text-teal-400" />
                <span>Camera Inspection Feed</span>
              </h3>
              <button
                onClick={stopCamera}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
              >
                <X size={16} />
              </button>
            </div>

            <div className="relative rounded-xl overflow-hidden bg-black border border-slate-800 aspect-video flex items-center justify-center">
              <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
              <div className="absolute inset-8 border border-teal-400/40 rounded-lg pointer-events-none" />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={stopCamera}
                className="px-4 py-2 rounded-lg text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={capturePhoto}
                className="px-4 py-2 rounded-lg text-xs font-bold text-slate-950 bg-teal-400 hover:bg-teal-300 flex items-center gap-1.5"
              >
                <Camera size={14} />
                <span>Capture & Inspect</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Screening Results View (Rendered when currentResult exists) */}
      {currentResult && (
        <div className="space-y-6">
          {/* Action & Status Top Bar */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <StatusBadge status={currentResult.status} size="lg" />
              <div>
                <h2 className="text-lg font-bold text-white">
                  {currentResult.document_type?.toUpperCase() || "DOCUMENT"}{" "}
                  {currentResult.document_number ? `• ${currentResult.document_number}` : ""}
                </h2>
                <p className="text-xs text-slate-400">
                  Screening ID: <span className="font-mono text-slate-300">{currentResult.screening_id}</span> • Processed at {formatDate(currentResult.timestamp)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <button
                type="button"
                onClick={handleReset}
                className="px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-slate-200 flex items-center gap-2 transition-colors"
              >
                <RotateCcw size={14} />
                <span>New Inspection</span>
              </button>

              <button
                type="button"
                onClick={() => handleDownloadJSON(currentResult)}
                className="px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-slate-200 flex items-center gap-2 transition-colors"
              >
                <Download size={14} />
                <span>Export JSON</span>
              </button>

              <Link
                to={`/evidence?id=${currentResult.screening_id}`}
                className="px-4 py-2 rounded-lg bg-teal-400 hover:bg-teal-300 text-slate-950 text-xs font-bold flex items-center gap-2 shadow-[0_0_12px_rgba(20,184,166,0.3)] transition-colors"
              >
                <FolderLock size={14} />
                <span>Full Evidence Dossier</span>
              </Link>
            </div>
          </div>

          {/* Main Inspection Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Document Image & High-Level Metrics */}
            <div className="lg:col-span-4 space-y-6">
              {/* Document Image Card */}
              <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Inspected Credential Image
                </h3>
                {docPreviewUrl ? (
                  <div className="relative rounded-lg overflow-hidden border border-slate-800 bg-black aspect-[3/2] flex items-center justify-center">
                    <img src={docPreviewUrl} alt="Document" className="w-full h-full object-contain" />
                  </div>
                ) : (
                  <div className="rounded-lg border border-slate-800 bg-slate-950/60 aspect-[3/2] flex items-center justify-center text-xs text-slate-500">
                    No image preview available
                  </div>
                )}
              </div>

              {/* Confidence Breakdown Card */}
              <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Multi-Modal Confidence Matrix
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-center">
                    <div className="text-[11px] text-slate-400 mb-1">OCR Clarity</div>
                    <div className="text-base font-mono font-bold text-teal-400">
                      {formatScorePct(currentResult.confidence_score || 0.95)}
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-center">
                    <div className="text-[11px] text-slate-400 mb-1">Authenticity</div>
                    <div className="text-base font-mono font-bold text-emerald-400">
                      {formatScorePct(1.0 - (currentResult.tampering_analysis?.tampering_score || 0))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Biometric Comparison Card (if face verified) */}
              {currentResult.face_comparison && (
                <div className="p-5 rounded-xl border border-slate-800 bg-slate-900/40">
                  <BiometricComparison comparison={currentResult.face_comparison} />
                </div>
              )}
            </div>

            {/* Right Column: Extracted Fields & Validation Checks */}
            <div className="lg:col-span-8 space-y-6">
              {/* Extracted Fields */}
              <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Scan size={15} className="text-teal-400" />
                  <span>Extracted Credential Fields (OCR & MRZ)</span>
                </h3>
                <ExtractedFieldsGrid fields={currentResult.extracted_fields} />
              </div>

              {/* Validation & Security Rules */}
              <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                  <Shield size={15} className="text-teal-400" />
                  <span>Rule Engine & Cross-Modal Integrity Checks</span>
                </h3>
                <ValidationChecksList checks={currentResult.validation_checks} />
              </div>

              {/* Forensic Analysis Card */}
              {currentResult.tampering_analysis && (
                <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40">
                  <ForensicAnalysisCard analysis={currentResult.tampering_analysis} />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
