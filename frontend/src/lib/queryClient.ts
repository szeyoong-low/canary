// The client cache for server state. Created outside React so the same
// instance is shared by the component tree and by any non-component code
// that needs to seed or invalidate it.

import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";
import { toast } from "@/lib/toast";

// Used when a query or mutation did not declare its own `errorTitle` in `meta`
// (see `queryMeta.ts` for how that field is typed).
const FALLBACK_ERROR_TITLE: string = "Something went wrong";

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
  // One handler for every query in the app, called after the last retry fails.
  queryCache: new QueryCache({
    onError: (error, query) => {
      // With no cached data there is nothing on screen to toast over, so the
      // component owns that state instead (an error boundary, or inline retry).
      // A toast would auto-dismiss and leave the user facing a blank page.
      if (query.state.data === undefined) {
        return;
      }

      // Keyed by the query so a failing refetch updates its own toast rather
      // than stacking a new one on every attempt.
      toast.error(query.meta?.errorTitle ?? FALLBACK_ERROR_TITLE, {
        id: query.queryHash,
        description: error.message,
      });
    },
  }),

  mutationCache: new MutationCache({
    onError: (error, _variables, _onMutateResult, mutation) => {
      const title: string = mutation.meta?.errorTitle ?? FALLBACK_ERROR_TITLE;

      // The title is the only stable identity a mutation has here, so repeated
      // failures of the same action collapse into one toast.
      toast.error(title, { id: title, description: error.message });
    },
  }),

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
