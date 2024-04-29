/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./accounts/templates/**/*.html",
    "./clients/templates/**/*.html",
    "./coreadmin/templates/**/*.html",
    "./scorm/templates/**/*.html", 
    "./templates/**/*.html",
    "./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('flowbite/plugin'),
  ],
}

