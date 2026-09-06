import React from "react";
import type { LucideIcon } from "lucide-react";
import clsx from "clsx";

interface MetricTileProps {
  label: string;
  value: number | string | null;
  suffix?: string;
  icon: LucideIcon;
  variant?: "neutral" | "emerald" | "amber" | "rose" | "teal" | "sky";
  helperText?: string;
}

export function MetricTile({
  label,
  value,
  suffix = "",
  icon: Icon,
  variant = "neutral",
  helperText,
}: MetricTileProps) {
  const variantStyles = {
    neutral: {
      text: "text-slateText-50",
      icon: "text-slateText-300",
      border: "border-canvas-600 hover:border-canvas-500",
    },
    emerald: {
      text: "text-accent-emerald",
      icon: "text-accent-emerald",
      border: "border-accent-emerald/40 hover:border-accent-emerald/70",
    },
    amber: {
      text: "text-accent-amber",
      icon: "text-accent-amber",
      border: "border-accent-amber/40 hover:border-accent-amber/70",
    },
    rose: {
      text: "text-accent-rose",
      icon: "text-accent-rose",
      border: "border-accent-rose/40 hover:border-accent-rose/70",
    },
    teal: {
      text: "text-brand-teal",
      icon: "text-brand-teal",
      border: "border-brand-teal/40 hover:border-brand-teal/70",
    },
    sky: {
      text: "text-accent-sky",
      icon: "text-accent-sky",
      border: "border-accent-sky/40 hover:border-accent-sky/70",
    },
  }[variant];

  return (
    <div className={clsx("panel-3d p-5 transition-all duration-150", variantStyles.border)}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-slateText-300">{label}</span>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-canvas-850 border border-canvas-600">
          <Icon size={18} className={variantStyles.icon} strokeWidth={2.4} />
        </div>
      </div>
      <div className="mt-3 flex items-baseline gap-1">
        <span className={clsx("font-mono-nums text-3xl font-bold tracking-tight", variantStyles.text)}>
          {value === null || value === undefined ? "—" : value}
        </span>
        {suffix && <span className="text-sm font-semibold text-slateText-300">{suffix}</span>}
      </div>
      {helperText && <p className="mt-1.5 text-xs font-medium text-slateText-400">{helperText}</p>}
    </div>
  );
}
