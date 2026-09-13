import type { components } from "@/lib/api.gen";

// The names come from the backend's schema; only their ordering is restated
// below.
export type ReportRole = components["schemas"]["ReportRoleName"];

// Precedence lives in the database's `role_vocabulary` table and is not part of
// the OpenAPI schema, so the ladder has to be repeated here.
//
// A `Record` rather than an ordered list: adding a role to the backend enum
// stops this file compiling until the new role is given a rung, which is the
// closest thing to a compiler-enforced sync available.
//
// Must keep in sync with seed/__main__.py
const rolePrecedence: Record<ReportRole, number> = {
  viewer: 1,
  commenter: 2,
  editor: 3,
  owner: 4,
};

/**
 * Whether a caller holding `role` clears the bar `minimum` sets.
 *
 * `null` is a caller with no role at all, which only a private report produces.
 *
 * Presentation only. The backend runs the same check and is the one that counts.
 */
export function hasAtLeastRole(
  role: ReportRole | null,
  minimum: ReportRole,
): boolean {
  return role !== null && rolePrecedence[role] >= rolePrecedence[minimum];
}

export interface ClassNameProps {
  className?: string;
}

// Carries the HTTP status so callers can tell a permanent failure (403, 404)
// from a transient one. The cache's retry policy reads `status` off this.
export class APIError extends Error {
  readonly status: number;

  constructor(response: Response) {
    super(`Error ${String(response.status)}: ${response.statusText}`);
    this.name = "APIError";
    this.status = response.status;
  }
}
