import React from "react";
import type { ExtractedField } from "@/types";
import { formatScorePct } from "@/utils/formatters";

interface ExtractedFieldsGridProps {
  fields: ExtractedField[];
}

export function ExtractedFieldsGrid({ fields }: ExtractedFieldsGridProps) {
  if (!fields || fields.length === 0) {
    return (
      <div className="panel-3d p-6 text-center text-xs font-semibold text-slateText-400">
        No optical fields extracted yet.
      </div>
    );
  }

  return (
    <div className="panel-3d p-6 space-y-4">
      <div className="flex items-center justify-between border-b border-canvas-600 pb-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slateText-100">
          Extracted Document Fields (MRZ & Visual)
        </h2>
        <span className="rounded bg-canvas-850 px-2 py-0.5 text-xs font-mono font-bold text-brand-teal border border-canvas-600">
          {fields.length} FIELDS
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {fields.map((f, idx) => (
          <div
            key={idx}
            className="p-3 rounded-xl bg-canvas-850 border border-canvas-600 hover:border-canvas-500 transition-colors flex flex-col justify-between"
          >
            <div className="flex items-center justify-between text-xs text-slateText-400 font-bold uppercase">
              <span>{f.field_name}</span>
              <span className="font-mono text-[11px] text-accent-emerald font-semibold">
                {f.confidence !== undefined ? formatScorePct(f.confidence) : "—"}
              </span>
            </div>
            <div className="mt-1 font-mono text-sm font-bold text-slateText-50 break-words">
              {f.extracted_value || "—"}
            </div>
            {f.engine && (
              <div className="mt-1.5 text-[10px] font-mono text-slateText-400">
                Engine: {f.engine}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
