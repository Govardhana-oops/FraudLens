import React from "react";
import { CheckCircle2, AlertTriangle, XCircle, Clock, HelpCircle, ShieldAlert } from "lucide-react";
import type { ScreeningStatus, CheckResult } from "@/types";
import { getStatusTheme } from "@/utils/formatters";
import clsx from "clsx";

interface StatusBadgeProps {
  status: ScreeningStatus | CheckResult;
  size?: "sm" | "md" | "lg";
}

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  const theme = getStatusTheme(status);

  const getIcon = () => {
    switch (status) {
      case "VALID":
      case "PASS":
        return <CheckCircle2 className={theme.iconClass} size={size === "lg" ? 20 : size === "sm" ? 14 : 16} />;
      case "REVIEW_REQUIRED":
        return <AlertTriangle className={theme.iconClass} size={size === "lg" ? 20 : size === "sm" ? 14 : 16} />;
      case "EXPIRED":
        return <Clock className={theme.iconClass} size={size === "lg" ? 20 : size === "sm" ? 14 : 16} />;
      case "TAMPERED":
      case "WATCHLIST_HIT":
        return <ShieldAlert className={theme.iconClass} size={size === "lg" ? 20 : size === "sm" ? 14 : 16} />;
      case "INVALID":
      case "FAIL":
      case "PROCESSING_ERROR":
        return <XCircle className={theme.iconClass} size={size === "lg" ? 20 : size === "sm" ? 14 : 16} />;
      default:
        return <HelpCircle className={theme.iconClass} size={size === "lg" ? 20 : size === "sm" ? 14 : 16} />;
    }
  };

  const sizeClasses = {
    sm: "px-2.5 py-0.5 text-[11px] gap-1.5 font-bold",
    md: "px-3.5 py-1 text-xs gap-2 font-bold",
    lg: "px-5 py-2 text-sm gap-2.5 font-extrabold tracking-wide",
  }[size];

  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-lg border font-mono uppercase tracking-wider transition-all duration-150",
        theme.bg,
        theme.border,
        theme.text,
        theme.glow,
        sizeClasses
      )}
    >
      {getIcon()}
      <span>{theme.label}</span>
    </span>
  );
}
