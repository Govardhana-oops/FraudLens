import React from "react";
import type { UnifiedScreeningDossier } from "@/types";
import { BookOpen, FileBadge2, CreditCard, Shield, FileCheck2 } from "lucide-react";

interface DocumentTypeBreakdownProps {
  records: UnifiedScreeningDossier[];
}

export function DocumentTypeBreakdown({ records }: DocumentTypeBreakdownProps) {
  const total = records.length;

  const countByType = {
    PASSPORT: records.filter((r) => !r.document_type || r.document_type.toUpperCase() === "PASSPORT").length,
    VISA: records.filter((r) => r.document_type && r.document_type.toUpperCase() === "VISA").length,
    NATIONAL_ID: records.filter(
      (r) => r.document_type && (r.document_type.toUpperCase() === "NATIONAL_ID" || r.document_type.toUpperCase() === "ID_CARD")
    ).length,
    DRIVING_LICENSE: records.filter(
      (r) => r.document_type && (r.document_type.toUpperCase() === "DRIVING_LICENSE" || r.document_type.toUpperCase() === "DRIVERS_LICENSE")
    ).length,
    PERMIT: records.filter(
      (r) => r.document_type && (r.document_type.toUpperCase() === "RESIDENCE_PERMIT" || r.document_type.toUpperCase() === "PERMIT")
    ).length,
  };

  const docTypes = [
    {
      label: "Passport",
      icon: BookOpen,
      count: countByType.PASSPORT,
      color: "from-teal-500 to-cyan-400",
    },
    {
      label: "Visa",
      icon: FileBadge2,
      count: countByType.VISA,
      color: "from-sky-500 to-blue-400",
    },
    {
      label: "National ID",
      icon: CreditCard,
      count: countByType.NATIONAL_ID,
      color: "from-emerald-500 to-teal-400",
    },
    {
      label: "Driving Licence",
      icon: Shield,
      count: countByType.DRIVING_LICENSE,
      color: "from-amber-500 to-yellow-400",
    },
    {
      label: "Permit",
      icon: FileCheck2,
      count: countByType.PERMIT,
      color: "from-purple-500 to-pink-400",
    },
  ];

  return (
    <div className="panel-3d p-5 flex flex-col justify-between border-cyan-900/60 bg-[#0A1624]/90 backdrop-blur-md">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#00D9F5] shadow-[0_0_8px_#00D9F5]" />
          <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
            DOCUMENT TYPE BREAKDOWN
          </h2>
        </div>
        <span className="text-[11px] font-mono text-[#5A7A9C]">
          5 Categories
        </span>
      </div>

      {/* Rows */}
      <div className="space-y-3.5 my-3">
        {docTypes.map((dt) => {
          const Icon = dt.icon;
          const pct = total > 0 ? Math.round((dt.count / total) * 100) : 0;
          return (
            <div key={dt.label} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <Icon className="w-3.5 h-3.5 text-cyan-400" />
                  <span className="font-semibold text-slate-200">{dt.label}</span>
                </div>
                <div className="flex items-center gap-1.5 font-mono text-xs">
                  <span className="font-bold text-white">{dt.count}</span>
                  <span className="text-[11px] text-[#5A7A9C]">({pct}%)</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="h-2 w-full rounded-full bg-[#06101B] overflow-hidden border border-cyan-950">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${dt.color} transition-all duration-500`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
