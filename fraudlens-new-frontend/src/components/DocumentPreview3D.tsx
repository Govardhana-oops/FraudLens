import React, { useState } from "react";
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  Maximize2,
  Minimize2,
  RefreshCw,
  FileText,
  FileQuestion,
  Shield,
  EyeOff,
} from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface DocumentPreview3DProps {
  dossier: UnifiedScreeningDossier;
  previewUrl?: string | null;
}

export function DocumentPreview3D({ dossier, previewUrl }: DocumentPreview3DProps) {
  const [zoom, setZoom] = useState<number>(1);
  const [rotation, setRotation] = useState<number>(0);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.25, 3));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.5));
  const handleRotate = () => setRotation((r) => (r + 90) % 360);
  const handleReset = () => {
    setZoom(1);
    setRotation(0);
  };

  const docNumber = dossier.document_number || "—";
  const docType = dossier.document_type || "PASSPORT";

  // Status-dependent perimeter glow
  const isPass = dossier.status === "VALID" || dossier.status === "PASS";
  const isFail =
    dossier.status === "INVALID" ||
    dossier.status === "TAMPERED" ||
    dossier.status === "FRAUD_DETECTED";

  const glowColor = isPass
    ? "rgba(16, 185, 129, 0.25)"
    : isFail
    ? "rgba(239, 68, 68, 0.25)"
    : "rgba(6, 182, 212, 0.25)";

  const renderDocumentContent = (inModal = false) => {
    if (previewUrl) {
      return (
        <div className="relative overflow-hidden rounded-xl border border-canvas-600 bg-canvas-950 flex items-center justify-center p-2">
          <img
            src={previewUrl}
            alt="Screened Identity Document"
            style={{
              transform: `scale(${zoom}) rotate(${rotation}deg)`,
              transition: "transform 0.25s ease-out",
            }}
            className={`max-h-[340px] ${inModal ? "max-h-[80vh]" : ""} w-auto object-contain select-none`}
          />
          {/* Subtle scanning laser line */}
          <div className="pointer-events-none absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-accent-sky/70 to-transparent shadow-[0_0_12px_rgba(6,182,212,0.8)] animate-pulse top-1/3" />
        </div>
      );
    }

    // Strictly compliant: Document Preview Unavailable (No synthetic/fake documents)
    return (
      <div
        className={`rounded-xl border border-canvas-700 bg-canvas-900/90 p-8 flex flex-col items-center justify-center text-center space-y-3 ${
          inModal ? "w-[500px]" : "w-full"
        }`}
      >
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-canvas-800 border border-canvas-700 text-slateText-400">
          <FileQuestion size={24} />
        </div>
        <div>
          <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slateText-200">
            DOCUMENT PREVIEW UNAVAILABLE
          </h4>
          <p className="text-[11px] font-mono text-slateText-400 mt-1 max-w-xs leading-relaxed">
            The original uploaded document preview could not be rendered.
          </p>
        </div>
        <div className="pt-2 border-t border-canvas-800 text-[10px] font-mono text-slateText-400">
          REF: <span className="text-slateText-300">{dossier.screening_id}</span> • TYPE:{" "}
          <span className="text-slateText-300">{docType}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="panel-3d p-5 rounded-2xl border border-canvas-600 bg-canvas-850 flex flex-col justify-between relative overflow-hidden group">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-canvas-600/80 mb-3">
        <div className="flex items-center gap-2">
          <FileText size={16} className="text-accent-sky" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slateText-100">
            Document Preview
          </h3>
        </div>
        <span
          className={`text-[10px] font-mono px-2 py-0.5 rounded border font-bold ${
            previewUrl
              ? "bg-accent-emerald/10 text-accent-emerald border-accent-emerald/30"
              : "bg-canvas-900 text-slateText-400 border-canvas-700"
          }`}
        >
          {previewUrl ? "ACTIVE UPLOAD" : "UNAVAILABLE"}
        </span>
      </div>

      {/* 3D Holographic Stage */}
      <div className="relative my-auto flex flex-col items-center justify-center min-h-[280px] py-4">
        {/* Circular Holographic 3D Base */}
        <div
          style={{
            boxShadow: `0 0 45px ${glowColor}`,
          }}
          className="absolute bottom-2 h-14 w-4/5 rounded-full border border-accent-sky/30 bg-gradient-to-r from-accent-sky/5 via-accent-teal/15 to-accent-sky/5 transform -rotate-x-60 pointer-events-none"
        />

        {/* Floating 3D Document Container */}
        <div className="relative z-10 w-full max-w-[320px] transition-transform duration-300 hover:translate-y-[-4px]">
          {renderDocumentContent(false)}
        </div>
      </div>

      {/* Interactive Tool Toolbar */}
      <div className="pt-3 border-t border-canvas-600/80 flex items-center justify-between text-slateText-300">
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleZoomIn}
            disabled={!previewUrl}
            title="Zoom In"
            className="p-1.5 rounded-lg bg-canvas-900 hover:bg-canvas-700 border border-canvas-700 hover:text-accent-sky disabled:opacity-40 disabled:pointer-events-none transition-colors text-xs"
          >
            <ZoomIn size={14} />
          </button>
          <button
            onClick={handleZoomOut}
            disabled={!previewUrl}
            title="Zoom Out"
            className="p-1.5 rounded-lg bg-canvas-900 hover:bg-canvas-700 border border-canvas-700 hover:text-accent-sky disabled:opacity-40 disabled:pointer-events-none transition-colors text-xs"
          >
            <ZoomOut size={14} />
          </button>
          <button
            onClick={handleRotate}
            disabled={!previewUrl}
            title="Rotate 90°"
            className="p-1.5 rounded-lg bg-canvas-900 hover:bg-canvas-700 border border-canvas-700 hover:text-accent-sky disabled:opacity-40 disabled:pointer-events-none transition-colors text-xs"
          >
            <RotateCw size={14} />
          </button>
          <button
            onClick={handleReset}
            disabled={!previewUrl}
            title="Reset Transform"
            className="p-1.5 rounded-lg bg-canvas-900 hover:bg-canvas-700 border border-canvas-700 hover:text-accent-sky disabled:opacity-40 disabled:pointer-events-none transition-colors text-xs"
          >
            <RefreshCw size={14} />
          </button>
        </div>

        <button
          onClick={() => previewUrl && setIsFullscreen(true)}
          disabled={!previewUrl}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-canvas-900 hover:bg-accent-sky/20 border border-canvas-700 hover:border-accent-sky/40 text-slateText-200 hover:text-accent-sky disabled:opacity-40 disabled:pointer-events-none text-[11px] font-mono font-bold transition-all"
        >
          <Maximize2 size={13} />
          <span>EXPAND</span>
        </button>
      </div>

      {/* Fullscreen Inspection Modal */}
      {isFullscreen && previewUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-6">
          <div className="relative w-full max-w-4xl rounded-2xl border border-accent-sky/40 bg-canvas-900 p-6 shadow-[0_0_60px_rgba(6,182,212,0.3)]">
            <div className="flex items-center justify-between pb-4 border-b border-canvas-700 mb-6">
              <div className="flex items-center gap-3">
                <FileText size={20} className="text-accent-sky" />
                <div>
                  <h3 className="text-base font-mono font-black text-slateText-50">
                    High-Resolution Specimen Inspection
                  </h3>
                  <p className="text-xs font-mono text-slateText-400">
                    Ref: {dossier.screening_id} • Type: {docType}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleZoomIn}
                  className="p-2 rounded-lg bg-canvas-800 hover:bg-canvas-700 border border-canvas-600 text-slateText-200"
                >
                  <ZoomIn size={16} />
                </button>
                <button
                  onClick={handleZoomOut}
                  className="p-2 rounded-lg bg-canvas-800 hover:bg-canvas-700 border border-canvas-600 text-slateText-200"
                >
                  <ZoomOut size={16} />
                </button>
                <button
                  onClick={handleRotate}
                  className="p-2 rounded-lg bg-canvas-800 hover:bg-canvas-700 border border-canvas-600 text-slateText-200"
                >
                  <RotateCw size={16} />
                </button>
                <button
                  onClick={handleReset}
                  className="p-2 rounded-lg bg-canvas-800 hover:bg-canvas-700 border border-canvas-600 text-slateText-200"
                >
                  <RefreshCw size={16} />
                </button>
                <button
                  onClick={() => setIsFullscreen(false)}
                  className="p-2 rounded-lg bg-accent-rose/20 hover:bg-accent-rose/30 border border-accent-rose/40 text-accent-rose ml-3"
                >
                  <Minimize2 size={16} />
                </button>
              </div>
            </div>

            <div className="flex items-center justify-center p-6 bg-canvas-950 rounded-xl border border-canvas-800 min-h-[420px] overflow-hidden">
              {renderDocumentContent(true)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
