module.exports = {
  env: {
    browser: true,
    es2021: true,
    "jest": true,
    "node": true

  },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
  ],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: ["react", "react-hooks"],
  rules: {
    "react/react-in-jsx-scope": "off", // No requerido en React 17+
    "react/prop-types": "off",         // No usas PropTypes, asumo uso manual o TS
    "no-unused-vars": "warn",          // Avisos útiles sin bloquear builds
    "no-console": "warn",              // Evitar logs en producción
    "react/jsx-uses-react": "off",
    "react/jsx-uses-vars": "error",
  },
  settings: {
    react: {
      version: "detect", // Detectar automáticamente la versión de React
    },
  },
};
