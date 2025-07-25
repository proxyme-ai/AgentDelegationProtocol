export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"] ,
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1d4ed8'
        }
      }
    }
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        light: {
          primary: '#1d4ed8'
        }
      }
    ]
  }
};
