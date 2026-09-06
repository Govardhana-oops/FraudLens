import React, { useState, useRef } from "react";
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
  Play,
  Square,
  Upload,
} from "lucide-react";
import { useApp } from "@/context/AppContext";
import { DocumentDropzone } from "@/components/DocumentDropzone";
import { StatusBadge } from "@/components/StatusBadge";
import { EmptyState } from "@/components/EmptyState";
import { api } from "@/services/api";
import type { FaceComparisonResult } from "@/types";

export function LiveVerificationPage() {
  const { records } = useApp();

  const [idFile, setIdFile] = useState<File | null>(null);
  const [liveFile, setLiveFile] = useState<File | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<FaceComparisonResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // WebCam state
  const [webcamActive, setWebcamActive] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const startWebcam = async () => {
    try {
      setWebcamActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      console.error("Camera access failed:", err);
      setErrorMessage("Could not access camera. Please upload an image file.");
      setWebcamActive(false);
    }
  };

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setWebcamActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const context = canvasRef.current.getContext("2d");
    if (!context) return;

    canvasRef.current.width = videoRef.current.videoWidth || 640;
    canvasRef.current.height = videoRef.current.videoHeight || 480;
    context.drawImage(videoRef.current, 0, 0);

    canvasRef.current.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], "webcam_capture.jpg", { type: "image/jpeg" });
        setLiveFile(file);
        stopWebcam();
      }
    }, "image/jpeg", 0.95);
  };

  const handleExecuteVerification = async () => {
    if (!idFile || !liveFile) return;

    setIsVerifying(true);
    setErrorMessage(null);

    try {
      // Execute inspection with both files
      const result = await api.inspectDocument(idFile, liveFile, "PASSPORT");
      if (result && result.face_comparison) {
        setComparisonResult(result.face_comparison);
      } else {
        setErrorMessage("Biometric comparison engine did not return a valid face verification result.");
      }
    } catch (err) {
      console.error("Biometric verification error:", err);
      setErrorMessage("Biometric engine error or backend unreachable. Check console logs.");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleReset = () => {
    setIdFile(null);
    setLiveFile(null);
    setComparisonResult(null);
    setErrorMessage(null);
    stopWebcam();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slateText-50 tracking-tight">1:1 Biometric Face Verification</h1>
            <span className="rounded bg-accent-sky/20 px-2 py-0.5 text-xs font-mono font-bold text-accent-sky border border-accent-sky/40">
              MODULE 4 BIOMETRICS
            </span>
          </div>
          <p className="text-sm font-semibold text-slateText-300">
            Facial landmark alignment, deep neural embedding similarity, and anti-spoofing liveness verification
          </p>
        </div>

        {comparisonResult && (
          <button
            onClick={handleReset}
            className="btn-secondary flex items-center gap-2 text-xs font-bold uppercase tracking-wider"
          >
            <RefreshCw size={14} />
            <span>Reset Verification</span>
          </button>
        )}
      </div>

      {/* Dual Image Input Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Source ID Document / Photo */}
        <div className="panel-3d p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slateText-200 flex items-center gap-2">
              <Shield size={16} className="text-brand-teal" />
              <span>Reference Credential (ID / Passport)</span>
            </h2>
            <span className="text-[11px] font-mono text-slateText-300">SOURCE A</span>
          </div>
          <p className="text-xs text-slateText-300 font-medium">
            Upload the ID document or photo page containing the bearer's official identity photo.
          </p>
          <DocumentDropzone
            onFileSelected={setIdFile}
            selectedFile={idFile}
            label="Drop reference document photo here"
          />
        </div>

        {/* Live Passenger Camera / Selfie Feed */}
        <div className="panel-3d p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slateText-200 flex items-center gap-2">
              <Camera size={16} className="text-brand-cyan" />
              <span>Live Traveler Capture (Webcam / Photo)</span>
            </h2>
            <span className="text-[11px] font-mono text-slateText-300">SOURCE B</span>
          </div>
          <p className="text-xs text-slateText-300 font-medium">
            Capture a live photo using the inspection terminal webcam or upload an incoming live camera snapshot.
          </p>

          {webcamActive ? (
            <div className="relative rounded-xl overflow-hidden border border-canvas-600 bg-canvas-950 aspect-video flex items-center justify-center">
              <video ref={videoRef} className="w-full h-full object-cover" />
              <canvas ref={canvasRef} className="hidden" />
              <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex items-center gap-3">
                <button
                  type="button"
                  onClick={capturePhoto}
                  className="btn-primary text-xs uppercase tracking-wider flex items-center gap-1.5 shadow-glow-teal"
                >
                  <Camera size={14} />
                  <span>Capture Photo</span>
                </button>
                <button
                  type="button"
                  onClick={stopWebcam}
                  className="btn-danger text-xs uppercase tracking-wider flex items-center gap-1.5"
                >
                  <Square size={14} />
                  <span>Cancel</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <DocumentDropzone
                onFileSelected={setLiveFile}
                selectedFile={liveFile}
                label="Drop live traveler face snapshot here"
              />
              <button
                type="button"
                onClick={startWebcam}
                className="btn-secondary w-full text-xs uppercase tracking-wider font-bold flex items-center justify-center gap-2"
              >
                <Camera size={14} />
                <span>Open Terminal Webcam</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Verification Trigger Button */}
      <div className="panel-3d p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slateText-100">Ready for 1:1 Biometric Comparison</h3>
          <p className="text-xs text-slateText-300 font-medium">
            Threshold: 75% similarity • Anti-spoofing liveness filter active
          </p>
        </div>

        <button
          type="button"
          disabled={!idFile || !liveFile || isVerifying}
          onClick={handleExecuteVerification}
          className="btn-primary px-8 py-3 text-xs uppercase tracking-wider font-black flex items-center gap-2 shadow-glow-teal disabled:opacity-50 disabled:pointer-events-none"
        >
          <ScanFace size={16} />
          <span>{isVerifying ? "Comparing Neural Embeddings..." : "Execute Biometric Match"}</span>
        </button>
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="rounded-xl border border-accent-rose/50 bg-accent-rose/10 p-4 text-xs font-bold text-accent-rose flex items-center gap-2">
          <AlertTriangle size={16} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Biometric Results Panel */}
      {comparisonResult && (
        <div className="panel-3d p-6 border-accent-sky/40 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-canvas-600 pb-4">
            <div className="flex items-center gap-3">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-xl border ${
                  comparisonResult.matched
                    ? "bg-accent-emerald/20 border-accent-emerald text-accent-emerald shadow-glow-emerald"
                    : "bg-accent-rose/20 border-accent-rose text-accent-rose shadow-glow-rose"
                }`}
              >
                {comparisonResult.matched ? <CheckCircle2 size={24} /> : <XCircle size={24} />}
              </div>
              <div>
                <h3 className="text-lg font-black text-slateText-50">
                  {comparisonResult.matched ? "BIOMETRIC MATCH CONFIRMED" : "BIOMETRIC MISMATCH DETECTED"}
                </h3>
                <p className="text-xs font-medium text-slateText-300">
                  Method: {comparisonResult.method || "Deep Neural Face Verification"}
                </p>
              </div>
            </div>

            <span
              className={`rounded-lg px-3 py-1.5 text-xs font-mono font-bold border ${
                comparisonResult.matched
                  ? "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/50"
                  : "bg-accent-rose/20 text-accent-rose border-accent-rose/50"
              }`}
            >
              {comparisonResult.matched ? "PASSED (MATCH)" : "FAILED (MISMATCH)"}
            </span>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-canvas-850 border border-canvas-600">
              <span className="text-xs font-bold uppercase tracking-wider text-slateText-400">Similarity Score</span>
              <div className="mt-2 text-2xl font-mono font-bold text-accent-sky">
                {Math.round(comparisonResult.similarity_score * 100)}%
              </div>
              <p className="text-[11px] font-medium text-slateText-300 mt-1">
                Cosine distance over 512-d embeddings
              </p>
            </div>

            <div className="p-4 rounded-xl bg-canvas-850 border border-canvas-600">
              <span className="text-xs font-bold uppercase tracking-wider text-slateText-400">Liveness Confidence</span>
              <div
                className={`mt-2 text-2xl font-mono font-bold ${
                  comparisonResult.liveness_detected ? "text-accent-emerald" : "text-accent-rose"
                }`}
              >
                {Math.round(comparisonResult.liveness_score * 100)}%
              </div>
              <p className="text-[11px] font-medium text-slateText-300 mt-1">
                {comparisonResult.liveness_detected ? "Genuine Human Face" : "Potential Presentation Attack"}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-canvas-850 border border-canvas-600">
              <span className="text-xs font-bold uppercase tracking-wider text-slateText-400">Match Threshold</span>
              <div className="mt-2 text-2xl font-mono font-bold text-slateText-100">
                {Math.round(comparisonResult.threshold * 100)}%
              </div>
              <p className="text-[11px] font-medium text-slateText-300 mt-1">
                ICAO 9303 / FAR &lt; 0.001 Standard
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
