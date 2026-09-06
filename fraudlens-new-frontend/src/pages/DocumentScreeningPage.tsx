import React, { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  UploadCloud,
  Camera,
  Wifi,
  WifiOff,
  RotateCcw,
  X,
  CheckCircle2,
  Scan,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { SequentialScenarioTracker } from "@/components/SequentialScenarioTracker";
import { InteractiveProcessingPipeline } from "@/components/InteractiveProcessingPipeline";
import { OcrExtractionDetailsCard } from "@/components/OcrExtractionDetailsCard";
import { ForensicAnalysisCards } from "@/components/ForensicAnalysisCards";
import { FinalScreeningBanner } from "@/components/FinalScreeningBanner";
import { generateSyntheticDocumentFile, type DemoScenario } from "@/utils/sampleDocs";
import type { DocumentType } from "@/types";

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
  const [pipelineStep, setPipelineStep] = useState(0); // 0 to 5
  const [activeAnimationStep, setActiveAnimationStep] = useState(0); // 0 to 5

  const docTypes: { type: DocumentType; label: string }[] = [
    { type: "PASSPORT", label: "Passport" },
    { type: "VISA", label: "Visa" },
    { type: "NATIONAL_ID", label: "National ID" },
    { type: "DRIVER_LICENSE", label: "Driving Licence" },
    { type: "RESIDENCE_PERMIT", label: "Permit" },
  ];

  // Auto-load initial synthetic passport if no file or result is present for instant demo display
  useEffect(() => {
    let isMounted = true;
    async function initInitialDocument() {
      if (!documentFile && !currentResult) {
        try {
          const defaultFile = await generateSyntheticDocumentFile("valid_passport");
          if (isMounted) {
            setDocumentFile(defaultFile);
            const url = URL.createObjectURL(defaultFile);
            setDocPreviewUrl(url);
            // Automatically execute screening pipeline
            runScreening(defaultFile);
          }
        } catch (e) {
          console.error("Initial synthetic document generation error:", e);
        }
      }
    }
    initInitialDocument();
    return () => {
      isMounted = false;
    };
  }, []);

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
      clearCurrentResult();
    }
  };

  // Run Complete Multi-Modal Screening Pipeline with Stage-by-Stage Sequential Animation
  const runScreening = async (fileToScreen: File) => {
    setPipelineStep(1);
    setActiveAnimationStep(1);

    // Sequential stage step timer (lights up stages 1 -> 2 -> 3 -> 4 -> 5)
    let currentStep = 1;
    const interval = setInterval(() => {
      currentStep += 1;
      if (currentStep <= 5) {
        setPipelineStep(currentStep);
        setActiveAnimationStep(currentStep);
      }
    }, 450);

    try {
      await executeScreening(fileToScreen, null, selectedDocType);
      setPipelineStep(5);
      setActiveAnimationStep(6);
    } catch (err) {
      console.error("Screening execution error:", err);
    } finally {
      clearInterval(interval);
    }
  };

  // Handle Demo Scenario Click
  const handleSelectScenario = async (scenarioId: DemoScenario) => {
    setSelectedScenario(scenarioId);
    clearCurrentResult();
    const synthFile = await generateSyntheticDocumentFile(scenarioId);
    setDocumentFile(synthFile);
    if (docPreviewUrl) URL.revokeObjectURL(docPreviewUrl);
    const url = URL.createObjectURL(synthFile);
    setDocPreviewUrl(url);
    await runScreening(synthFile);
  };

  // Handle Replace / Reset
  const handleReplace = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
      fileInputRef.current.click();
    }
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
    canvas.width = videoRef.current.videoWidth || 960;
    canvas.height = videoRef.current.videoHeight || 640;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
          stopCamera();
          handleFileChange(file);
        }
      }, "image/jpeg", 0.95);
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

  const fileSizeLabel = documentFile
    ? `${(documentFile.size / (1024 * 1024)).toFixed(1)} MB`
    : "2.1 MB";

  const fileNameLabel = documentFile ? documentFile.name : "passport.jpg";

  return (
    <div className="space-y-4 max-w-[1600px] mx-auto select-none font-sans pb-6">
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

      {/* ============================================================ */}
      {/* 1. TOP BREADCRUMB, TITLE & ONLINE/OFFLINE PILL               */}
      {/* ============================================================ */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
        <div>
          {/* Breadcrumb */}
          <div className="flex items-center gap-1.5 text-xs font-mono text-[#5A7A9C] mb-1">
            <Link to="/" className="hover:text-cyan-400 transition-colors">
              Home
            </Link>
            <span>&gt;</span>
            <span className="text-slate-300 font-semibold">Document Screening</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Document Screening
          </h1>
          <p className="text-xs font-medium text-[#7E9AB8] mt-0.5">
            Upload an identity document for multi-layer verification.
          </p>
        </div>

        {/* Status Pill Indicator */}
        <div className="flex items-center gap-1.5 p-1 rounded-full border border-cyan-950 bg-[#040C16] self-start sm:self-auto shadow-md">
          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold ${
              isLiveConnected
                ? "bg-emerald-950/80 text-[#00F5A0] border border-emerald-500/40 shadow-[0_0_10px_rgba(0,245,160,0.25)]"
                : "text-slate-500"
            }`}
          >
            <Wifi size={13} className={isLiveConnected ? "text-[#00F5A0] animate-pulse" : "text-slate-500"} />
            <span>ONLINE</span>
          </div>
          <div
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold ${
              !isLiveConnected
                ? "bg-rose-950/80 text-rose-400 border border-rose-500/40 shadow-[0_0_10px_rgba(239,68,68,0.25)]"
                : "text-slate-500"
            }`}
          >
            <WifiOff size={13} />
            <span>OFFLINE</span>
          </div>
        </div>
      </div>

      {/* ============================================================ */}
      {/* 2. DEMO SCENARIO SEQUENTIAL ANIMATED FLOW BAR               */}
      {/* ============================================================ */}
      <SequentialScenarioTracker
        currentResult={currentResult}
        isScreening={isScreening}
        activeAnimationStep={activeAnimationStep}
        selectedScenario={selectedScenario}
        onSelectScenario={handleSelectScenario}
      />

      {/* ============================================================ */}
      {/* 3. DOCUMENT TYPE SELECTOR ROW                                */}
      {/* ============================================================ */}
      <div className="flex items-center gap-2.5 flex-wrap">
        <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#7E9AB8] shrink-0">
          Document type:
        </span>
        <div className="flex items-center gap-2 flex-wrap">
          {docTypes.map((dt) => (
            <button
              key={dt.type}
              type="button"
              onClick={() => setSelectedDocType(dt.type)}
              className={`px-4 py-1.5 rounded-full text-xs font-mono font-bold transition-all ${
                selectedDocType === dt.type
                  ? "border border-cyan-400 bg-cyan-950/60 text-cyan-300 shadow-[0_0_12px_rgba(0,217,245,0.3)]"
                  : "border border-cyan-950/80 bg-[#040C16] text-slate-400 hover:border-cyan-800 hover:text-white"
              }`}
            >
              {dt.label}
            </button>
          ))}
        </div>
      </div>

      {/* ============================================================ */}
      {/* 4. MAIN 2-COLUMN VERIFICATION CONSOLE LAYOUT                 */}
      {/* ============================================================ */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
        {/* ============================================================ */}
        {/* LEFT COLUMN: DROPZONE & DOCUMENT PREVIEW CARD (~40%)         */}
        {/* ============================================================ */}
        <div className="lg:col-span-5 space-y-3.5">
          <div
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            className={`p-4 rounded-2xl bg-[#071322]/90 border transition-all duration-300 shadow-xl backdrop-blur-md relative overflow-hidden ${
              isDragOver
                ? "border-cyan-400 shadow-[0_0_25px_rgba(0,217,245,0.3)] bg-cyan-950/30"
                : "border-cyan-900/60 hover:border-cyan-700"
            }`}
          >
            {/* Top Prompt Area */}
            <div className="flex flex-col items-center justify-center text-center pb-3 border-b border-cyan-950/80">
              <div
                onClick={() => fileInputRef.current?.click()}
                className="cursor-pointer flex flex-col items-center group w-full py-2"
              >
                <div className="w-11 h-11 rounded-xl bg-cyan-950/80 border border-cyan-700/80 flex items-center justify-center text-cyan-400 mb-2 group-hover:scale-110 group-hover:border-cyan-400 transition-all shadow-[0_0_12px_rgba(0,217,245,0.2)]">
                  <UploadCloud size={22} className="text-cyan-400" />
                </div>
                <p className="text-xs font-medium text-slate-200">
                  Drag & drop a document, or{" "}
                  <span className="text-cyan-400 underline font-bold hover:text-cyan-300">
                    browse files
                  </span>
                </p>
                <p className="text-[10px] text-[#5A7A9C] mt-0.5">
                  JPG, PNG or PDF • single document per screening
                </p>
              </div>

              {/* Capture Image Button */}
              <button
                type="button"
                onClick={startCamera}
                className="mt-2 inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg border border-cyan-800/80 bg-[#040C16] hover:bg-cyan-950 text-cyan-300 text-xs font-mono font-bold hover:border-cyan-400 shadow-sm transition-all"
              >
                <Camera size={13} className="text-cyan-400" />
                <span>Capture image</span>
              </button>
            </div>

            {/* Document Image Display Box */}
            <div className="relative mt-3 rounded-xl overflow-hidden border border-cyan-900/80 bg-black aspect-[3/2] flex items-center justify-center shadow-inner">
              {docPreviewUrl ? (
                <div className="relative w-full h-full flex items-center justify-center">
                  <img
                    src={docPreviewUrl}
                    alt="Inspected Document"
                    className="w-full h-full object-contain select-none"
                  />
                  {/* Glowing Laser Scanline Effect during screening */}
                  {isScreening && (
                    <div className="absolute inset-0 pointer-events-none overflow-hidden">
                      <div className="w-full h-1 bg-gradient-to-r from-transparent via-[#00F5A0] to-transparent shadow-[0_0_15px_#00F5A0] animate-bounce" />
                      <div className="absolute inset-0 bg-cyan-500/10 backdrop-blur-[0.5px]" />
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-[#5A7A9C] text-xs font-mono gap-2 p-4">
                  <Scan size={28} className="text-cyan-800 animate-pulse" />
                  <span>No document uploaded</span>
                </div>
              )}
            </div>

            {/* Bottom Status Bar */}
            <div className="flex items-center justify-between gap-2 mt-3 pt-3 border-t border-cyan-950/80 text-xs">
              <div className="flex items-center gap-1.5 min-w-0">
                <CheckCircle2 size={14} className="text-[#00F5A0] shrink-0" />
                <span className="text-[11px] font-bold text-[#00F5A0] shrink-0">
                  Image uploaded successfully
                </span>
                <span className="text-[10px] text-[#5A7A9C] truncate">
                  {fileNameLabel} ({fileSizeLabel})
                </span>
              </div>

              <button
                type="button"
                onClick={handleReplace}
                className="px-2.5 py-1 rounded-lg bg-[#040C16] hover:bg-cyan-950 border border-cyan-900/80 hover:border-cyan-400 text-slate-200 hover:text-cyan-300 text-[11px] font-mono font-bold flex items-center gap-1 shrink-0 transition-all"
              >
                <RotateCcw size={11} />
                <span>Replace</span>
              </button>
            </div>
          </div>
        </div>

        {/* ============================================================ */}
        {/* RIGHT COLUMN: PIPELINE, OCR DETAILS, CARDS, FINAL RESULT (~60%) */}
        {/* ============================================================ */}
        <div className="lg:col-span-7 space-y-3.5">
          {/* Panel 1: Processing Pipeline */}
          <InteractiveProcessingPipeline
            currentResult={currentResult}
            isScreening={isScreening}
            pipelineStep={pipelineStep}
          />

          {/* Panel 2: OCR EXTRACTION DETAILS */}
          <OcrExtractionDetailsCard currentResult={currentResult} />

          {/* Panel 3: Forensic Analysis Result Cards (3-Column Subgrid) */}
          <ForensicAnalysisCards currentResult={currentResult} />

          {/* Panel 4: Final Screening Result Banner */}
          <FinalScreeningBanner currentResult={currentResult} />
        </div>
      </div>

      {/* ============================================================ */}
      {/* 5. WEBCAM CAPTURE MODAL                                      */}
      {/* ============================================================ */}
      {isCameraOpen && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-[#071322] border border-cyan-500/80 rounded-2xl max-w-lg w-full p-5 space-y-4 shadow-[0_0_35px_rgba(0,217,245,0.25)]">
            <div className="flex items-center justify-between border-b border-cyan-950 pb-3">
              <h3 className="text-xs font-mono font-bold uppercase text-white flex items-center gap-2">
                <Camera size={15} className="text-cyan-400" />
                <span>Border Camera Inspection Feed</span>
              </h3>
              <button
                onClick={stopCamera}
                className="p-1 rounded-lg hover:bg-cyan-950 text-slate-400 hover:text-white"
              >
                <X size={16} />
              </button>
            </div>

            <div className="relative rounded-xl overflow-hidden bg-black border border-cyan-900 aspect-video flex items-center justify-center">
              <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover" />
              <div className="absolute inset-8 border border-cyan-400/50 rounded-lg pointer-events-none" />
            </div>

            <div className="flex items-center justify-end gap-3 pt-1">
              <button
                onClick={stopCamera}
                className="px-4 py-2 rounded-xl text-xs font-mono text-slate-300 bg-[#040C16] border border-cyan-950 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={capturePhoto}
                className="px-4 py-2 rounded-xl text-xs font-mono font-bold text-slate-950 bg-[#00F5A0] hover:bg-emerald-300 flex items-center gap-1.5 shadow-[0_0_15px_rgba(0,245,160,0.3)] transition-all"
              >
                <Camera size={13} />
                <span>Capture &amp; Inspect</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
