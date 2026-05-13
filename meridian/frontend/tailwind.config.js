/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
      theme: {
    extend: {
      colors: {
        'phase-1': '#3B82F6',
        'phase-2': '#8B5CF6',
        'phase-3': '#10B981',
        'dl-bg': '#f6f5f0',
        'dl-paper': '#fbfaf6',
        'dl-ink': '#0d1117',
        'dl-muted': '#4a5560',
        'dl-accent': '#ff5b1f',
        'dl-leaf': '#2f6b3d',
        'dl-plum': '#5b3a7a',
        'dl-sky': '#2563eb',
      },
      backgroundColor: {
        'app': '#f6f5f0',
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
