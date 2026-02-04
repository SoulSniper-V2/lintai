/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        claw: { 400: '#38bdf8', 500: '#0ea5e9', 600: '#0284c7' }
      }
    },
  },
  plugins: [],
}
