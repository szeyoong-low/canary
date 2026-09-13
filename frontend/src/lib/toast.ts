// Toasts are raised from React event handlers (onError) and TanStack Query's
// global cache callbacks in `queryClient.ts`, which run outside the component
// tree and so cannot call a hook. Base UI can create a manager at module scope
// to be shared by both cases.

import { Toast } from "@base-ui/react/toast";
import { useEffect } from "react";

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

// Created once for the lifetime of the bundle. `Toast.Provider` subscribes to
// it, so anything added before the tree mounts is still shown.
export const toastManager = Toast.createToastManager();

// Returns toast ID
export type ToastRaiser = (title: string, options?: ToastOptions) => string;

const raise =
  (type: ToastType): ToastRaiser =>
  (title, options = {}) =>
    toastManager.add({
      type,
      title,
      priority: priorityByType[type],
      ...options,
    });

/** Raises a toast from anywhere, React or not. */
export const toast: Record<ToastType, ToastRaiser> = {
  error: raise("error"),
  success: raise("success"),
  info: raise("info"),
};

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
