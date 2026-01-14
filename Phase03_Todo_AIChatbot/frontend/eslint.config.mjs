import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;

// import js from "@eslint/js";
// import globals from "globals";
// import reactHooks from "eslint-plugin-react-hooks";
// import reactRefresh from "eslint-plugin-react-refresh";
// import tseslint from "@typescript-eslint/eslint-plugin";
// import tsParser from "@typescript-eslint/parser";

// export default [
//   {
//     ignores: ["node_modules/**", "dist/**", ".next/**"],
//   },
//   js.configs.recommended,
//   {
//     files: ["**/*.{ts,tsx}"],
//     languageOptions: {
//       parser: tsParser,
//       parserOptions: {
//         projectService: true,
//         ecmaFeatures: { jsx: true },
//       },
//       globals: { ...globals.browser, ...globals.node },
//     },
//     plugins: {
//       "@typescript-eslint": tseslint,
//       "react-hooks": reactHooks,
//       "react-refresh": reactRefresh,
//     },
//     rules: {
//       ...tseslint.configs["recommended-type-checked"].rules,
//       ...reactHooks.configs.recommended.rules,
//       "react-refresh/only-export-components": [
//         "warn",
//         { allowConstantExport: true },
//       ],
//     },
//   },
// ];
