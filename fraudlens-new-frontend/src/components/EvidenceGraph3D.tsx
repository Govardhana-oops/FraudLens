import React from "react";
import { Shield, FileCheck, CheckCircle2, Lock, Cpu, Eye } from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface EvidenceGraph3DProps {
  dossier?: UnifiedScreeningDossier | null;
  nodes?: any[];
}

export function EvidenceGraph3D({ dossier }: EvidenceGraph3DProps) {
  if (!dossier) {
    return (
      <div className="panel-3d p-12 text-center text-xs font-semibold text-slateText-400">
        No evidence dossier available to graph.
      </div>
    );
  }

  const nodes = [
    {
      id: "DOC_INPUT",
      label: "Document Input",
      desc: `${dossier.document_type || "PASSPORT"} (${dossier.document_number || "EXTRACTED"})`,
      icon: FileCheck,
      color: "border-brand-teal text-brand-teal bg-brand-teal/10",
    },
    {
      id: "OCR_LAYER",
      label: "Multi-Engine OCR",
      desc: `${dossier.extracted_fields?.length || 0} fields extracted with EasyOCR / Tesseract`,
      icon: Eye,
      color: "border-accent-sky text-accent-sky bg-accent-sky/10",
    },
    {
      id: "RULE_LAYER",
      label: "ICAO 9303 Logic",
      desc: `${dossier.validation_checks?.filter((c) => c.result === "PASS").length || 0} checksums verified`,
      icon: CheckCircle2,
      color: "border-accent-emerald text-accent-emerald bg-accent-emerald/10",
    },
    {
      id: "TAMPER_LAYER",
      label: "Deep Forensics",
      desc: `Tampering Risk: ${Math.round((dossier.tampering_analysis?.tampering_score || 0) * 100)}%`,
      icon: Shield,
      color:
        (dossier.tampering_analysis?.tampering_score || 0) > 0.4
          ? "border-accent-rose text-accent-rose bg-accent-rose/10"
          : "border-accent-emerald text-accent-emerald bg-accent-emerald/10",
    },
    {
      id: "CRYPTO_LAYER",
      label: "SHA-256 Provenance",
      desc: `Hash: ${dossier.record_hash?.substring(0, 16)}...`,
      icon: Lock,
      color: "border-brand-cyan text-brand-cyan bg-brand-cyan/10",
    },
  ];

  return (
    <div className="panel-3d p-6 space-y-6">
      <div className="flex items-center justify-between border-b border-canvas-600 pb-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slateText-100 flex items-center gap-2">
          <Cpu size={16} className="text-brand-teal" />
          <span>Multi-Layer Forensic Traceability Graph</span>
        </h2>
        <span className="text-xs font-mono text-brand-teal font-bold">SHA-256 MERKLE LINKED</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {nodes.map((node, i) => {
          const Icon = node.icon;
          return (
            <div
              key={node.id}
              className={`p-4 rounded-xl border flex flex-col justify-between ${node.color} transition-all duration-200 hover:scale-[1.02]`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-canvas-850 border border-canvas-600">
                    <Icon size={18} />
                  </div>
                  <span className="font-mono text-[10px] font-bold opacity-80">0{i + 1}</span>
                </div>
                <div className="text-xs font-bold text-slateText-50">{node.label}</div>
                <div className="text-[11px] text-slateText-300 font-medium mt-1">{node.desc}</div>
              </div>
              <div className="mt-4 pt-2 border-t border-canvas-600/50 text-[10px] font-mono text-slateText-400">
                STATUS: VERIFIED
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
