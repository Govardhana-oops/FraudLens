import type { ScreeningStatus, CheckResult } from "@/types";

export function formatDate(isoString?: string | null): string {
  if (!isoString) return "—";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleString("en-US", {
      month: "short",
      day: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch {
    return isoString;
  }
}

export function formatDateTime(isoString?: string | null): string {
  return formatDate(isoString);
}

export function truncateMiddle(str: string | null | undefined, maxLen = 16): string {
  if (!str) return "—";
  if (str.length <= maxLen) return str;
  const charsEachSide = Math.floor((maxLen - 3) / 2);
  return `${str.substring(0, charsEachSide)}...${str.substring(str.length - charsEachSide)}`;
}

export function formatScorePct(val: number | null | undefined): string {
  if (val === null || val === undefined) return "—";
  if (val <= 1.0) return `${Math.round(val * 100)}%`;
  return `${Math.round(val)}%`;
}

export function mapActionToStatus(action: string): ScreeningStatus {
  const norm = (action || "").toUpperCase();
  if (norm === "ADMIT" || norm === "CLEAR" || norm === "VALID" || norm === "PASS") return "VALID";
  if (norm.includes("EXPIRED")) return "EXPIRED";
  if (norm.includes("TAMPER")) return "TAMPERED";
  if (norm.includes("WATCHLIST")) return "WATCHLIST_HIT";
  if (norm.includes("REVIEW") || norm.includes("SECONDARY") || norm.includes("FLAG")) return "REVIEW_REQUIRED";
  if (norm.includes("REJECT") || norm.includes("INVALID") || norm.includes("FRAUD")) return "INVALID";
  return "UNKNOWN";
}

export function getStatusTheme(status: ScreeningStatus | CheckResult) {
  switch (status) {
    case "VALID":
    case "PASS":
      return {
        label: "VALID / PASS",
        text: "text-accent-emerald",
        bg: "bg-accent-emerald/15",
        border: "border-accent-emerald/50",
        glow: "shadow-[0_0_12px_rgba(16,185,129,0.3)]",
        iconClass: "text-accent-emerald",
      };
    case "REVIEW_REQUIRED":
      return {
        label: "REVIEW REQUIRED",
        text: "text-accent-amber",
        bg: "bg-accent-amber/15",
        border: "border-accent-amber/50",
        glow: "shadow-[0_0_12px_rgba(245,158,11,0.3)]",
        iconClass: "text-accent-amber",
      };
    case "EXPIRED":
      return {
        label: "EXPIRED",
        text: "text-accent-amber",
        bg: "bg-accent-amber/20",
        border: "border-accent-amber/60",
        glow: "shadow-[0_0_12px_rgba(245,158,11,0.3)]",
        iconClass: "text-accent-amber",
      };
    case "TAMPERED":
    case "FRAUD_DETECTED":
    case "WATCHLIST_HIT":
    case "INVALID":
    case "FAIL":
    case "PROCESSING_ERROR":
      return {
        label: status === "TAMPERED" ? "TAMPERED" : status === "WATCHLIST_HIT" ? "WATCHLIST HIT" : "INVALID / FAILED",
        text: "text-accent-rose",
        bg: "bg-accent-rose/15",
        border: "border-accent-rose/50",
        glow: "shadow-[0_0_12px_rgba(239,68,68,0.3)]",
        iconClass: "text-accent-rose",
      };
    case "UNKNOWN":
    default:
      return {
        label: "UNKNOWN",
        text: "text-slateText-200",
        bg: "bg-canvas-750",
        border: "border-canvas-500",
        glow: "shadow-none",
        iconClass: "text-slateText-300",
      };
  }
}
