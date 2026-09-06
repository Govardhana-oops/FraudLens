import React, { useEffect, useState } from "react";
import { Scan, ShieldCheck, AlertTriangle, XCircle, RefreshCw, Cpu, CheckCircle2 } from "lucide-react";
import type { FaceComparisonResult } from "@/types";

interface CentralBiometricHudProps {
  isProcessing: boolean;
  activeStage: number; // 0 to 6
  result: FaceComparisonResult | null;
  hasReferenceFace: boolean;
  hasLiveCapture: boolean;
}

export function CentralBiometricHud({
  isProcessing,
  activeStage,
  result,
  hasReferenceFace,
  hasLiveCapture,
}: CentralBiometricHudProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    if (result && result.similarity_score !== undefined) {
      const targetPercent = Math.round(result.similarity_score * 1000) / 10;
      let current = 0;
      const step = Math.max(1, targetPercent / 20);
      const timer = setInterval(() => {
        current += step;
        if (current >= targetPercent) {
          setAnimatedScore(targetPercent);
          clearInterval(timer);
        } else {
          setAnimatedScore(Math.round(current * 10) / 10);
        }
      }, 25);
      return () => clearInterval(timer);
    } else {
      setAnimatedScore(0);
    }
  }, [result]);

  const circumference = 2 * Math.PI * 72; // radius 72
  const strokeOffset = result
    ? circumference - (Math.min(100, animatedScore) / 100) * circumference
    : circumference;

  const isMatched = result?.matched ?? false;
  const isReview = result && !result.matched && result.similarity_score >= 0.48;
  const isNoMatch = result && !result.matched && result.similarity_score < 0.48;

  let ringColor = "stroke-accent-sky";
  let glowColor = "shadow-[0_0_25px_rgba(59,130,246,0.35)]";
  let textColor = "text-accent-sky";
  let badgeBg = "bg-accent-sky/20 border-accent-sky/50 text-accent-sky";
  let statusText = "WAITING FOR LIVE CAPTURE";

  if (isProcessing) {
    ringColor = "stroke-accent-teal animate-pulse";
    glowColor = "shadow-[0_0_35px_rgba(45,212,191,0.5)]";
    textColor = "text-accent-teal";
    badgeBg = "bg-accent-teal/20 border-accent-teal/50 text-accent-teal";
    statusText = "ANALYZING BIOMETRIC FEATURES";
  } else if (result) {
    if (isMatched) {
      ringColor = "stroke-accent-emerald";
      glowColor = "shadow-[0_0_35px_rgba(16,185,129,0.5)]";
      textColor = "text-accent-emerald";
      badgeBg = "bg-accent-emerald/20 border-accent-emerald/50 text-accent-emerald";
      statusText = "BIOMETRIC MATCH CONFIRMED";
    } else if (isReview) {
      ringColor = "stroke-accent-amber";
      glowColor = "shadow-[0_0_35px_rgba(245,158,11,0.5)]";
      textColor = "text-accent-amber";
      badgeBg = "bg-accent-amber/20 border-accent-amber/50 text-accent-amber";
      statusText = "REVIEW REQUIRED";
    } else {
      ringColor = "stroke-accent-rose";
      glowColor = "shadow-[0_0_35px_rgba(239,68,68,0.5)]";
      textColor = "text-accent-rose";
      badgeBg = "bg-accent-rose/20 border-accent-rose/50 text-accent-rose";
      statusText = "BIOMETRIC MISMATCH";
    }
  }

  return (
    <div className="relative flex flex-col items-center justify-center p-6 bg-canvas-850/80 rounded-2xl border border-canvas-600/80 backdrop-blur-md shadow-2xl overflow-hidden min-h-[360px]">
      {/* Dynamic Cyber Grid & Scanlines Background */}
      <div className="absolute inset-0 bg-grid-ops opacity-30 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-accent-sky/5 to-transparent pointer-events-none" />

      {/* Decorative Biometric Connection Lines from Left & Right */}
      <div className="absolute top-1/2 -left-6 w-12 h-[2px] bg-gradient-to-r from-transparent to-accent-sky/60 -translate-y-1/2 hidden lg:block" />
      <div className="absolute top-1/2 -right-6 w-12 h-[2px] bg-gradient-to-l from-transparent to-accent-teal/60 -translate-y-1/2 hidden lg:block" />

      {/* Header Tag */}
      <div className="relative z-10 flex items-center gap-2 mb-4">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-bold tracking-widest uppercase border bg-canvas-950/80 border-canvas-600 text-slateText-300">
          <Cpu size={13} className="text-accent-sky animate-spin" style={{ animationDuration: "10s" }} />
          <span>1:1 NEURAL MATCHING ENGINE</span>
        </span>
      </div>

      {/* 3D Circular Radar HUD */}
      <div className="relative flex items-center justify-center w-56 h-56 my-2">
        {/* Outer Rotating Reticle */}
        <div
          className={`absolute inset-0 rounded-full border border-dashed border-canvas-500/60 transition-all duration-1000 ${
            isProcessing ? "animate-spin" : "animate-spin"
          }`}
          style={{ animationDuration: isProcessing ? "4s" : "24s" }}
        />

        {/* Secondary Inner Glow Circle */}
        <div
          className={`absolute inset-3 rounded-full border border-canvas-600/50 ${
            isProcessing ? "border-accent-teal/40 animate-ping" : ""
          }`}
          style={{ animationDuration: "3s" }}
        />

        {/* Circular SVG Progress Ring */}
        <svg className="w-48 h-48 -rotate-90 transform" viewBox="0 0 160 160">
          {/* Track */}
          <circle
            cx="80"
            cy="80"
            r="72"
            className="stroke-canvas-700/60 fill-none"
            strokeWidth="8"
          />
          {/* Active Animated Ring */}
          <circle
            cx="80"
            cy="80"
            r="72"
            className={`${ringColor} fill-none transition-all duration-700 ease-out`}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeOffset}
            strokeLinecap="round"
          />
        </svg>

        {/* Center Content Display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-4">
          {isProcessing ? (
            <div className="flex flex-col items-center space-y-2">
              <Scan size={36} className="text-accent-teal animate-bounce" />
              <span className="text-[11px] font-mono font-bold text-accent-teal uppercase tracking-wider animate-pulse">
                SCANNING EMBEDDINGS
              </span>
              <span className="text-[9px] font-mono text-slateText-400">STAGE {activeStage}/6</span>
            </div>
          ) : result ? (
            <div className="flex flex-col items-center">
              <span className="text-[10px] font-mono font-bold text-slateText-400 uppercase tracking-widest">
                SIMILARITY
              </span>
              <div className={`text-4xl font-mono font-black tracking-tight ${textColor}`}>
                {animatedScore.toFixed(1)}%
              </div>
              <span className="text-[10px] font-mono font-bold text-slateText-300 mt-1 uppercase">
                {isMatched ? "MATCHED" : isReview ? "REVIEW" : "MISMATCH"}
              </span>
            </div>
          ) : (
            <div className="flex flex-col items-center space-y-1">
              <Scan size={32} className="text-slateText-400 opacity-60" />
              <span className="text-[11px] font-mono font-bold text-slateText-300 uppercase tracking-wider">
                IDLE
              </span>
              <span className="text-[10px] text-slateText-400 max-w-[120px] leading-tight">
                Capture live photo to begin
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Dynamic Status Determination Badge */}
      <div className="relative z-10 mt-3 flex flex-col items-center gap-1.5">
        <div className={`px-3.5 py-1.5 rounded-lg border text-xs font-mono font-bold tracking-wider uppercase flex items-center gap-2 ${badgeBg} ${glowColor}`}>
          {isProcessing ? (
            <RefreshCw size={14} className="animate-spin text-accent-teal" />
          ) : isMatched ? (
            <CheckCircle2 size={14} className="text-accent-emerald" />
          ) : isReview ? (
            <AlertTriangle size={14} className="text-accent-amber" />
          ) : result ? (
            <XCircle size={14} className="text-accent-rose" />
          ) : (
            <ShieldCheck size={14} className="text-slateText-400" />
          )}
          <span>{statusText}</span>
        </div>

        <span className="text-[11px] font-mono text-slateText-400">
          {result
            ? `Threshold: ${Math.round((result.threshold || 0.72) * 100)}% • Cosine Distance Metric`
            : "ICAO Doc 9303 / ISO/IEC 19794-5 Compliant"}
        </span>
      </div>
    </div>
  );
}
