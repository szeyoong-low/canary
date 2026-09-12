// The client cache for server state. Created outside React so the same
// instance is shared by the component tree and by any non-component code
// that needs to seed or invalidate it.

import { QueryClient } from "@tanstack/react-query";

const MINUTE_MS: number = 60 * 1000;

// How long fetched data is trusted before a remount triggers a background refetch.
//
// For now, no collaboration is supported, so this staleness is fine as all
// server state updates come from a single browser instance.
const STALE_TIME: number = 5 * MINUTE_MS;

// How long data with no mounted consumer is kept before being dropped.
// Longer than STALE_TIME so returning to a report re-renders from memory
// rather than refetching charts that are expensive to ship.
const GARBAGE_COLLECTION_TIME: number = 30 * MINUTE_MS;

const MAXIMUM_RETRIES: number = 2;

// 4xx means the request itself was wrong (missing, forbidden, malformed), so
// repeating it verbatim can only fail the same way. 5xx and network faults are
// transient and worth another attempt.
const CLIENT_ERROR_RANGE: readonly [number, number] = [400, 499];

// Matched on the shape rather than on a class, so this module stays
// independent of whichever feature module threw (see `APIError` in reports.ts).
function hasStatus(error: unknown): error is { status: number } {
  return (
    typeof error === "object" &&
    error !== null &&
    "status" in error &&
    typeof error.status === "number"
  );
}

function isClientError(error: unknown): boolean {
  if (!hasStatus(error)) {
    return false;
  }

  const [lower, upper] = CLIENT_ERROR_RANGE;
  return error.status >= lower && error.status <= upper;
}

export const queryClient: QueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: STALE_TIME,
      gcTime: GARBAGE_COLLECTION_TIME,
      // Alt-tabbing back to the page should not re-download every chart.
      refetchOnWindowFocus: false,
      retry: (failureCount: number, error: unknown): boolean =>
        !isClientError(error) && failureCount < MAXIMUM_RETRIES,
    },
    mutations: {
      // Generating a chart is not idempotent: a silent retry would bill a
      // second agent run and could save two containers.
      retry: false,
    },
  },
});
