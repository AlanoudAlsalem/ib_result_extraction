import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        teal: {
          DEFAULT: '#30CDD7',
          hover:   '#22B9C3',
          light:   '#E0F7FA',
        },
      },
    },
  },
  plugins: [],
};

export default config;
