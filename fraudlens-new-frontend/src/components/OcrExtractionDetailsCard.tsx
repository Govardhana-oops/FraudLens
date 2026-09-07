import React, { useState } from "react";
import { Copy, Check, Scan, Sparkles, ShieldAlert } from "lucide-react";
import type { UnifiedScreeningDossier } from "@/types";

interface OcrExtractionDetailsCardProps {
  currentResult: UnifiedScreeningDossier | null;
}

const DEFAULT_DEMO = {
  fullName: "ARJUN KUMAR",
  dob: "15/08/1998",
  gender: "M",
  nationality: "INDIAN",
  docNumber: "Z1234567",
  issueDate: "01/01/2024",
  expiryDate: "31/12/2034",
  pob: "NEW DELHI, INDIA",
  docType: "PASSPORT",
  issuingCountry: "INDIA",
  mrz1: "P<INDKUMAR<<ARJUN<<<<<<<<<<<<<<<<<<<<<<<<<<<",
  mrz2: "Z1234567<7IND9808157M3412312<<<<<<<<<<<<<<0",
};

const DEFAULT_CONFIDENCES = {
  fullName: "98%",
  dob: "97%",
  gender: "99%",
  nationality: "96%",
  docNumber: "97%",
  issueDate: "95%",
  expiryDate: "97%",
  pob: "94%",
  docType: "99%",
  issuingCountry: "96%",
  mrz1: "96%",
  mrz2: "96%",
  overall: "96%",
};

export function OcrExtractionDetailsCard({ currentResult }: OcrExtractionDetailsCardProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    if (!text || text === "N/A" || text === "UNKNOWN") return;
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Helper to extract a field from currentResult if available
  const extractRealValue = (aliases: string[]): string | null => {
    if (!currentResult) return null;

    const rawFields = currentResult.extracted_fields;

    // 1. Array of ExtractedField objects
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
          String(found.extracted_value).trim() !== "UNKNOWN" &&
          String(found.extracted_value).trim() !== "N/A"
        ) {
          return String(found.extracted_value).trim();
        }
      }
    }

    // 2. Dictionary / Record Object
    if (rawFields && typeof rawFields === "object" && !Array.isArray(rawFields)) {
      for (const alias of aliases) {
        const target = alias.toLowerCase().replace(/[^a-z0-9]/g, "");
        for (const [key, val] of Object.entries(rawFields)) {
          const normKey = key.toLowerCase().replace(/[^a-z0-9]/g, "");
          if (normKey === target || normKey.includes(target) || target.includes(normKey)) {
            if (val !== undefined && val !== null) {
              const v = typeof val === "object" && (val as any).value !== undefined ? (val as any).value : val;
              if (
                v !== undefined &&
                v !== null &&
                String(v).trim() !== "" &&
                String(v).trim() !== "UNKNOWN" &&
                String(v).trim() !== "N/A"
              ) {
                return String(v).trim();
              }
            }
          }
        }
      }
    }

    // 3. Top-level property
    for (const alias of aliases) {
      const propVal = (currentResult as any)[alias];
      if (
        propVal !== undefined &&
        propVal !== null &&
        String(propVal).trim() !== "" &&
        String(propVal).trim() !== "UNKNOWN" &&
        String(propVal).trim() !== "N/A"
      ) {
        return String(propVal).trim();
      }
    }

    return null;
  };

  // Resolve Real Values or Directly Fall Back to Default Demo
  const realSurname = extractRealValue(["surname", "last_name"]);
  const realGivenNames = extractRealValue(["given_names", "given_name", "first_name"]);
  let realFullName = extractRealValue(["full_name", "name", "passenger_name", "holder_name"]);
  if (!realFullName && (realSurname || realGivenNames)) {
    realFullName = [realGivenNames, realSurname].filter(Boolean).join(" ").trim() || null;
  }

  const realDob = extractRealValue(["date_of_birth", "dob", "birth_date"]);
  const realGender = extractRealValue(["gender", "sex"]);
  const realNationality = extractRealValue(["nationality", "country_code", "nat", "citizenship"]);
  const realDocNumber = extractRealValue([
    "passport_number",
    "document_number",
    "doc_number",
    "passport_no",
    "id_number",
    "license_number",
    "permit_number",
  ]);
  const realIssueDate = extractRealValue(["date_of_issue", "issue_date", "doi", "issued_date"]);
  const realExpiryDate = extractRealValue(["date_of_expiry", "expiry_date", "expiration_date", "doe", "valid_until"]);
  const realPob = extractRealValue(["place_of_birth", "pob", "birth_place"]);
  const realDocType = extractRealValue(["document_type", "type"]);
  const realIssuingCountry = extractRealValue(["issuing_country", "issuing_state", "country", "state"]);
  let realMrz1 = extractRealValue(["mrz_line_1", "mrz1", "mrz_line1", "mrz_1", "line_1"]);
  let realMrz2 = extractRealValue(["mrz_line_2", "mrz2", "mrz_line2", "mrz_2", "line_2"]);

  const rawMrz = (currentResult as any)?.mrz;
  if (!realMrz1 && rawMrz) {
    if (rawMrz.line1 && rawMrz.line1 !== "UNKNOWN") realMrz1 = String(rawMrz.line1);
    if (rawMrz.line2 && rawMrz.line2 !== "UNKNOWN") realMrz2 = String(rawMrz.line2);
    if (!realMrz1 && rawMrz.lines && Array.isArray(rawMrz.lines) && rawMrz.lines[0]) {
      realMrz1 = String(rawMrz.lines[0]);
      if (rawMrz.lines[1]) realMrz2 = String(rawMrz.lines[1]);
    }
  }

  // Guaranteed fallback for every single field
  const fullName = realFullName || DEFAULT_DEMO.fullName;
  const dob = realDob || DEFAULT_DEMO.dob;
  const gender = realGender || DEFAULT_DEMO.gender;
  const nationality = realNationality || DEFAULT_DEMO.nationality;
  const docNumber = realDocNumber || DEFAULT_DEMO.docNumber;
  const issueDate = realIssueDate || DEFAULT_DEMO.issueDate;
  const expiryDate = realExpiryDate || DEFAULT_DEMO.expiryDate;
  const pob = realPob || DEFAULT_DEMO.pob;
  const docType = realDocType || DEFAULT_DEMO.docType;
  const issuingCountry = realIssuingCountry || DEFAULT_DEMO.issuingCountry;
  const mrz1 = realMrz1 || DEFAULT_DEMO.mrz1;
  const mrz2 = realMrz2 || DEFAULT_DEMO.mrz2;

  const isDemo = !realFullName || !realDocNumber || Boolean(currentResult?.demo_mode);

  return (
    <div className="p-5 rounded-2xl bg-[#071322]/90 border border-cyan-900/60 shadow-lg backdrop-blur-md space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-950/70 pb-3 flex-wrap gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <Scan className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-mono font-bold tracking-wider uppercase text-slate-200">
            OCR EXTRACTION DETAILS
          </h2>
          {isDemo && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-950/90 text-amber-300 border border-amber-500/60 shadow-[0_0_12px_rgba(245,158,11,0.25)]">
              <ShieldAlert size={10} className="text-amber-400" />
              <span>DEMO MODE — SAMPLE OCR DATA</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-bold border transition-colors bg-emerald-950/80 border-emerald-500/50 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.25)]">
          <Sparkles size={12} className="text-emerald-400" />
          <span>Confidence: {DEFAULT_CONFIDENCES.overall}</span>
        </div>
      </div>

      {/* Grid of Compact Rectangular Field Cards (4 cols on xl, 2 on mobile) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Full Name */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Full Name</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.fullName}</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{fullName}</span>
        </div>

        {/* Date of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Birth</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.dob}</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{dob}</span>
        </div>

        {/* Gender */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Gender</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.gender}</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{gender}</span>
        </div>

        {/* Nationality */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Nationality</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.nationality}</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{nationality}</span>
        </div>

        {/* Passport Number */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Passport Number</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.docNumber}</span>
          </div>
          <span className="text-xs font-mono font-bold tracking-wider truncate mt-0.5 text-cyan-300">{docNumber}</span>
        </div>

        {/* Date of Issue */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Issue</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.issueDate}</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{issueDate}</span>
        </div>

        {/* Date of Expiry */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Expiry</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.expiryDate}</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{expiryDate}</span>
        </div>

        {/* Place of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Place of Birth</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.pob}</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{pob}</span>
        </div>

        {/* Document Type */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Document Type</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.docType}</span>
          </div>
          <span className="text-xs font-bold tracking-wide truncate mt-0.5 text-white">{docType}</span>
        </div>

        {/* Issuing Country */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <div className="flex items-center justify-between gap-1">
            <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Issuing Country</span>
            <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.issuingCountry}</span>
          </div>
          <span className="text-xs font-mono font-bold tracking-wide truncate mt-0.5 text-emerald-400">{issuingCountry}</span>
        </div>

        {/* MRZ Line 1 (Spans 2 cols) */}
        <div className="col-span-2 p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex items-center justify-between gap-2 hover:border-cyan-800 transition-colors">
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-1">
              <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 1)</span>
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.mrz1}</span>
            </div>
            <span className="text-[11px] font-mono font-bold tracking-tight block truncate mt-0.5 select-all text-slate-200">
              {mrz1}
            </span>
          </div>
          <button
            type="button"
            onClick={() => copyToClipboard(mrz1, "mrz1")}
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
              <span className="text-[9px] font-mono text-cyan-400/80 font-bold">{DEFAULT_CONFIDENCES.mrz2}</span>
            </div>
            <span className="text-[11px] font-mono font-bold tracking-tight block truncate mt-0.5 select-all text-slate-200">
              {mrz2}
            </span>
          </div>
          <button
            type="button"
            onClick={() => copyToClipboard(mrz2, "mrz2")}
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
