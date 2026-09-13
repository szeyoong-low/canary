import { useEffect } from "react";
import { toast } from "@/lib/toast";

export interface ErrorToastOptions {
  id: string;
  title: string;
}

/**
 * Raises an error toast whenever `error` becomes set.
 *
 * Only for errors that are state exposed on every render rather than events,
 * so showing one is a side effect of it appearing. TanStack Query failures are
 * already toasted globally (see `queryClient.ts`) and must not use this.
 */
export function useErrorToast(
  error: Error | undefined,
  { id, title }: ErrorToastOptions,
) {
  useEffect(() => {
    if (!error) {
      return;
    }

    toast.error(title, { id, description: error.message });
  }, [error, id, title]);
}
