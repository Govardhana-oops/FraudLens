import React, { useState } from "react";
import { Copy, Check, Scan, Sparkles } from "lucide-react";
import type { UnifiedScreeningDossier, ExtractedField } from "@/types";
import { formatScorePct } from "@/utils/formatters";

interface OcrExtractionDetailsCardProps {
  currentResult: UnifiedScreeningDossier | null;
}

export function OcrExtractionDetailsCard({ currentResult }: OcrExtractionDetailsCardProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    if (!text || text === "N/A" || text === "UNKNOWN") return;
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Extract helper supporting Arrays, Dictionary Objects, and direct properties
  const rawFields = currentResult?.extracted_fields;
  const getField = (aliases: string[], fallback = "UNKNOWN"): string => {
    if (!currentResult) return fallback;

    // 1. If extracted_fields is an Array of ExtractedField objects
    if (Array.isArray(rawFields)) {
      for (const alias of aliases) {
        const target = alias.toLowerCase().replace(/[^a-z0-9]/g, "");
        const found = rawFields.find((f) => {
          if (!f || !f.field_name) return false;
          const name = f.field_name.toLowerCase().replace(/[^a-z0-9]/g, "");
          return name === target || name.includes(target) || target.includes(name);
        });
        if (found && found.extracted_value && String(found.extracted_value).trim() !== "" && String(found.extracted_value).trim() !== "UNKNOWN") {
          return String(found.extracted_value).trim();
        }
      }
    }

    // 2. If extracted_fields is a Dictionary / Record Object
    if (rawFields && typeof rawFields === "object" && !Array.isArray(rawFields)) {
      for (const alias of aliases) {
        const target = alias.toLowerCase().replace(/[^a-z0-9]/g, "");
        for (const [key, val] of Object.entries(rawFields)) {
          const normKey = key.toLowerCase().replace(/[^a-z0-9]/g, "");
          if (normKey === target || normKey.includes(target) || target.includes(normKey)) {
            if (val !== undefined && val !== null) {
              const v = typeof val === "object" && (val as any).value !== undefined ? (val as any).value : val;
              if (v !== undefined && v !== null && String(v).trim() !== "" && String(v).trim() !== "UNKNOWN") {
                return String(v).trim();
              }
            }
          }
        }
      }
    }

    // 3. Direct top-level properties on currentResult
    for (const alias of aliases) {
      const propVal = (currentResult as any)[alias];
      if (propVal !== undefined && propVal !== null && String(propVal).trim() !== "" && String(propVal).trim() !== "UNKNOWN") {
        return String(propVal).trim();
      }
    }

    return fallback;
  };

  // Derive all 12 key visual fields from real OCR data only
  const surname = getField(["surname", "last_name"]);
  const givenNames = getField(["given_names", "given_name", "first_name"]);
  let fullName = getField(["full_name", "name", "passenger_name", "holder_name"]);
  if (fullName === "UNKNOWN" && (surname !== "UNKNOWN" || givenNames !== "UNKNOWN")) {
    fullName = [givenNames !== "UNKNOWN" ? givenNames : "", surname !== "UNKNOWN" ? surname : ""].filter(Boolean).join(" ").trim() || "UNKNOWN";
  }

  const dob = getField(["date_of_birth", "dob", "birth_date"]);
  const gender = getField(["gender", "sex"]);
  const nationality = getField(["nationality", "country_code", "nat", "citizenship"]);
  const docNumber = getField(["passport_number", "document_number", "doc_number", "passport_no", "id_number", "license_number", "permit_number"], currentResult?.document_number || "UNKNOWN");
  const issueDate = getField(["date_of_issue", "issue_date", "doi", "issued_date"]);
  const expiryDate = getField(["date_of_expiry", "expiry_date", "expiration_date", "doe", "valid_until"]);
  const pob = getField(["place_of_birth", "pob", "birth_place"]);
  const docType = currentResult?.document_type || getField(["document_type", "type"]);
  const issuingCountry = getField(["issuing_country", "issuing_state", "country", "state"]);

  // Format MRZ lines from real OCR extraction only
  let mrz1 = getField(["mrz_line_1", "mrz1", "mrz_line1", "mrz_1", "line_1"]);
  let mrz2 = getField(["mrz_line_2", "mrz2", "mrz_line2", "mrz_2", "line_2"]);

  const rawMrz = (currentResult as any)?.mrz;
  if (mrz1 === "UNKNOWN" && rawMrz) {
    if (rawMrz.line1) mrz1 = String(rawMrz.line1);
    if (rawMrz.line2) mrz2 = String(rawMrz.line2);
    if (mrz1 === "UNKNOWN" && rawMrz.lines && Array.isArray(rawMrz.lines) && rawMrz.lines[0]) {
      mrz1 = String(rawMrz.lines[0]);
      if (rawMrz.lines[1]) mrz2 = String(rawMrz.lines[1]);
    }
  }

  const hasConfidence = currentResult?.confidence_score !== undefined && currentResult?.confidence_score !== null;
  const confidenceScore = hasConfidence
    ? formatScorePct(currentResult.confidence_score)
    : "UNKNOWN";

  return (
    <div className="p-5 rounded-2xl bg-[#071322]/90 border border-cyan-900/60 shadow-lg backdrop-blur-md space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3">
        <div className="flex items-center gap-2">
          <Scan className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
            OCR EXTRACTION DETAILS
          </h2>
        </div>

        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold border transition-colors ${
            hasConfidence
              ? "bg-emerald-950/80 border-emerald-500/50 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.25)]"
              : "bg-canvas-900 border-canvas-700 text-slateText-400"
          }`}
        >
          <Sparkles size={12} className={hasConfidence ? "text-emerald-400" : "text-slateText-400"} />
          <span>{hasConfidence ? `Confidence: ${confidenceScore}` : "Confidence: UNKNOWN"}</span>
        </div>
      </div>

      {/* Grid of Compact Rectangular Field Cards (4 cols on xl, 2 on mobile) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Full Name */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Full Name</span>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${fullName === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{fullName}</span>
        </div>

        {/* Date of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Birth</span>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${dob === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{dob}</span>
        </div>

        {/* Gender */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Gender</span>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${gender === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{gender}</span>
        </div>

        {/* Nationality */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Nationality</span>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${nationality === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{nationality}</span>
        </div>

        {/* Passport Number */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Passport Number</span>
          <span className={`text-xs font-mono font-bold tracking-wider truncate mt-0.5 ${docNumber === "UNKNOWN" ? "text-slateText-400 italic" : "text-cyan-300"}`}>{docNumber}</span>
        </div>

        {/* Date of Issue */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Issue</span>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${issueDate === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{issueDate}</span>
        </div>

        {/* Date of Expiry */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Expiry</span>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${expiryDate === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{expiryDate}</span>
        </div>

        {/* Place of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Place of Birth</span>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${pob === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{pob}</span>
        </div>

        {/* Document Type */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Document Type</span>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${docType === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{docType}</span>
        </div>

        {/* Issuing Country */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Issuing Country</span>
          <span className={`text-xs font-mono font-bold tracking-wide truncate mt-0.5 ${issuingCountry === "UNKNOWN" ? "text-slateText-400 italic" : "text-emerald-400"}`}>{issuingCountry}</span>
        </div>

        {/* MRZ Line 1 (Spans 2 cols) */}
        <div className="col-span-2 p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex items-center justify-between gap-2 hover:border-cyan-800 transition-colors">
          <div className="min-w-0 flex-1">
            <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 1)</span>
            <span className={`text-[11px] font-mono font-bold tracking-tight block truncate mt-0.5 select-all ${mrz1 === "UNKNOWN" ? "text-slateText-400 italic" : "text-slate-200"}`}>
              {mrz1}
            </span>
          </div>
          {mrz1 !== "UNKNOWN" && (
            <button
              type="button"
              onClick={() => copyToClipboard(mrz1, "mrz1")}
              title="Copy MRZ Line 1"
              className="p-1.5 rounded-lg bg-[#071524] hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-cyan-900 shrink-0 transition-colors"
            >
              {copiedKey === "mrz1" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
            </button>
          )}
        </div>

        {/* MRZ Line 2 (Spans 2 cols or row) */}
        <div className="col-span-2 md:col-span-4 p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex items-center justify-between gap-2 hover:border-cyan-800 transition-colors">
          <div className="min-w-0 flex-1">
            <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 2)</span>
            <span className={`text-[11px] font-mono font-bold tracking-tight block truncate mt-0.5 select-all ${mrz2 === "UNKNOWN" ? "text-slateText-400 italic" : "text-slate-200"}`}>
              {mrz2}
            </span>
          </div>
          {mrz2 !== "UNKNOWN" && (
            <button
              type="button"
              onClick={() => copyToClipboard(mrz2, "mrz2")}
              title="Copy MRZ Line 2"
              className="p-1.5 rounded-lg bg-[#071524] hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-cyan-900 shrink-0 transition-colors"
            >
              {copiedKey === "mrz2" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
