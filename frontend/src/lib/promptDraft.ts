// Keeps a half-typed prompt alive across the full page navigation that signing
// in requires. `sessionStorage` is scoped to this tab and cleared when it
// closes, which matches how long a draft is worth keeping.

const DRAFT_KEY: string = "canary:prompt-draft";

function withStorage<T>(operation: (storage: Storage) => T, fallback: T): T {
  try {
    return operation(window.sessionStorage);
  } catch {
    // Browsers throw on any `sessionStorage` access when site data is blocked
    return fallback;
  }
}

export function readPromptDraft(): string {
  return withStorage((storage) => storage.getItem(DRAFT_KEY) ?? "", "");
}

export function writePromptDraft(draft: string): void {
  withStorage((storage) => {
    storage.setItem(DRAFT_KEY, draft);
  }, undefined);
}

export function clearPromptDraft(): void {
  withStorage((storage) => {
    storage.removeItem(DRAFT_KEY);
  }, undefined);
}
