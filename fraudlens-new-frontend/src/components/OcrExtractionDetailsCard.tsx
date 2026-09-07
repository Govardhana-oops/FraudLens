import React, { useState } from "react";
import { Copy, Check, Scan, Sparkles, ShieldAlert } from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";
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

  const isDemoMode = Boolean(
    currentResult?.demo_mode || (currentResult?.metadata as any)?.demo_fallback
  );

  // Extract helper supporting Arrays, Dictionary Objects, and direct properties
  const rawFields = currentResult?.extracted_fields;

  const getFieldData = (
    aliases: string[],
    fallback = "UNKNOWN",
    defaultConf: number | null = null
  ): { value: string; confidence: number | null } => {
    if (!currentResult) return { value: fallback, confidence: null };

    // 1. If extracted_fields is an Array of ExtractedField objects
    if (Array.isArray(rawFields)) {
      for (const alias of aliases) {
        const target = alias.toLowerCase().replace(/[^a-z0-9]/g, "");
        const found = rawFields.find((f) => {
          if (!f || !f.field_name) return false;
          const name = f.field_name.toLowerCase().replace(/[^a-z0-9]/g, "");
          return name === target || name.includes(target) || target.includes(name);
        });
        if (
          found &&
          found.extracted_value &&
          String(found.extracted_value).trim() !== "" &&
          String(found.extracted_value).trim() !== "UNKNOWN"
        ) {
          return {
            value: String(found.extracted_value).trim(),
            confidence: typeof found.confidence === "number" ? found.confidence : defaultConf,
          };
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
              const conf = typeof val === "object" && typeof (val as any).confidence === "number" ? (val as any).confidence : defaultConf;
              if (v !== undefined && v !== null && String(v).trim() !== "" && String(v).trim() !== "UNKNOWN") {
                return {
                  value: String(v).trim(),
                  confidence: conf,
                };
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
        return {
          value: String(propVal).trim(),
          confidence: defaultConf,
        };
      }
    }

    return { value: fallback, confidence: defaultConf };
  };

  // Derive all 12 key visual fields
  const surnameData = getFieldData(["surname", "last_name"]);
  const givenNamesData = getFieldData(["given_names", "given_name", "first_name"]);
  let fullNameData = getFieldData(["full_name", "name", "passenger_name", "holder_name"]);
  if (fullNameData.value === "UNKNOWN" && (surnameData.value !== "UNKNOWN" || givenNamesData.value !== "UNKNOWN")) {
    const combined = [givenNamesData.value !== "UNKNOWN" ? givenNamesData.value : "", surnameData.value !== "UNKNOWN" ? surnameData.value : ""]
      .filter(Boolean)
      .join(" ")
      .trim();
    if (combined) {
      fullNameData = {
        value: combined,
        confidence: surnameData.confidence || givenNamesData.confidence || null,
      };
    }
  }

  const dobData = getFieldData(["date_of_birth", "dob", "birth_date"]);
  const genderData = getFieldData(["gender", "sex"]);
  const nationalityData = getFieldData(["nationality", "country_code", "nat", "citizenship"]);
  const docNumberData = getFieldData(
    ["passport_number", "document_number", "doc_number", "passport_no", "id_number", "license_number", "permit_number"],
    currentResult?.document_number || "UNKNOWN"
  );
  const issueDateData = getFieldData(["date_of_issue", "issue_date", "doi", "issued_date"]);
  const expiryDateData = getFieldData(["date_of_expiry", "expiry_date", "expiration_date", "doe", "valid_until"]);
  const pobData = getFieldData(["place_of_birth", "pob", "birth_place"]);
  const docTypeData = {
    value: currentResult?.document_type || getFieldData(["document_type", "type"]).value,
    confidence: getFieldData(["document_type", "type"]).confidence || 0.99,
  };
  const issuingCountryData = getFieldData(["issuing_country", "issuing_state", "country", "state"]);

  // Format MRZ lines from real OCR extraction only
  let mrz1Data = getFieldData(["mrz_line_1", "mrz1", "mrz_line1", "mrz_1", "line_1"]);
  let mrz2Data = getFieldData(["mrz_line_2", "mrz2", "mrz_line2", "mrz_2", "line_2"]);

  const rawMrz = (currentResult as any)?.mrz;
  if (mrz1Data.value === "UNKNOWN" && rawMrz) {
    if (rawMrz.line1) mrz1Data = { value: String(rawMrz.line1), confidence: 0.96 };
    if (rawMrz.line2) mrz2Data = { value: String(rawMrz.line2), confidence: 0.96 };
    if (mrz1Data.value === "UNKNOWN" && rawMrz.lines && Array.isArray(rawMrz.lines) && rawMrz.lines[0]) {
      mrz1Data = { value: String(rawMrz.lines[0]), confidence: 0.96 };
      if (rawMrz.lines[1]) mrz2Data = { value: String(rawMrz.lines[1]), confidence: 0.96 };
    }
  }

  const hasConfidence = currentResult?.confidence_score !== undefined && currentResult?.confidence_score !== null;
  const confidenceScore = hasConfidence
    ? formatScorePct(currentResult.confidence_score)
    : "UNKNOWN";

  return (
    <div className="p-5 rounded-2xl bg-[#071322]/90 border border-cyan-900/60 shadow-lg backdrop-blur-md space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3 flex-wrap gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <Scan className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
            OCR EXTRACTION DETAILS
          </h2>
          {isDemoMode && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-950/90 text-amber-300 border border-amber-500/60 shadow-[0_0_12px_rgba(245,158,11,0.25)]">
              <ShieldAlert size={10} className="text-amber-400" />
              <span>DEMO MODE — SAMPLE OCR DATA</span>
            </span>
          )}
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
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Full Name</span>
            {fullNameData.confidence !== null && fullNameData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(fullNameData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${fullNameData.value === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{fullNameData.value}</span>
        </div>

        {/* Date of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Birth</span>
            {dobData.confidence !== null && dobData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(dobData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${dobData.value === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{dobData.value}</span>
        </div>

        {/* Gender */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Gender</span>
            {genderData.confidence !== null && genderData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(genderData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${genderData.value === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{genderData.value}</span>
        </div>

        {/* Nationality */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Nationality</span>
            {nationalityData.confidence !== null && nationalityData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(nationalityData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${nationalityData.value === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{nationalityData.value}</span>
        </div>

        {/* Passport Number */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Passport Number</span>
            {docNumberData.confidence !== null && docNumberData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(docNumberData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-mono font-bold tracking-wider truncate mt-0.5 ${docNumberData.value === "UNKNOWN" ? "text-slateText-400 italic" : "text-cyan-300"}`}>{docNumberData.value}</span>
        </div>

        {/* Date of Issue */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Issue</span>
            {issueDateData.confidence !== null && issueDateData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(issueDateData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${issueDateData.value === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{issueDateData.value}</span>
        </div>

        {/* Date of Expiry */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Expiry</span>
            {expiryDateData.confidence !== null && expiryDateData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(expiryDateData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${expiryDateData.value === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{expiryDateData.value}</span>
        </div>

        {/* Place of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Place of Birth</span>
            {pobData.confidence !== null && pobData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(pobData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${pobData.value === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{pobData.value}</span>
        </div>

        {/* Document Type */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Document Type</span>
            {docTypeData.confidence !== null && docTypeData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(docTypeData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-bold tracking-wide truncate mt-0.5 ${docTypeData.value === "UNKNOWN" ? "text-slateText-400 font-mono italic" : "text-white"}`}>{docTypeData.value}</span>
        </div>

        {/* Issuing Country */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Issuing Country</span>
            {issuingCountryData.confidence !== null && issuingCountryData.value !== "UNKNOWN" && (
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(issuingCountryData.confidence * 100)}%</span>
            )}
          </div>
          <span className={`text-xs font-mono font-bold tracking-wide truncate mt-0.5 ${issuingCountryData.value === "UNKNOWN" ? "text-slateText-400 italic" : "text-emerald-400"}`}>{issuingCountryData.value}</span>
        </div>

        {/* MRZ Line 1 (Spans 2 cols) */}
        <div className="col-span-2 p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex items-center justify-between gap-2 hover:border-cyan-800 transition-colors">
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-1">
              <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 1)</span>
              {mrz1Data.confidence !== null && mrz1Data.value !== "UNKNOWN" && (
                <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(mrz1Data.confidence * 100)}%</span>
              )}
            </div>
            <span className={`text-[11px] font-mono font-bold tracking-tight block truncate mt-0.5 select-all ${mrz1Data.value === "UNKNOWN" ? "text-slateText-400 italic" : "text-slate-200"}`}>
              {mrz1Data.value}
            </span>
          </div>
          {mrz1Data.value !== "UNKNOWN" && (
            <button
              type="button"
              onClick={() => copyToClipboard(mrz1Data.value, "mrz1")}
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
            <div className="flex items-center justify-between gap-1">
              <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 2)</span>
              {mrz2Data.confidence !== null && mrz2Data.value !== "UNKNOWN" && (
                <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(mrz2Data.confidence * 100)}%</span>
              )}
            </div>
            <span className={`text-[11px] font-mono font-bold tracking-tight block truncate mt-0.5 select-all ${mrz2Data.value === "UNKNOWN" ? "text-slateText-400 italic" : "text-slate-200"}`}>
              {mrz2Data.value}
            </span>
          </div>
          {mrz2Data.value !== "UNKNOWN" && (
            <button
              type="button"
              onClick={() => copyToClipboard(mrz2Data.value, "mrz2")}
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
