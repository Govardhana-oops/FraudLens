import React, { useState } from "react";
import {
  ZoomIn,
  ZoomOut,
  RotateCw,
  Maximize2,
  Minimize2,
  RefreshCw,
  FileText,
  ShieldCheck,
  QrCode,
  User,
  Fingerprint,
  Eye,
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

  const nameField = dossier.extracted_fields?.find(
    (f) =>
      f.field_name.toLowerCase().includes("name") ||
      f.field_name.toLowerCase().includes("surname") ||
      f.field_name.toLowerCase().includes("given")
  );
  const holderName = nameField?.extracted_value || "UNKNOWN";
  const docNumber = dossier.document_number || "—";
  const docType = dossier.document_type || "PASSPORT";

  // Check if tampering or security check failed
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
        <div className="relative overflow-hidden rounded-xl border border-canvas-600 bg-canvas-950 flex items-center justify-center">
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

    // High-tech Forensic Blueprint Document Visualization
    return (
      <div
        style={{
          transform: `scale(${zoom}) rotate(${rotation}deg)`,
          transition: "transform 0.25s ease-out",
        }}
        className={`relative rounded-xl border border-canvas-600 bg-gradient-to-br from-canvas-850 via-canvas-900 to-canvas-950 p-5 shadow-2xl ${
          inModal ? "w-[500px]" : "w-full"
        }`}
      >
        {/* Holographic header */}
        <div className="flex items-center justify-between border-b border-canvas-700 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-accent-sky/20 border border-accent-sky/40 text-accent-sky">
              <ShieldCheck size={16} />
            </div>
            <div>
              <span className="text-[10px] font-mono font-black text-accent-sky uppercase tracking-widest block">
                OFFICIAL SPECIMEN
              </span>
              <span className="text-xs font-mono font-bold text-slateText-100">
                {docType} • FORENSIC RECORD
              </span>
            </div>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-canvas-800 text-slateText-300 border border-canvas-600">
            {docNumber}
          </span>
        </div>

        {/* Specimen Body */}
        <div className="grid grid-cols-3 gap-3 items-center">
          {/* Photo frame */}
          <div className="col-span-1 rounded-lg border-2 border-dashed border-canvas-600 bg-canvas-950/80 p-3 flex flex-col items-center justify-center min-h-[120px] text-center">
            <div className="h-12 w-12 rounded-full bg-accent-sky/10 border border-accent-sky/30 flex items-center justify-center text-accent-sky mb-2">
              <User size={24} />
            </div>
            <span className="text-[9px] font-mono text-slateText-400">BIOMETRIC PHOTO</span>
            <span className="text-[8px] font-mono text-accent-emerald mt-0.5">ICAO 9303</span>
          </div>

          {/* Primary Details */}
          <div className="col-span-2 space-y-2 text-left pl-1">
            <div>
              <span className="text-[9px] font-mono uppercase text-slateText-400 block">Bearer Name</span>
              <span className="text-xs font-mono font-bold text-slateText-50 truncate block">
                {holderName}
              </span>
            </div>

            <div>
              <span className="text-[9px] font-mono uppercase text-slateText-400 block">Doc Number</span>
              <span className="text-xs font-mono font-bold text-accent-sky tracking-wider block">
                {docNumber}
              </span>
            </div>

            <div className="flex items-center gap-2 pt-1">
              <div className="flex items-center gap-1 text-[9px] font-mono text-slateText-400">
                <Fingerprint size={12} className="text-accent-teal" />
                <span>CHIP VERIFIED</span>
              </div>
              <div className="flex items-center gap-1 text-[9px] font-mono text-slateText-400">
                <QrCode size={12} className="text-accent-sky" />
                <span>MRZ PASS</span>
              </div>
            </div>
          </div>
        </div>

        {/* Specimen MRZ Footer */}
        <div className="mt-4 pt-3 border-t border-canvas-700/80 bg-canvas-950/60 p-2 rounded border border-canvas-700 font-mono text-[9px] text-slateText-300 leading-tight tracking-widest break-all">
          <div className="text-accent-teal">{dossier.extracted_fields?.find(f => f.field_name.toLowerCase().includes("mrz") && f.field_name.includes("1"))?.extracted_value || `P<SPECIMEN<<${holderName.replace(/\s+/g, "<<")}`}</div>
          <div className="text-accent-sky">{dossier.extracted_fields?.find(f => f.field_name.toLowerCase().includes("mrz") && f.field_name.includes("2"))?.extracted_value || `${docNumber}<<<<<<<<<<<<<<<<<<<<<<01`}</div>
        </div>

        {/* Scanning laser line overlay */}
        <div className="pointer-events-none absolute inset-x-0 h-0.5 bg-gradient-to-r from-transparent via-accent-sky to-transparent shadow-[0_0_8px_rgba(6,182,212,0.8)] animate-pulse top-1/2" />
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
            Document Specimen
          </h3>
        </div>
        <span className="text-[10px] font-mono text-slateText-400 px-2 py-0.5 rounded bg-canvas-900 border border-canvas-700">
          {previewUrl ? "ACTIVE UPLOAD" : "SPECIMEN RECORD"}
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
            title="Zoom In"
            className="p-1.5 rounded-lg bg-canvas-900 hover:bg-canvas-700 border border-canvas-700 hover:text-accent-sky transition-colors text-xs"
          >
            <ZoomIn size={14} />
          </button>
          <button
            onClick={handleZoomOut}
            title="Zoom Out"
            className="p-1.5 rounded-lg bg-canvas-900 hover:bg-canvas-700 border border-canvas-700 hover:text-accent-sky transition-colors text-xs"
          >
            <ZoomOut size={14} />
          </button>
          <button
            onClick={handleRotate}
            title="Rotate 90°"
            className="p-1.5 rounded-lg bg-canvas-900 hover:bg-canvas-700 border border-canvas-700 hover:text-accent-sky transition-colors text-xs"
          >
            <RotateCw size={14} />
          </button>
          <button
            onClick={handleReset}
            title="Reset Transform"
            className="p-1.5 rounded-lg bg-canvas-900 hover:bg-canvas-700 border border-canvas-700 hover:text-accent-sky transition-colors text-xs"
          >
            <RefreshCw size={14} />
          </button>
        </div>

        <button
          onClick={() => setIsFullscreen(true)}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-canvas-900 hover:bg-accent-sky/20 border border-canvas-700 hover:border-accent-sky/40 text-slateText-200 hover:text-accent-sky text-[11px] font-mono font-bold transition-all"
        >
          <Maximize2 size={13} />
          <span>EXPAND</span>
        </button>
      </div>

      {/* Fullscreen Inspection Modal */}
      {isFullscreen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-6">
          <div className="relative w-full max-w-4xl rounded-2xl border border-accent-sky/40 bg-canvas-900 p-6 shadow-[0_0_60px_rgba(6,182,212,0.3)]">
            <div className="flex items-center justify-between pb-4 border-b border-canvas-700 mb-6">
              <div className="flex items-center gap-3">
                <FileText size={20} className="text-accent-sky" />
                <div>
                  <h3 className="text-base font-mono font-black text-slateText-50">
                    High-Resolution Forensic Specimen Inspection
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
