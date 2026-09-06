/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Projector-First Deep Obsidian & Cyan Security Theme
        canvas: {
          950: "#080D16", // Deepest background
          900: "#0E1624", // Primary app background
          850: "#131E30", // Secondary container surface
          800: "#1A283F", // Card / panel elevated surface
          750: "#22334E", // Active card / interactive hover
          700: "#2B3F5F", // Dividers and prominent borders
          600: "#3B557F", // High-visibility borders
          500: "#5072A8", // Highlighted focus borders
        },
        slateText: {
          50: "#FFFFFF",  // Pure white headers and critical metrics
          100: "#F0F5FC", // High-visibility subheadings
          200: "#D8E4F2", // Standard body and table content
          300: "#B8CCE2", // Secondary descriptions and metadata
          400: "#8FA8C6", // Helper tags and timestamp notes
          500: "#6B85A4", // Deepest auxiliary notes (passes WCAG AA)
        },
        accent: {
          teal: "#2DD4BF",
          tealGlow: "rgba(45, 212, 191, 0.25)",
          tealDark: "#0F766E",
          emerald: "#10B981",
          amber: "#F59E0B",
          rose: "#EF4444",
          sky: "#3B82F6",
        },
      },
      fontFamily: {
        sans: ["'IBM Plex Sans'", "system-ui", "-apple-system", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel3d: "0 1px 0 0 rgba(255, 255, 255, 0.12) inset, 0 10px 25px -5px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.05)",
        cardElevated: "0 1px 0 0 rgba(255, 255, 255, 0.1) inset, 0 4px 12px -2px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.04)",
        glowTeal: "0 0 15px 0 rgba(45, 212, 191, 0.3)",
      },
    },
  },
  plugins: [],
};
