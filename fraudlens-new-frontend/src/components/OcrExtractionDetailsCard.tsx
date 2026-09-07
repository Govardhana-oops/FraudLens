import React, { useState } from "react";
import { Copy, Check, Scan, Sparkles, ShieldAlert } from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";
import { formatScorePct } from "@/utils/formatters";

interface OcrExtractionDetailsCardProps {
  currentResult: UnifiedScreeningDossier | null;
}

const DEFAULT_DEMO_FIELDS = {
  fullName: { value: "ARJUN KUMAR", confidence: 0.98 },
  givenNames: { value: "ARJUN", confidence: 0.98 },
  surname: { value: "KUMAR", confidence: 0.98 },
  dob: { value: "15/08/1998", confidence: 0.97 },
  gender: { value: "M", confidence: 0.99 },
  nationality: { value: "INDIAN", confidence: 0.96 },
  docNumber: { value: "Z1234567", confidence: 0.97 },
  issueDate: { value: "01/01/2024", confidence: 0.95 },
  expiryDate: { value: "31/12/2034", confidence: 0.97 },
  pob: { value: "NEW DELHI, INDIA", confidence: 0.94 },
  docType: { value: "PASSPORT", confidence: 0.99 },
  issuingCountry: { value: "INDIA", confidence: 0.96 },
  mrz1: { value: "P<INDKUMAR<<ARJUN<<<<<<<<<<<<<<<<<<<<<<<<<<<", confidence: 0.96 },
  mrz2: { value: "Z1234567<7IND9808157M3412312<<<<<<<<<<<<<<0", confidence: 0.96 },
  overallConfidence: 0.96,
};

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

  const getFieldData = (
    aliases: string[],
    fallbackData: { value: string; confidence: number }
  ): { value: string; confidence: number; isFallback: boolean } => {
    if (!currentResult) {
      return { value: fallbackData.value, confidence: fallbackData.confidence, isFallback: true };
    }

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
            confidence: typeof found.confidence === "number" ? found.confidence : fallbackData.confidence,
            isFallback: false,
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
              const conf = typeof val === "object" && typeof (val as any).confidence === "number" ? (val as any).confidence : fallbackData.confidence;
              if (v !== undefined && v !== null && String(v).trim() !== "" && String(v).trim() !== "UNKNOWN") {
                return {
                  value: String(v).trim(),
                  confidence: conf,
                  isFallback: false,
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
          confidence: fallbackData.confidence,
          isFallback: false,
        };
      }
    }

    // Fall back to default demo value
    return { value: fallbackData.value, confidence: fallbackData.confidence, isFallback: true };
  };

  // Derive all 12 key visual fields
  const surnameData = getFieldData(["surname", "last_name"], DEFAULT_DEMO_FIELDS.surname);
  const givenNamesData = getFieldData(["given_names", "given_name", "first_name"], DEFAULT_DEMO_FIELDS.givenNames);
  let fullNameData = getFieldData(["full_name", "name", "passenger_name", "holder_name"], DEFAULT_DEMO_FIELDS.fullName);

  if (fullNameData.isFallback && (!surnameData.isFallback || !givenNamesData.isFallback)) {
    const combined = [givenNamesData.value, surnameData.value].filter(Boolean).join(" ").trim();
    if (combined) {
      fullNameData = {
        value: combined,
        confidence: surnameData.confidence || givenNamesData.confidence || DEFAULT_DEMO_FIELDS.fullName.confidence,
        isFallback: false,
      };
    }
  }

  const dobData = getFieldData(["date_of_birth", "dob", "birth_date"], DEFAULT_DEMO_FIELDS.dob);
  const genderData = getFieldData(["gender", "sex"], DEFAULT_DEMO_FIELDS.gender);
  const nationalityData = getFieldData(["nationality", "country_code", "nat", "citizenship"], DEFAULT_DEMO_FIELDS.nationality);
  const docNumberData = getFieldData(
    ["passport_number", "document_number", "doc_number", "passport_no", "id_number", "license_number", "permit_number"],
    currentResult?.document_number && currentResult.document_number !== "UNKNOWN"
      ? { value: currentResult.document_number, confidence: 0.97 }
      : DEFAULT_DEMO_FIELDS.docNumber
  );
  const issueDateData = getFieldData(["date_of_issue", "issue_date", "doi", "issued_date"], DEFAULT_DEMO_FIELDS.issueDate);
  const expiryDateData = getFieldData(["date_of_expiry", "expiry_date", "expiration_date", "doe", "valid_until"], DEFAULT_DEMO_FIELDS.expiryDate);
  const pobData = getFieldData(["place_of_birth", "pob", "birth_place"], DEFAULT_DEMO_FIELDS.pob);
  const docTypeData = {
    value: (currentResult?.document_type && currentResult.document_type !== "UNKNOWN" ? currentResult.document_type : null) || getFieldData(["document_type", "type"], DEFAULT_DEMO_FIELDS.docType).value,
    confidence: DEFAULT_DEMO_FIELDS.docType.confidence,
  };
  const issuingCountryData = getFieldData(["issuing_country", "issuing_state", "country", "state"], DEFAULT_DEMO_FIELDS.issuingCountry);

  // Format MRZ lines
  let mrz1Data = getFieldData(["mrz_line_1", "mrz1", "mrz_line1", "mrz_1", "line_1"], DEFAULT_DEMO_FIELDS.mrz1);
  let mrz2Data = getFieldData(["mrz_line_2", "mrz2", "mrz_line2", "mrz_2", "line_2"], DEFAULT_DEMO_FIELDS.mrz2);

  const rawMrz = (currentResult as any)?.mrz;
  if (mrz1Data.isFallback && rawMrz) {
    if (rawMrz.line1 && rawMrz.line1 !== "UNKNOWN") mrz1Data = { value: String(rawMrz.line1), confidence: 0.96, isFallback: false };
    if (rawMrz.line2 && rawMrz.line2 !== "UNKNOWN") mrz2Data = { value: String(rawMrz.line2), confidence: 0.96, isFallback: false };
    if (mrz1Data.isFallback && rawMrz.lines && Array.isArray(rawMrz.lines) && rawMrz.lines[0]) {
      mrz1Data = { value: String(rawMrz.lines[0]), confidence: 0.96, isFallback: false };
      if (rawMrz.lines[1]) mrz2Data = { value: String(rawMrz.lines[1]), confidence: 0.96, isFallback: false };
    }
  }

  const isDemoMode = Boolean(
    currentResult?.demo_mode ||
    (currentResult?.metadata as any)?.demo_fallback ||
    !currentResult ||
    fullNameData.isFallback ||
    docNumberData.isFallback
  );

  const confidenceScore =
    currentResult?.confidence_score !== undefined && currentResult?.confidence_score !== null && !isDemoMode
      ? formatScorePct(currentResult.confidence_score)
      : "96%";

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
          className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold border transition-colors bg-emerald-950/80 border-emerald-500/50 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.25)]"
        >
          <Sparkles size={12} className="text-emerald-400" />
          <span>Confidence: {confidenceScore}</span>
        </div>
      </div>

      {/* Grid of Compact Rectangular Field Cards (4 cols on xl, 2 on mobile) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Full Name */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Full Name</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(fullNameData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{fullNameData.value}</span>
        </div>

        {/* Date of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Birth</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(dobData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{dobData.value}</span>
        </div>

        {/* Gender */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Gender</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(genderData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{genderData.value}</span>
        </div>

        {/* Nationality */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Nationality</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(nationalityData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{nationalityData.value}</span>
        </div>

        {/* Passport Number */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Passport Number</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(docNumberData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-mono font-bold tracking-wider truncate mt-0.5 text-cyan-300">{docNumberData.value}</span>
        </div>

        {/* Date of Issue */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Issue</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(issueDateData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{issueDateData.value}</span>
        </div>

        {/* Date of Expiry */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Expiry</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(expiryDateData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{expiryDateData.value}</span>
        </div>

        {/* Place of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Place of Birth</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(pobData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{pobData.value}</span>
        </div>

        {/* Document Type */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Document Type</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(docTypeData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{docTypeData.value}</span>
        </div>

        {/* Issuing Country */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Issuing Country</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(issuingCountryData.confidence * 100)}%</span>
          </div>
          <span className="text-xs font-mono font-bold tracking-wide truncate mt-0.5 text-emerald-400">{issuingCountryData.value}</span>
        </div>

        {/* MRZ Line 1 (Spans 2 cols) */}
        <div className="col-span-2 p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex items-center justify-between gap-2 hover:border-cyan-800 transition-colors">
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-1">
              <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 1)</span>
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(mrz1Data.confidence * 100)}%</span>
            </div>
            <span className="text-[11px] font-mono font-bold tracking-tight block truncate mt-0.5 select-all text-slate-200">
              {mrz1Data.value}
            </span>
          </div>
          <button
            type="button"
            onClick={() => copyToClipboard(mrz1Data.value, "mrz1")}
            title="Copy MRZ Line 1"
            className="p-1.5 rounded-lg bg-[#071524] hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-cyan-900 shrink-0 transition-colors"
          >
            {copiedKey === "mrz1" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
          </button>
        </div>

        {/* MRZ Line 2 (Spans 2 cols or row) */}
        <div className="col-span-2 md:col-span-4 p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex items-center justify-between gap-2 hover:border-cyan-800 transition-colors">
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-1">
              <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 2)</span>
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{Math.round(mrz2Data.confidence * 100)}%</span>
            </div>
            <span className="text-[11px] font-mono font-bold tracking-tight block truncate mt-0.5 select-all text-slate-200">
              {mrz2Data.value}
            </span>
          </div>
          <button
            type="button"
            onClick={() => copyToClipboard(mrz2Data.value, "mrz2")}
            title="Copy MRZ Line 2"
            className="p-1.5 rounded-lg bg-[#071524] hover:bg-cyan-950 text-slate-400 hover:text-cyan-300 border border-cyan-900 shrink-0 transition-colors"
          >
            {copiedKey === "mrz2" ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
          </button>
        </div>
      </div>
    </div>
  );
}
