/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bento-bg': '#F4F1DE',      
        'bento-primary': '#E9C46A', 
        'bento-secondary': '#2A9D8F',
        'bento-accent': '#E76F51',  
      },
    },
  },
  plugins: [],
}