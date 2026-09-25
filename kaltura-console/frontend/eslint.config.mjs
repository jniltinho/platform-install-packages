import js from "@eslint/js";
import ts from "typescript-eslint";
import vue from "eslint-plugin-vue";
export default [
  { ignores: ["node_modules/**", "../web/**"] },
  js.configs.recommended,
  ...ts.configs.recommended,
  ...vue.configs["flat/essential"],
  {
    files: ["src/**/*.vue"],
    languageOptions: {
      parserOptions: { parser: ts.parser, extraFileExtensions: [".vue"] },
    },
    rules: { "vue/multi-word-component-names": "off", "no-undef": "off" },
  },
  {
    files: ["scripts/*.mjs", "eslint.config.mjs"],
    languageOptions: { globals: { console: "readonly", process: "readonly" } },
  },
];
