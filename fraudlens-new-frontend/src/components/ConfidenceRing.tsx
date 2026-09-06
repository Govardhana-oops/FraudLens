import React from "react";

interface ConfidenceRingProps {
  score: number; // 0 to 1
  size?: number;
  label?: string;
  color?: string;
}

export function ConfidenceRing({
  score,
  size = 72,
  label = "Score",
  color = "#2DD4BF",
}: ConfidenceRingProps) {
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const normalizedScore = Math.max(0, Math.min(1, score));
  const strokeDashoffset = circumference - normalizedScore * circumference;
  const percentText = `${Math.round(normalizedScore * 100)}%`;

  return (
    <div className="flex flex-col items-center">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1A283F"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <span className="absolute font-mono-nums text-xs font-bold text-slateText-50">{percentText}</span>
      </div>
      <span className="mt-1 text-[11px] font-bold uppercase tracking-wider text-slateText-300">{label}</span>
    </div>
  );
}
