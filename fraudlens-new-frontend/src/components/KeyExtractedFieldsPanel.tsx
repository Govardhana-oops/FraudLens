import React, { useState } from "react";
import {
  User,
  CreditCard,
  Globe,
  Calendar,
  Flag,
  Copy,
  Check,
  FileCode,
  Sparkles,
  MapPin,
  Layers,
} from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface KeyExtractedFieldsPanelProps {
  dossier: UnifiedScreeningDossier;
}

export function KeyExtractedFieldsPanel({ dossier }: KeyExtractedFieldsPanelProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const handleCopy = (key: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(key);
    setTimeout(() => setCopiedField(null), 1800);
  };

  const getFieldValue = (fieldName: string): string => {
    const target = fieldName.toLowerCase();
    const match = dossier.extracted_fields?.find((f) => {
      const fn = f.field_name.toLowerCase();
      if (target === "name") {
        return (
          fn.includes("name") ||
          fn.includes("surname") ||
          fn.includes("given") ||
          fn.includes("holder")
        );
      }
      if (target === "doc_number") {
        return (
          fn.includes("number") ||
          fn.includes("passport_no") ||
          fn.includes("document_number") ||
          fn.includes("doc_num")
        );
      }
      if (target === "nationality") {
        return fn.includes("nationality") || fn.includes("country_code") || fn.includes("citizenship");
      }
      if (target === "dob") {
        return fn.includes("birth") || fn.includes("dob");
      }
      if (target === "gender") {
        return fn.includes("sex") || fn.includes("gender");
      }
      if (target === "issuing_country") {
        return fn.includes("issue") && (fn.includes("state") || fn.includes("country") || fn.includes("org"));
      }
      if (target === "issue_date") {
        return (fn.includes("issue") || fn.includes("issued")) && fn.includes("date");
      }
      if (target === "expiry_date") {
        return fn.includes("expiry") || fn.includes("expiration") || fn.includes("valid_until");
      }
      if (target === "pob") {
        return fn.includes("place") && fn.includes("birth");
      }
      return fn.includes(target);
    });

    if (match && match.extracted_value && match.extracted_value.trim().length > 0) {
      return match.extracted_value.trim();
    }

    // Secondary fallback to root dossier fields
    if (target === "doc_number" && dossier.document_number) return dossier.document_number;
    if (target === "doc_type" && dossier.document_type) return dossier.document_type;

    return "UNKNOWN";
  };

  const fullName = getFieldValue("name");
  const docNumber = getFieldValue("doc_number");
  const docType = dossier.document_type || "PASSPORT";
  const nationality = getFieldValue("nationality");
  const dob = getFieldValue("dob");
  const gender = getFieldValue("gender");
  const issuingCountry = getFieldValue("issuing_country");
  const issueDate = getFieldValue("issue_date");
  const expiryDate = getFieldValue("expiry_date");
  const pob = getFieldValue("pob");

  // MRZ lines extraction from real OCR
  const mrz1Field = dossier.extracted_fields?.find(
    (f) =>
      f.field_name.toLowerCase().includes("mrz") &&
      (f.field_name.includes("1") || f.field_name.toLowerCase().includes("line 1") || f.field_name.toLowerCase().includes("line_1"))
  );
  const mrz2Field = dossier.extracted_fields?.find(
    (f) =>
      f.field_name.toLowerCase().includes("mrz") &&
      (f.field_name.includes("2") || f.field_name.toLowerCase().includes("line 2") || f.field_name.toLowerCase().includes("line_2"))
  );

  const mrzLine1 = mrz1Field?.extracted_value || "— (NO MRZ LINE 1 DETECTED)";
  const mrzLine2 = mrz2Field?.extracted_value || "— (NO MRZ LINE 2 DETECTED)";

  const fields = [
    { label: "Full Name", value: fullName, icon: User, key: "name" },
    { label: "Document Number", value: docNumber, icon: CreditCard, key: "docNum" },
    { label: "Document Type", value: docType, icon: Layers, key: "docType" },
    { label: "Nationality", value: nationality, icon: Globe, key: "nat" },
    { label: "Date of Birth", value: dob, icon: Calendar, key: "dob" },
    { label: "Gender", value: gender, icon: User, key: "gen" },
    { label: "Issuing State", value: issuingCountry, icon: Flag, key: "state" },
    { label: "Date of Issue", value: issueDate, icon: Calendar, key: "iss" },
    { label: "Date of Expiry", value: expiryDate, icon: Calendar, key: "exp" },
    ...(pob !== "UNKNOWN" ? [{ label: "Place of Birth", value: pob, icon: MapPin, key: "pob" }] : []),
  ];

  return (
    <div className="panel-3d p-5 rounded-2xl border border-canvas-600 bg-canvas-850 flex flex-col justify-between relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-canvas-600/80 mb-3">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-accent-teal" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slateText-100">
            Key Extracted Data
          </h3>
        </div>
        <span className="text-[10px] font-mono text-accent-teal px-2 py-0.5 rounded bg-accent-teal/10 border border-accent-teal/30 font-bold">
          {dossier.extracted_fields?.length || 0} TOTAL FIELDS
        </span>
      </div>

      {/* Fields List */}
      <div className="space-y-1.5 overflow-y-auto max-h-[360px] pr-1 scrollbar-thin">
        {fields.map((f) => {
          const Icon = f.icon;
          const isUnknown = f.value === "UNKNOWN" || f.value === "—";
          return (
            <div
              key={f.key}
              className="p-2 rounded-xl bg-canvas-900/80 border border-canvas-700/70 hover:border-accent-sky/40 transition-colors flex items-center justify-between gap-2"
            >
              <div className="flex items-center gap-2 min-w-0">
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-canvas-800 border border-canvas-700 text-slateText-400">
                  <Icon size={13} />
                </div>
                <div className="min-w-0">
                  <span className="text-[9px] font-mono uppercase text-slateText-400 block tracking-wider leading-none">
                    {f.label}
                  </span>
                  <span
                    className={`text-xs font-mono font-bold truncate block mt-0.5 ${
                      isUnknown ? "text-slateText-500 italic" : "text-slateText-100"
                    }`}
                  >
                    {f.value}
                  </span>
                </div>
              </div>

              {!isUnknown && (
                <button
                  onClick={() => handleCopy(f.key, f.value)}
                  className="p-1 rounded text-slateText-400 hover:text-accent-sky transition-colors shrink-0"
                  title="Copy Field"
                >
                  {copiedField === f.key ? (
                    <Check size={12} className="text-accent-emerald" />
                  ) : (
                    <Copy size={12} />
                  )}
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* MRZ Block Section */}
      <div className="mt-3 pt-3 border-t border-canvas-600/80">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-1.5 text-[10px] font-mono font-bold text-slateText-300">
            <FileCode size={13} className="text-accent-sky" />
            <span>ICAO 9303 MRZ ENCODING</span>
          </div>
          <button
            onClick={() => handleCopy("mrz", `${mrzLine1}\n${mrzLine2}`)}
            className="text-[10px] font-mono text-accent-sky hover:underline flex items-center gap-1"
          >
            {copiedField === "mrz" ? (
              <Check size={11} className="text-accent-emerald" />
            ) : (
              <Copy size={11} />
            )}
            <span>Copy MRZ</span>
          </button>
        </div>

        <div className="p-2 rounded-lg bg-canvas-950 border border-canvas-700/80 font-mono text-[9px] text-slateText-200 leading-snug tracking-wider select-all break-all">
          <div className="text-accent-teal">{mrzLine1}</div>
          <div className="text-accent-sky">{mrzLine2}</div>
        </div>
      </div>
    </div>
  );
}
