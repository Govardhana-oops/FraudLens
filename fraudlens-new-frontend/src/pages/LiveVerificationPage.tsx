import React, { useState, useRef, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  ScanFace,
  Camera,
  Shield,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
  FolderLock,
  Square,
  Sparkles,
  ArrowRight,
  ExternalLink,
  Lock,
  UserCheck,
  Video,
  VideoOff,
  Crosshair,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { CentralBiometricHud } from "@/components/CentralBiometricHud";
import { BiometricProcessingStages } from "@/components/BiometricProcessingStages";
import { FaceAnalysisResultsGrid } from "@/components/FaceAnalysisResultsGrid";
import { BiometricResultBanner } from "@/components/BiometricResultBanner";
import type { FaceComparisonResult } from "@/types";

export function LiveVerificationPage() {
  const {
    currentResult,
    referenceDocumentFile,
    referenceDocPreviewUrl,
    referenceFaceUrl,
    referenceFaceStatus,
    referenceFaceConfidence,
    referenceDocNumber,
    referenceHolderName,
    referenceDocType,
    biometricResult,
    isBiometricVerifying,
    setReferenceDocument,
    executeBiometricVerification,
    resetBiometricResult,
  } = useApp();

  // Webcam stream state
  const [cameraActive, setCameraActive] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [capturedLiveFaceUrl, setCapturedLiveFaceUrl] = useState<string | null>(null);
  const [capturedLiveFile, setCapturedLiveFile] = useState<File | null>(null);

  // Pipeline animation stage (0 to 6)
  const [activeStage, setActiveStage] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [localBiometricResult, setLocalBiometricResult] = useState<FaceComparisonResult | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Start Camera
  const startCamera = useCallback(async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user",
        },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setCameraActive(true);
    } catch (err: any) {
      console.warn("Webcam access failed:", err);
      let errorMsg = "Camera access denied or device unavailable. Please verify browser permissions.";
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        errorMsg = "CAMERA ACCESS DENIED: Browser camera permission was not granted.";
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        errorMsg = "CAMERA NOT FOUND: No physical video capture device was detected.";
      }
      setCameraError(errorMsg);
      setCameraActive(false);
    }
  }, []);

  // Stop Camera
  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
  }, []);

  // Auto-start camera when page opens if not captured
  useEffect(() => {
    if (!capturedLiveFaceUrl && !cameraActive) {
      startCamera();
    }
    return () => {
      stopCamera();
    };
  }, [capturedLiveFaceUrl, startCamera, stopCamera]);

  // Synchronize local biometric result with context
  useEffect(() => {
    if (biometricResult) {
      setLocalBiometricResult(biometricResult);
    }
  }, [biometricResult]);

  // Trigger Automatic 6-Stage Biometric Processing Pipeline upon Photo Capture
  const handleCapturePhoto = async () => {
    if (!videoRef.current) return;

    const width = videoRef.current.videoWidth || 640;
    const height = videoRef.current.videoHeight || 480;

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(videoRef.current, 0, 0, width, height);

    const liveDataUrl = canvas.toDataURL("image/jpeg", 0.95);
    setCapturedLiveFaceUrl(liveDataUrl);

    // Stop webcam after capture
    stopCamera();

    // Create File from Canvas Blob
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const file = new File([blob], "live_traveler_capture.jpg", { type: "image/jpeg" });
      setCapturedLiveFile(file);

      // Start Automatic Sequential Verification Flow
      setIsProcessing(true);
      setActiveStage(1); // Stage 1: Capture

      // Sequential Stage Step Timer (1 -> 2 -> 3 -> 4 -> 5 -> 6)
      let stageCounter = 1;
      const stageInterval = setInterval(() => {
        stageCounter += 1;
        if (stageCounter <= 5) {
          setActiveStage(stageCounter);
        }
      }, 350);

      try {
        const result = await executeBiometricVerification(file);
        setLocalBiometricResult(result);
        setActiveStage(6); // Final result reached
      } catch (err) {
        console.error("Biometric verification execution failed:", err);
      } finally {
        clearInterval(stageInterval);
        setIsProcessing(false);
      }
    }, "image/jpeg", 0.95);
  };

  // Retake live photo
  const handleRetake = () => {
    setCapturedLiveFaceUrl(null);
    setCapturedLiveFile(null);
    setLocalBiometricResult(null);
    resetBiometricResult();
    setActiveStage(0);
    startCamera();
  };

  // Reset entire verification session
  const handleResetAll = () => {
    setCapturedLiveFaceUrl(null);
    setCapturedLiveFile(null);
    setLocalBiometricResult(null);
    resetBiometricResult();
    setActiveStage(0);
    startCamera();
  };

  const docInputRef = useRef<HTMLInputElement | null>(null);

  const handleDocUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setReferenceDocument(file, referenceDocType);
    }
  };

  // Derive resolved metadata for Source A
  const resolvedDocNumber =
    referenceDocNumber ||
    currentResult?.document_number ||
    (currentResult?.extracted_fields?.find(
      (f) => f.field_name.toLowerCase().includes("number") || f.field_name.toLowerCase().includes("passport")
    )?.extracted_value ?? "—");

  const resolvedHolderName =
    referenceHolderName ||
    (currentResult?.extracted_fields?.find(
      (f) =>
        f.field_name.toLowerCase().includes("name") ||
        f.field_name.toLowerCase().includes("surname") ||
        f.field_name.toLowerCase().includes("given")
    )?.extracted_value ?? "—");

  const hasReferenceFace = Boolean(referenceFaceUrl && referenceFaceStatus === "EXTRACTED");
  const hasLiveCapture = Boolean(capturedLiveFaceUrl);

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-mono font-black text-slateText-50 tracking-tight flex items-center gap-2.5">
              <ScanFace size={26} className="text-accent-teal" />
              <span>1:1 Biometric Verification Console</span>
            </h1>
            <span className="rounded bg-accent-sky/20 px-2 py-0.5 text-xs font-mono font-bold text-accent-sky border border-accent-sky/40">
              MODULE 4
            </span>
          </div>
          <p className="text-xs font-semibold text-slateText-300 mt-1">
            Automated facial feature extraction, 128-d spatial gradient & texture embeddings comparison, and ISO/IEC 19794-5 compliance verification
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleResetAll}
            className="btn-secondary flex items-center gap-2 text-xs font-mono font-bold uppercase tracking-wider"
          >
            <RefreshCw size={14} />
            <span>Reset Console</span>
          </button>
        </div>
      </div>

      {/* 6-Stage Sequential Pipeline Animation Tracker */}
      <BiometricProcessingStages
        currentStage={activeStage}
        isProcessing={isProcessing}
        isComplete={activeStage === 6}
        hasResult={Boolean(localBiometricResult)}
      />

      {/* Main 3-Column 1:1 Biometric Comparison Console */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* ========================================================================= */}
        {/* SOURCE A: AUTOMATIC REFERENCE FACE FROM SCREENING (4 Columns)             */}
        {/* ========================================================================= */}
        <div className="lg:col-span-4 panel-3d p-5 flex flex-col justify-between space-y-4 bg-canvas-850 border-canvas-600/90 shadow-cardElevated">
          <div>
            <div className="flex items-center justify-between border-b border-canvas-700 pb-3">
              <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slateText-200 flex items-center gap-2">
                <Shield size={16} className="text-accent-teal" />
                <span>Reference Face From Document</span>
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-canvas-900 border border-canvas-600 text-accent-teal">
                SOURCE A
              </span>
            </div>
            <p className="text-[11px] text-slateText-300 font-mono mt-2 leading-relaxed">
              Extracted from screening session or uploaded directly as reference.
            </p>
          </div>

          {/* Reference Face Image / Status Container */}
          <div className="relative rounded-2xl overflow-hidden border border-canvas-600 bg-canvas-950/90 aspect-[4/5] flex items-center justify-center shadow-inner group">
            {hasReferenceFace ? (
              <>
                <img
                  src={referenceFaceUrl!}
                  alt="Reference Document Face Crop"
                  className="w-full h-full object-cover"
                />

                {/* Cyber HUD Overlay on Face */}
                <div className="absolute inset-0 border-2 border-accent-teal/30 pointer-events-none" />
                {/* Corner Brackets */}
                <div className="absolute top-2 left-2 w-4 h-4 border-t-2 border-l-2 border-accent-teal" />
                <div className="absolute top-2 right-2 w-4 h-4 border-t-2 border-r-2 border-accent-teal" />
                <div className="absolute bottom-2 left-2 w-4 h-4 border-b-2 border-l-2 border-accent-teal" />
                <div className="absolute bottom-2 right-2 w-4 h-4 border-b-2 border-r-2 border-accent-teal" />

                {/* Subtle Facial Scan Laser */}
                <div className="absolute inset-x-0 h-[2px] bg-accent-teal/60 shadow-[0_0_8px_#2DD4BF] animate-pulse top-1/3" />

                {/* Source Tag Badge */}
                <div className="absolute top-3 left-3 px-2 py-0.5 rounded bg-canvas-950/90 border border-accent-teal/60 text-[10px] font-mono font-bold text-accent-teal flex items-center gap-1.5 shadow-md">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent-teal animate-ping" />
                  <span>DOCUMENT REFERENCE</span>
                </div>

                {/* Confidence Tag */}
                <div className="absolute bottom-3 right-3 px-2 py-0.5 rounded bg-canvas-950/90 border border-canvas-600 text-[10px] font-mono font-bold text-slateText-200">
                  {referenceFaceConfidence
                    ? `${(referenceFaceConfidence * 100).toFixed(1)}% QUALITY`
                    : "EXTRACTED"}
                </div>
              </>
            ) : referenceFaceStatus === "DETECTING" ? (
              <div className="flex flex-col items-center space-y-3 p-6 text-center">
                <RefreshCw size={28} className="text-accent-teal animate-spin" />
                <span className="text-xs font-mono font-bold text-accent-teal uppercase tracking-wider">
                  Extracting Reference Face...
                </span>
                <p className="text-[11px] text-slateText-400">
                  Scanning passport portrait area from uploaded document
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center space-y-3 p-6 text-center">
                <div className="p-3 rounded-full bg-accent-teal/10 border border-accent-teal/30 text-accent-teal">
                  <ScanFace size={28} />
                </div>
                <div className="text-xs font-mono font-bold text-accent-teal uppercase tracking-wider">
                  UPLOAD REFERENCE DOCUMENT
                </div>
                <p className="text-[11px] text-slateText-300 max-w-[220px] leading-relaxed">
                  Upload an identity document or portrait photo to compare against the live traveler camera.
                </p>
                <input
                  ref={docInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleDocUpload}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => docInputRef.current?.click()}
                  className="btn-primary text-xs font-mono font-bold uppercase tracking-wider mt-1 flex items-center gap-1.5 shadow-glowTeal"
                >
                  <FolderLock size={12} />
                  <span>Choose File</span>
                </button>
                <Link
                  to="/screening"
                  className="text-[10px] text-accent-sky font-mono hover:underline flex items-center gap-1 mt-1"
                >
                  <ExternalLink size={10} />
                  <span>Or select in Document Screening</span>
                </Link>
              </div>
            )}
          </div>

          {/* Reference Document Metadata */}
          <div className="rounded-xl p-3 bg-canvas-900 border border-canvas-700/80 space-y-2 text-xs font-mono">
            <div className="flex justify-between items-center text-slateText-400">
              <span>DOCUMENT NUMBER:</span>
              <strong className="text-slateText-100">{resolvedDocNumber}</strong>
            </div>
            <div className="flex justify-between items-center text-slateText-400">
              <span>BEARER NAME:</span>
              <strong className="text-slateText-100 truncate max-w-[160px]">{resolvedHolderName}</strong>
            </div>
            <div className="flex justify-between items-center text-slateText-400">
              <span>CREDENTIAL TYPE:</span>
              <span className="px-1.5 py-0.2 rounded bg-canvas-800 text-[10px] font-bold text-accent-sky border border-canvas-600">
                {referenceDocType}
              </span>
            </div>
            <div className="flex justify-between items-center text-slateText-400">
              <span>DETECTION STATUS:</span>
              <span
                className={`font-bold ${
                  hasReferenceFace ? "text-accent-emerald" : "text-accent-rose"
                }`}
              >
                {hasReferenceFace ? "DETECTED" : "UNAVAILABLE"}
              </span>
            </div>
            {hasReferenceFace && (
              <div className="flex items-center justify-between pt-1 border-t border-canvas-800">
                <input
                  ref={docInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleDocUpload}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => docInputRef.current?.click()}
                  className="text-[11px] font-mono text-accent-teal hover:underline flex items-center gap-1"
                >
                  <RefreshCw size={11} />
                  <span>Change Reference Document</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* ========================================================================= */}
        {/* CENTRAL BIOMETRIC HUD RADAR (4 Columns)                                   */}
        {/* ========================================================================= */}
        <div className="lg:col-span-4 flex flex-col justify-center">
          <CentralBiometricHud
            isProcessing={isProcessing}
            activeStage={activeStage}
            result={localBiometricResult}
            hasReferenceFace={hasReferenceFace}
            hasLiveCapture={hasLiveCapture}
          />
        </div>

        {/* ========================================================================= */}
        {/* SOURCE B: LIVE TRAVELER CAMERA CAPTURE (4 Columns)                        */}
        {/* ========================================================================= */}
        <div className="lg:col-span-4 panel-3d p-5 flex flex-col justify-between space-y-4 bg-canvas-850 border-canvas-600/90 shadow-cardElevated">
          <div>
            <div className="flex items-center justify-between border-b border-canvas-700 pb-3">
              <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slateText-200 flex items-center gap-2">
                <Camera size={16} className="text-accent-sky" />
                <span>Live Traveler Capture</span>
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-canvas-900 border border-canvas-600 text-accent-sky">
                SOURCE B
              </span>
            </div>
            <p className="text-[11px] text-slateText-300 font-mono mt-2 leading-relaxed">
              Real-time terminal webcam feed with anti-spoof liveness guidance.
            </p>
          </div>

          {/* Camera Viewport / Captured Freeze View */}
          <div className="relative rounded-2xl overflow-hidden border border-canvas-600 bg-canvas-950 aspect-[4/5] flex items-center justify-center shadow-inner">
            {capturedLiveFaceUrl ? (
              // Frozen Post-Capture Live Image
              <>
                <img
                  src={capturedLiveFaceUrl}
                  alt="Captured Live Traveler Face"
                  className="w-full h-full object-cover"
                />

                {/* Cyber Corner Brackets */}
                <div className="absolute top-2 left-2 w-4 h-4 border-t-2 border-l-2 border-accent-sky" />
                <div className="absolute top-2 right-2 w-4 h-4 border-t-2 border-r-2 border-accent-sky" />
                <div className="absolute bottom-2 left-2 w-4 h-4 border-b-2 border-l-2 border-accent-sky" />
                <div className="absolute bottom-2 right-2 w-4 h-4 border-b-2 border-r-2 border-accent-sky" />

                {/* Status Badge */}
                <div className="absolute top-3 left-3 px-2 py-0.5 rounded bg-canvas-950/90 border border-accent-sky/60 text-[10px] font-mono font-bold text-accent-sky flex items-center gap-1.5">
                  <CheckCircle2 size={12} className="text-accent-sky" />
                  <span>CAPTURED PROBE</span>
                </div>
              </>
            ) : cameraActive ? (
              // Live Video Stream
              <>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover -scale-x-100"
                />

                {/* 3D Cyber Face-Positioning Oval Guide */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="w-48 h-60 rounded-[50%] border-2 border-dashed border-accent-sky/50 shadow-[0_0_20px_rgba(59,130,246,0.2)] flex items-center justify-center">
                    <Crosshair size={24} className="text-accent-sky/40 animate-spin" style={{ animationDuration: "12s" }} />
                  </div>
                </div>

                {/* Scanning Laser Line */}
                <div className="absolute inset-x-0 h-[2px] bg-accent-sky/70 shadow-[0_0_10px_#3B82F6] animate-pulse top-1/2 pointer-events-none" />

                {/* Corner Brackets */}
                <div className="absolute top-2 left-2 w-5 h-5 border-t-2 border-l-2 border-accent-sky" />
                <div className="absolute top-2 right-2 w-5 h-5 border-t-2 border-r-2 border-accent-sky" />
                <div className="absolute bottom-2 left-2 w-5 h-5 border-b-2 border-l-2 border-accent-sky" />
                <div className="absolute bottom-2 right-2 w-5 h-5 border-b-2 border-r-2 border-accent-sky" />

                {/* Camera Ready Pulsing Indicator */}
                <div className="absolute top-3 left-3 px-2 py-0.5 rounded bg-canvas-950/90 border border-accent-emerald/60 text-[10px] font-mono font-bold text-accent-emerald flex items-center gap-1.5 shadow-md">
                  <span className="w-2 h-2 rounded-full bg-accent-emerald animate-ping" />
                  <span>CAMERA READY</span>
                </div>

                <div className="absolute bottom-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-canvas-950/80 border border-canvas-600 text-[10px] font-mono text-slateText-300">
                  Align face within guide
                </div>
              </>
            ) : cameraError ? (
              // Camera Error / Denied State
              <div className="flex flex-col items-center space-y-3 p-6 text-center">
                <div className="p-3 rounded-full bg-accent-rose/10 border border-accent-rose/30 text-accent-rose">
                  <VideoOff size={28} />
                </div>
                <div className="text-xs font-mono font-bold text-accent-rose uppercase tracking-wider">
                  CAMERA UNAVAILABLE
                </div>
                <p className="text-[11px] text-slateText-400 max-w-[220px] leading-relaxed">
                  {cameraError}
                </p>
                <button
                  type="button"
                  onClick={startCamera}
                  className="btn-secondary text-xs font-mono font-bold uppercase tracking-wider mt-2 flex items-center gap-1.5"
                >
                  <RefreshCw size={12} />
                  <span>Retry Camera</span>
                </button>
              </div>
            ) : (
              // Initial Camera Activation Trigger
              <div className="flex flex-col items-center space-y-3 p-6 text-center">
                <Video size={32} className="text-slateText-400 opacity-60" />
                <span className="text-xs font-mono font-bold text-slateText-300 uppercase tracking-wider">
                  Camera Standby
                </span>
                <button
                  type="button"
                  onClick={startCamera}
                  className="btn-primary text-xs font-mono font-bold uppercase tracking-wider shadow-glowTeal flex items-center gap-1.5"
                >
                  <Video size={14} />
                  <span>Activate Webcam</span>
                </button>
              </div>
            )}
          </div>

          {/* Camera Action Buttons (3D Capture / Retake) */}
          <div className="space-y-2">
            {capturedLiveFaceUrl ? (
              <button
                type="button"
                onClick={handleRetake}
                disabled={isProcessing}
                className="btn-secondary w-full py-2.5 text-xs font-mono font-bold uppercase tracking-wider flex items-center justify-center gap-2"
              >
                <RefreshCw size={14} />
                <span>Retake Live Photo</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={handleCapturePhoto}
                disabled={!cameraActive || isProcessing}
                className="btn-primary w-full py-3 text-xs font-mono font-black uppercase tracking-wider flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(45,212,191,0.35)] disabled:opacity-50 disabled:pointer-events-none"
              >
                <Camera size={16} />
                <span>
                  {isProcessing
                    ? "Comparing Feature Embeddings..."
                    : "Capture Photo & Verify"}
                </span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Face Analysis Results 3D Cards */}
      <FaceAnalysisResultsGrid
        result={localBiometricResult}
        hasDocumentFace={hasReferenceFace}
        hasLiveCapture={hasLiveCapture}
      />

      {/* Bottom Result Banner */}
      <BiometricResultBanner
        result={localBiometricResult}
        docNumber={resolvedDocNumber}
        holderName={resolvedHolderName}
        onReset={handleResetAll}
      />
    </div>
  );
}
