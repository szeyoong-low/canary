// Tells TanStack Query what `meta` holds on a query or mutation, so a typo at a
// call site is a compile error instead of silently typing as `unknown`.
//
// Three things this declaration is fussy about:
//   - it augments query-core, not TanStack Query: the latter only re-exports
//     `Register`, and merging into a re-export creates an unrelated interface
//   - the import below is required, because an augmentation merges into a
//     module only if the file also imports that module
//   - the shape is written inline rather than as a named local interface,
//     which stops the merge being seen by other files.

import type { QueryMeta } from "@tanstack/query-core";

declare module "@tanstack/query-core" {
  interface Register {
    // `errorTitle` is the headline shown when this query or mutation fails.
    // Set it per call site; `queryClient.ts` falls back to a generic message.
    queryMeta: { errorTitle?: string };
    mutationMeta: { errorTitle?: string };
  }
}

// Re-exported only so the import above counts as used under `noUnusedLocals`.
export type { QueryMeta };
