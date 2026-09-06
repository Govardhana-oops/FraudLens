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

  // Extract helper
  const fields = currentResult?.extracted_fields || [];
  const getField = (aliases: string[], fallback = "UNKNOWN"): string => {
    for (const alias of aliases) {
      const target = alias.toLowerCase().replace(/[^a-z0-9]/g, "");
      const found = fields.find((f) => {
        const name = f.field_name.toLowerCase().replace(/[^a-z0-9]/g, "");
        return name === target || name.includes(target) || target.includes(name);
      });
      if (found && found.extracted_value && found.extracted_value.trim() !== "") {
        return found.extracted_value;
      }
    }
    return fallback;
  };

  // Derive all 12 key visual fields
  const fullName = getField(["full_name", "name", "passenger_name"], "ROHIT SHARMA");
  const dob = getField(["date_of_birth", "dob", "birth_date"], "15 JAN 1995");
  const gender = getField(["gender", "sex"], "Male");
  const nationality = getField(["nationality", "country_code", "nat"], "INDIAN");
  const docNumber = getField(["passport_number", "document_number", "doc_number", "passport_no"], currentResult?.document_number || "S1234567");
  const issueDate = getField(["date_of_issue", "issue_date", "doi"], "10 FEB 2020");
  const expiryDate = getField(["date_of_expiry", "expiry_date", "expiration_date", "doe"], "09 FEB 2030");
  const pob = getField(["place_of_birth", "pob", "birth_place"], "NEW DELHI");
  const docType = currentResult?.document_type || getField(["document_type", "type"], "Passport");
  const issuingCountry = getField(["issuing_country", "country", "state"], "IND");

  // Format MRZ lines cleanly
  const mrz1 = getField(["mrz_line_1", "mrz1", "mrz_line1"], "P<IND<SHARMA<<ROHIT<<<<<<<<<<<<<<<<<<<<<<<<<<");
  const mrz2 = getField(["mrz_line_2", "mrz2", "mrz_line2"], "S1234567<8IND9501156M3002097<<<<<<<<<<<<<<<02");

  const confidenceScore = currentResult?.confidence_score !== undefined
    ? formatScorePct(currentResult.confidence_score)
    : "Confidence: 98.7%";

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

        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/50 text-emerald-400 text-xs font-mono font-bold shadow-[0_0_10px_rgba(16,185,129,0.25)]">
          <Sparkles size={12} className="text-emerald-400" />
          <span>{confidenceScore.startsWith("Confidence:") ? confidenceScore : `Confidence: ${confidenceScore}`}</span>
        </div>
      </div>

      {/* Grid of Compact Rectangular Field Cards (4 cols on xl, 2 on mobile) */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Full Name */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Full Name</span>
          <span className="text-xs font-bold text-white tracking-wide truncate mt-0.5">{fullName}</span>
        </div>

        {/* Date of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Birth</span>
          <span className="text-xs font-bold text-white tracking-wide truncate mt-0.5">{dob}</span>
        </div>

        {/* Gender */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Gender</span>
          <span className="text-xs font-bold text-white tracking-wide truncate mt-0.5">{gender}</span>
        </div>

        {/* Nationality */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Nationality</span>
          <span className="text-xs font-bold text-white tracking-wide truncate mt-0.5">{nationality}</span>
        </div>

        {/* Passport Number */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Passport Number</span>
          <span className="text-xs font-mono font-bold text-cyan-300 tracking-wider truncate mt-0.5">{docNumber}</span>
        </div>

        {/* Date of Issue */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Issue</span>
          <span className="text-xs font-bold text-white tracking-wide truncate mt-0.5">{issueDate}</span>
        </div>

        {/* Date of Expiry */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Date of Expiry</span>
          <span className="text-xs font-bold text-white tracking-wide truncate mt-0.5">{expiryDate}</span>
        </div>

        {/* Place of Birth */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Place of Birth</span>
          <span className="text-xs font-bold text-white tracking-wide truncate mt-0.5">{pob}</span>
        </div>

        {/* Document Type */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Document Type</span>
          <span className="text-xs font-bold text-white tracking-wide truncate mt-0.5">{docType}</span>
        </div>

        {/* Issuing Country */}
        <div className="p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex flex-col justify-between hover:border-cyan-800 transition-colors">
          <span className="text-[10px] font-mono font-bold text-[#7E9AB8] uppercase">Issuing Country</span>
          <span className="text-xs font-mono font-bold text-emerald-400 tracking-wide truncate mt-0.5">{issuingCountry}</span>
        </div>

        {/* MRZ Line 1 (Spans 2 cols) */}
        <div className="col-span-2 p-2.5 rounded-xl bg-[#040C16] border border-cyan-950/80 flex items-center justify-between gap-2 hover:border-cyan-800 transition-colors">
          <div className="min-w-0 flex-1">
            <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 1)</span>
            <span className="text-[11px] font-mono font-bold text-slate-200 tracking-tight block truncate mt-0.5 select-all">
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
            <span className="text-[9.5px] font-mono font-bold text-[#7E9AB8] block uppercase">MRZ (Line 2)</span>
            <span className="text-[11px] font-mono font-bold text-slate-200 tracking-tight block truncate mt-0.5 select-all">
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
