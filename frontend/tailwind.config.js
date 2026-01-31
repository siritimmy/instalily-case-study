/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "partselect-teal": "#2B6B6B",
        "partselect-gold": "#D4A843",
        "partselect-orange": "#FF6F3C",
        "partselect-dark": "#1A1A1A",
        "partselect-light": "#F5F5F5",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      animation: {
        "fade-in-up": "fadeInUp 0.3s ease-out",
        "pulse-dot": "pulseDot 1.4s ease-in-out infinite",
      },
      keyframes: {
        fadeInUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseDot: {
          "0%, 80%, 100%": { transform: "scale(0.6)", opacity: "0.5" },
          "40%": { transform: "scale(1)", opacity: "1" },
        },
      },
      boxShadow: {
        "chat-bubble": "0 1px 2px rgba(0, 0, 0, 0.1)",
        "input-focus": "0 0 0 3px rgba(43, 107, 107, 0.2)",
      },
    },
  },
  plugins: [],
};
