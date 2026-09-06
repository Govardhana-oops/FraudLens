import React from "react";
import { Link } from "react-router-dom";
import { FolderOpen, ArrowRight } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: string | (() => void);
}

export function EmptyState({
  title = "No records available",
  description = "There are no records to display at this moment.",
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center space-y-4">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-canvas-850 border border-canvas-600 text-slateText-400">
        <FolderOpen size={32} />
      </div>
      <div className="max-w-md">
        <h3 className="text-base font-bold text-slateText-100">{title}</h3>
        <p className="text-xs font-medium text-slateText-300 mt-1">{description}</p>
      </div>

      {actionLabel && onAction && (
        <div className="pt-2">
          {typeof onAction === "string" ? (
            <Link
              to={onAction}
              className="btn-primary inline-flex items-center gap-2 text-xs uppercase tracking-wider shadow-glow-teal"
            >
              <span>{actionLabel}</span>
              <ArrowRight size={14} />
            </Link>
          ) : (
            <button
              onClick={onAction}
              className="btn-primary inline-flex items-center gap-2 text-xs uppercase tracking-wider shadow-glow-teal"
            >
              <span>{actionLabel}</span>
              <ArrowRight size={14} />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
