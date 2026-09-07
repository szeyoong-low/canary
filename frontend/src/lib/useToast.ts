import { Toast } from "@base-ui/react/toast";
import { useEffect, useMemo } from "react";

export type ToastType = "error" | "success" | "info";

export interface ToastOptions {
  id?: string; // ID per call site makes raising toasts idempotent (update-only)
  description?: string;
}

const priorityByType: Record<ToastType, "low" | "high"> = {
  error: "high",
  success: "low",
  info: "low",
};

export type ToastRaiser = (title: string, options?: ToastOptions) => string;

export type ToastFunctions = Record<ToastType, ToastRaiser>;

/**
 * Returns functions for raising a toast from an event handler.
 *
 * Use this for toasts caused by events. For a toast that mirrors error state
 * exposed on every render, use `useErrorToast` instead.
 */
export function useToast(): ToastFunctions {
  const { add } = Toast.useToastManager();

  return useMemo(() => {
    const raise =
      (type: ToastType): ToastRaiser =>
      (title, options = {}) =>
        add({ type, title, priority: priorityByType[type], ...options });

    return {
      error: raise("error"),
      success: raise("success"),
      info: raise("info"),
    };
  }, [add]);
  // "add" is included because the effect calls it and the
  // react-hooks/exhaustive-deps rule requires every value read from the
  // component scope to be listed. "add" is a return value.
}

export interface ErrorToastOptions {
  id: string;
  title: string;
}

/**
 * Raises an error toast whenever `error` becomes set.
 *
 * Errors surfaced by hooks are state exposed on every render rather than
 * events, so showing one is a side effect of it appearing.
 */
export function useErrorToast(
  error: Error | undefined,
  { id, title }: ErrorToastOptions,
) {
  const toast = useToast();

  useEffect(() => {
    if (!error) {
      return;
    }

    toast.error(title, { id, description: error.message });
  }, [error, toast, id, title]);
}
