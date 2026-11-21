/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#fffbf0',
          100: '#fef5d6',
          200: '#fde9ad',
          300: '#fcd97a',
          400: '#fac847',
          500: '#f5b01e',
          600: '#d99011',
          700: '#b06c0d',
          800: '#8d5311',
          900: '#754312',
        },
      },
    },
  },
  plugins: [],
}
