module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2557a7',
          dark: '#1f4f96',
          soft: '#eef3fb'
        },
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617'
        },
        surface: '#ffffff',
        backdrop: '#f3f6fb',
      },
      boxShadow: {
        soft: '0 20px 40px rgba(24, 34, 51, 0.08)',
        glow: '0 20px 80px rgba(37, 87, 167, 0.08)'
      },
      borderRadius: {
        xl: '1rem',
        '2xl': '1.5rem'
      }
    }
  },
  variants: {
    extend: {
      opacity: ['disabled'],
      ringWidth: ['hover', 'focus'],
      ringColor: ['hover', 'focus']
    }
  },
  plugins: []
};
