import eslintConfigPrettier from "eslint-config-prettier/flat";
import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import { defineConfig, globalIgnores } from "eslint/config";

export default defineConfig([
  // `api.gen.ts` is generated from backend/openapi.json and rewritten wholesale
  // by `npm run generate:api`, so linting it reports on the generator's output
  // rather than on anything anyone can edit. `--fix` would also be undone on the
  // next run. Ignored here as well as in .prettierignore.
  globalIgnores(["dist", "src/lib/api.gen.ts"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      js.configs.recommended,
      tseslint.configs.strictTypeChecked,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
      eslintConfigPrettier,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: {
        project: [
          "./tsconfig.node.json",
          "./tsconfig.app.json",
          "./tsconfig.worker.json",
        ],
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
]);
