/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Phase accent colors per Requirements 3.5, 3.6, 3.7
        'phase-1': '#3B82F6', // Blue for Phase 1
        'phase-2': '#8B5CF6', // Violet for Phase 2
        'phase-3': '#10B981', // Emerald for Phase 3
      },
      backgroundColor: {
        // Requirement 3.3: slate-950 background
        'app': '#020617',
      },
      backdropBlur: {
        'glass': '16px',
        'xl': '24px',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
