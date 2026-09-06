import React, { useEffect, useState } from "react";
import { api } from "@/services/api";
import { Cpu, CheckCircle2, AlertCircle, XCircle } from "lucide-react";

export function SystemStatusPanel() {
  const [healthData, setHealthData] = useState<{
    status: string;
    modules_ready: string[];
    timestamp?: string;
  }>({
    status: "CHECKING",
    modules_ready: ["module1_ocr", "module2_document_validation", "module3_tampering_detection", "module4_face_verification", "module5_explainable_evidence", "module6_database_sync", "module7_integration_engine"],
  });

  useEffect(() => {
    let isMounted = true;
    async function fetchHealth() {
      try {
        const res = await api.getHealth();
        if (isMounted && res) {
          setHealthData(res);
        }
      } catch {
        if (isMounted) {
          setHealthData((prev) => ({ ...prev, status: "STANDBY" }));
        }
      }
    }
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const modulesList = [
    { key: "ocr", name: "OCR", desc: "Multi-Engine EasyOCR/Tesseract", modId: "module1_ocr" },
    { key: "mrz", name: "MRZ", desc: "ICAO Doc 9303 Checksum Engine", modId: "module2_document_validation" },
    { key: "valid", name: "VALID", desc: "Rule-Based Validation Matrix", modId: "module2_document_validation" },
    { key: "tamper", name: "TAMPER", desc: "Neural Forensic Detection", modId: "module3_tampering_detection" },
    { key: "face", name: "FACE", desc: "1:1 Biometric Face & Liveness", modId: "module4_face_verification" },
    { key: "evidence", name: "EVIDENCE", desc: "Explainable Merkle Dossier", modId: "module5_explainable_evidence" },
    { key: "sync", name: "SYNC", desc: "SQLite & Cloud Sync Engine", modId: "module6_database_sync" },
  ];

  const isHealthy = healthData.status === "HEALTHY" || healthData.status === "healthy";
  const readyCount = isHealthy ? healthData.modules_ready?.length || 7 : 0;

  return (
    <div className="panel-3d p-5 flex flex-col justify-between border-cyan-900/60 bg-[#0A1624]/90 backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-[#20E3C2]" />
          <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
            SYSTEM STATUS
          </h2>
        </div>
        <span className="text-[11px] font-mono font-bold text-emerald-400">
          {readyCount}/7 Ready
        </span>
      </div>

      {/* 7 Modules Indicators */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2.5 my-3">
        {modulesList.map((mod) => {
          const isModuleReady = isHealthy && healthData.modules_ready?.includes(mod.modId);
          return (
            <div
              key={mod.key}
              className="p-2.5 rounded-lg bg-[#06101B]/80 border border-cyan-950/80 flex flex-col items-center justify-between text-center group hover:border-[#20E3C2]/60 transition-colors"
            >
              <span className="text-[11px] font-mono font-bold text-white mb-1">
                {mod.name}
              </span>
              <div className="flex items-center gap-1.5 my-1">
                <span
                  className={`w-2 h-2 rounded-full ${
                    isModuleReady
                      ? "bg-emerald-400 shadow-[0_0_6px_#10B981] animate-pulse"
                      : isHealthy
                      ? "bg-amber-400 shadow-[0_0_6px_#F59E0B]"
                      : "bg-rose-500 shadow-[0_0_6px_#EF4444]"
                  }`}
                />
                <span className="text-[9px] font-mono font-bold text-[#7E9AB8]">
                  {isModuleReady ? "ONLINE" : isHealthy ? "ACTIVE" : "STANDBY"}
                </span>
              </div>
              <span className="text-[8px] text-[#5A7A9C] leading-tight truncate w-full mt-1">
                {mod.desc.split(" ")[0]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
